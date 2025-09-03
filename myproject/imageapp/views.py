# import os
# from django.shortcuts import render, redirect
# from PIL import Image
# import numpy as np
# from django.contrib.auth import login, authenticate
# from django.contrib.auth.decorators import login_required
# from .forms import RegistrationForm, LoginForm, ImageUploadForm
# from .models import CustomUser
# from django.http import JsonResponse
# from .utils.send_mail import send_email

# # Path to your model
# MODEL_PATH = os.path.join(os.path.dirname(__file__), 'New_Test_model.keras')

# # Define the mapping for model output
# CLASS_MAPPING = {
#     0: 'Clear_Cell',
#     1: 'Endometri',
#     2: 'Mucinous',
#     3: 'Non_Cancerous',
#     4: 'Serous'
# }

# # Global variable to cache the model
# model = None

# def load_prediction_model():
#     """Load the model if not loaded already."""
#     global model
#     if model is None:
#         from tensorflow.keras.models import load_model
#         model = load_model(MODEL_PATH)
#     return model

# def preprocess_image(image, target_size):
#     """Preprocess the image to match the input format of the model."""
#     image = image.resize(target_size)
#     image = np.array(image) / 255.0  # Normalize to [0, 1]
#     image = np.expand_dims(image, axis=0)  # Add batch dimension
#     return image

# def register(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             try:
#                 user = form.save(commit=False)
#                 # Generate a unique username based on email
#                 base_username = user.email.split('@')[0]
#                 username = base_username
#                 counter = 1
                
#                 while CustomUser.objects.filter(username=username).exists():
#                     username = f"{base_username}{counter}"
#                     counter += 1
                
#                 user.username = username
#                 user.save()
                
#                 login(request, user)
#                 return redirect('home')
#             except Exception as e:
#                 print(f'Error registering user: {str(e)}')
#                 form.add_error(None, 'Registration failed. Please try again.')
#     else:
#         form = RegistrationForm()
#     return render(request, 'imageapp/register.html', {'form': form})

# def user_login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=email, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('home')
#     else:
#         form = LoginForm()
#     return render(request, 'imageapp/login.html', {'form': form})

# @login_required
# def home(request):
#     return render(request, 'imageapp/home.html')

# @login_required
# def image_upload(request):
#     context = {}
#     if request.method == 'POST':
#         form = ImageUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             # Save the image with the user
#             image_instance = form.save(commit=False)
#             image_instance.user = request.user
#             image_instance.save()

#             # Load the model lazily
#             model = load_prediction_model()

#             # Handle the uploaded image
#             image_file = form.cleaned_data['image']
#             image = Image.open(image_file)

#             # Preprocess and predict
#             processed_image = preprocess_image(image, target_size=(224, 224))
#             predictions = model.predict(processed_image).flatten()

#             highest_class_index = np.argmax(predictions)
#             highest_class_name = CLASS_MAPPING[highest_class_index]
#             highest_probability = predictions[highest_class_index]

#             context['predictions'] = {CLASS_MAPPING[i]: float(prob) for i, prob in enumerate(predictions)}
#             context['highest_class'] = highest_class_name
#             context['highest_probability'] = float(highest_probability)

#             # Store prediction results in session for email sending
#             request.session['prediction_results'] = {
#                 'predictions': {k: float(v) for k, v in context['predictions'].items()},
#                 'highest_class': highest_class_name,
#                 'highest_probability': float(highest_probability)
#             }
#     else:
#         form = ImageUploadForm()

#     context['form'] = form
#     return render(request, 'imageapp/upload.html', context)

# @login_required
# def send_prediction_email(request):
#     if request.method == 'POST':
#         prediction_results = request.session.get('prediction_results')
#         if prediction_results:
#             template_path = os.path.join('imageapp', 'templates', 'prediction_email.html')
            
#             # Convert predictions dictionary to a formatted string
#             predictions_str = "\n".join([f"{class_name}: {prob:.2f}" 
#                                        for class_name, prob in prediction_results['predictions'].items()])
            
