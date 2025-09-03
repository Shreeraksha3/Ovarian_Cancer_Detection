import os
from django.shortcuts import render, redirect
from PIL import Image
import numpy as np
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm, ImageUploadForm
from .models import CustomUser
from django.http import JsonResponse
from .utils.send_mail import send_email

# Path to your model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'New_Test_model.keras')

# Define the mapping for model output
CLASS_MAPPING = {
    0: 'Clear_Cell',
    1: 'Endometri',
    2: 'Mucinous',
    3: 'Non_Cancerous',
    4: 'Serous'
}

# Global variable to cache the model
model = None

def load_prediction_model():
    """Load the model if not loaded already."""
    global model
    if model is None:
        from tensorflow.keras.models import load_model
        model = load_model(MODEL_PATH)
    return model

def preprocess_image(image, target_size):
    """Preprocess the image to match the input format of the model."""
    image = image.resize(target_size)
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

# ---------- Heuristic: looks like H&E histopathology? ----------
def is_histopathology_like(image_rgb: Image.Image) -> bool:
    """
    Lightweight heuristic to reject non-histopathology colored images:
    - Require min size
    - Reject grayscale disguised as RGB (all channels ~equal)
    - Require a reasonable amount of saturated pink/purple/blue hues (H&E-like)
    - Reject images strongly dominated by green (e.g., landscapes)
    """
    if image_rgb.mode != "RGB":
        return False

    w, h = image_rgb.size
    if w < 128 or h < 128:
        return False

    np_img = np.array(image_rgb)

    # Reject grayscale disguised as RGB (allow tiny tolerance for noise)
    if (np.allclose(np_img[:, :, 0], np_img[:, :, 1], atol=3) and
        np.allclose(np_img[:, :, 1], np_img[:, :, 2], atol=3)):
        return False

    # Convert to HSV (PIL: H,S,V in 0..255; H maps to 0..360 deg)
    hsv = np.array(image_rgb.convert('HSV'), dtype=np.uint8)
    H = hsv[:, :, 0].astype(np.float32) * (360.0 / 255.0)
    S = hsv[:, :, 1].astype(np.float32) / 255.0
    V = hsv[:, :, 2].astype(np.float32) / 255.0

    saturated = S > 0.25

    # Pink/Magenta/Eosin-ish: H ~ [300..360] or [0..20]
    pink_mask = ((H >= 300) | (H <= 20)) & saturated
    # Purple/Blue/Hematoxylin-ish: H ~ [210..290]
    purple_blue_mask = ((H >= 210) & (H <= 290)) & saturated

    tissue_like = pink_mask | purple_blue_mask
    tissue_ratio = np.count_nonzero(tissue_like) / tissue_like.size

    # Reject if the image is overly green (common in non-histo photos)
    mean_r, mean_g, mean_b = np.mean(np_img[:, :, 0]), np.mean(np_img[:, :, 1]), np.mean(np_img[:, :, 2])
    green_dominant = (mean_g > (mean_r + mean_b) * 0.75) and (mean_g > 110)

    if green_dominant:
        return False

    # Require at least 12% H&E-like pixels (tuneable)
    return tissue_ratio >= 0.12

# ------------------ REGISTER VIEW ------------------
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                base_username = user.email.split('@')[0]
                username = base_username
                counter = 1
                while CustomUser.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                user.username = username
                user.save()
                login(request, user)
                return redirect('home')
            except Exception:
                form.add_error(None, 'Registration failed. Please try again.')
    else:
        form = RegistrationForm()
    return render(request, 'imageapp/register.html', {'form': form})

# ------------------ LOGIN VIEW ------------------
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'imageapp/login.html', {'form': form})

# ------------------ HOME VIEW ------------------
@login_required
def home(request):
    return render(request, 'imageapp/home.html')

# ------------------ IMAGE UPLOAD ------------------
@login_required
def image_upload(request):
    context = {}
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            image_instance.user = request.user
            image_instance.save()

            patient_email = request.POST.get('patient_email')

            try:
                # Load model
                model = load_prediction_model()

                # Open image
                image_file = form.cleaned_data['image']
                image = Image.open(image_file)

                # Reject non-colored images early
                if image.mode not in ["RGB", "RGBA"]:
                    context['error_message'] = "Invalid image uploaded. Please upload a valid colored histopathology image."
                    context['form'] = form
                    return render(request, 'imageapp/upload.html', context)

                # Use RGB for analysis
                image_rgb = image.convert("RGB")

                # Reject images that don't look like H&E histopathology
                if not is_histopathology_like(image_rgb):
                    context['error_message'] = "Invalid image uploaded. Please upload a valid histopathology image (H&E-stained)."
                    context['form'] = form
                    return render(request, 'imageapp/upload.html', context)

                # Preprocess valid image
                processed_image = preprocess_image(image_rgb, target_size=(224, 224))

                # Make prediction
                predictions = model.predict(processed_image).flatten()
                highest_class_index = np.argmax(predictions)
                highest_class_name = CLASS_MAPPING[highest_class_index]
                highest_probability = predictions[highest_class_index]

                # Save prediction context
                context['predictions'] = {CLASS_MAPPING[i]: float(prob) for i, prob in enumerate(predictions)}
                context['highest_class'] = highest_class_name
                context['highest_probability'] = float(highest_probability)

                request.session['prediction_results'] = {
                    'predictions': context['predictions'],
                    'highest_class': highest_class_name,
                    'highest_probability': float(highest_probability),
                    'patient_email': patient_email
                }

            except Exception:
                # Friendly error for corrupted/unsupported files
                context['error_message'] = "Invalid image uploaded. Please upload a proper histopathology image."

    else:
        form = ImageUploadForm()

    context['form'] = form
    return render(request, 'imageapp/upload.html', context)

# ------------------ SEND EMAIL ------------------
@login_required
def send_prediction_email(request):
    if request.method == 'POST':
        prediction_results = request.session.get('prediction_results')
        if prediction_results:
            template_path = os.path.join('imageapp', 'templates', 'prediction_email.html')

            predictions_str = "\n".join([
                f"{class_name}: {prob:.2f}%"
                for class_name, prob in prediction_results['predictions'].items()
            ])

            context = {
                'name': "Patient",
                'highest_class': prediction_results['highest_class'],
                'highest_probability': f"{prediction_results['highest_probability']:.2f}",
                'predictions': predictions_str
            }

            try:
                send_email(
                    subject="AI Prediction Report - Ovarian Cancer Detection",
                    recipient_email=prediction_results['patient_email'],
                    template_path=template_path,
                    context=context
                )
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