#             context = {
#                 'name': request.user.name,
#                 'highest_class': prediction_results['highest_class'],
#                 'highest_probability': f"{prediction_results['highest_probability']:.2f}",
#                 'predictions': predictions_str
#             }
            
#             try:
#                 send_email(
#                     subject="Your Image Prediction Results",
#                     recipient_email=request.user.email,
#                     template_path=template_path,
#                     context=context
#                 )
#                 return JsonResponse({'status': 'success'})
#             except Exception as e:
#                 return JsonResponse({'status': 'error', 'message': str(e)})
    
#     return JsonResponse({'status': 'error', 'message': 'Invalid request'})
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
    image = np.array(image) / 255.0  # Normalize to [0, 1]
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                # Generate a unique username based on email
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
            except Exception as e:
                print(f'Error registering user: {str(e)}')
                form.add_error(None, 'Registration failed. Please try again.')
    else:
        form = RegistrationForm()
    return render(request, 'imageapp/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'imageapp/login.html', {'form': form})

@login_required
def home(request):
    return render(request, 'imageapp/home.html')

@login_required
def image_upload(request):
    context = {}
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the image with the user
            image_instance = form.save(commit=False)
            image_instance.user = request.user
            image_instance.save()

            # Load the model lazily
            model = load_prediction_model()

            # Handle the uploaded image
            image_file = form.cleaned_data['image']
            image = Image.open(image_file)

            # Preprocess and predict
            processed_image = preprocess_image(image, target_size=(224, 224))
            predictions = model.predict(processed_image).flatten()

            highest_class_index = np.argmax(predictions)
            highest_class_name = CLASS_MAPPING[highest_class_index]
            highest_probability = predictions[highest_class_index]

            context['predictions'] = {CLASS_MAPPING[i]: float(prob) for i, prob in enumerate(predictions)}
            context['highest_class'] = highest_class_name
            context['highest_probability'] = float(highest_probability)

            # Store prediction results in session for email sending
            request.session['prediction_results'] = {
                'predictions': {k: float(v) for k, v in context['predictions'].items()},
                'highest_class': highest_class_name,
                'highest_probability': float(highest_probability)
            }
    else:
        form = ImageUploadForm()

    context['form'] = form
    return render(request, 'imageapp/upload.html', context)

# @login_required
# def send_prediction_email(request):
#     if request.method == 'POST':
#         prediction_results = request.session.get('prediction_results')
#         if prediction_results:
#             template_path = os.path.join('imageapp', 'templates', 'prediction_email.html')
            
#             # Convert predictions dictionary to a formatted string
#             predictions_str = "\n".join([f"{class_name}: {prob:.2f}" 
#                                        for class_name, prob in prediction_results['predictions'].items()])
            
#             context = {
#                 'name': request.user.name,
#                 'highest_class': prediction_results['highest_class'],
#                 'highest_probability': f"{prediction_results['highest_probability']:.2f}",
#                 'predictions': predictions_str
#             }
            
#             try:
#                 send_email(
#                     subject="Your Image Prediction Results",
#                     recipient_email=request.user.email,
#                     template_path=template_path,
#                     context=context
#                 )
#                 return JsonResponse({'status': 'success'})
#             except Exception as e:
#                 return JsonResponse({'status': 'error', 'message': str(e)})
    
#     return JsonResponse({'status': 'error', 'message': 'Invalid request'})
@login_required
def send_prediction_email(request):
    if request.method == 'POST':
        prediction_results = request.session.get('prediction_results')
        if prediction_results:
            template_path = os.path.join('imageapp', 'utils', 'predict_email.html')

            # Convert predictions dictionary to a formatted string
            predictions_str = "\n".join([f"{class_name}: {prob:.2f}" 
                                         for class_name, prob in prediction_results['predictions'].items()])

            context = {
                'name': request.user.name,  # patient name
                'highest_class': prediction_results['highest_class'],
                'highest_probability': f"{prediction_results['highest_probability']:.2f}",
                'predictions': predictions_str
            }

            try:
                # Send email dynamically to the patient
                send_email(
                    subject="Your Image Prediction Results",
                    recipient_email=request.user.email,  #  dynamic
                    template_path=template_path,
                    context=context
                )
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
