# Image Prediction App

## Overview
This project is an image prediction application that uses a machine learning model to classify images. It is built with Django and uses MongoDB as the database backend.

## System Requirements
- **Python**: Version 3.8 or higher
- **MongoDB**: Version 4.4 or higher
- **Operating System**: Windows/Linux/MacOS
- **RAM**: Minimum 8GB (recommended due to ML model)
- **Storage**: At least 2GB free space
- **GPU**: Optional but recommended for faster predictions

## Step 1: Environment Setup
```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment
# For Windows:
venv\Scripts\activate
# For Linux/Mac:
source venv/bin/activate
```

## Step 2: Install Dependencies
```bash
pip install django
pip install djongo
pip install pillow
pip install numpy
pip install pymongo
pip install tensorflow

```

## Step 3: Project Structure
Create the following directory structure:
```
myproject/
├── manage.py
├── media/
│   └── images/
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── imageapp/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── tests.py
    ├── urls.py
    ├── views.py
    ├── utils/
    │   └── send_mail.py
    ├── static/
    │   └── css/
    │       └── style.css
    └── templates/
        ├── base.html
        └── imageapp/
            ├── home.html
            ├── login.html
            ├── register.html
            ├── upload.html
            └── prediction_email.html
```

## Step 4: MongoDB Setup

### Install MongoDB

#### On Windows:
1. **Download MongoDB**: Go to the [MongoDB Download Center](https://www.mongodb.com/try/download/community) and download the Community Server version for Windows.
2. **Install MongoDB**: Run the installer and follow the setup wizard. Ensure you select "Complete" setup type and check "Install MongoDB as a Service".
3. **Configure MongoDB**: During installation, you can choose to install MongoDB Compass, a GUI for MongoDB, which is optional but helpful.

#### On macOS:
1. **Install Homebrew**: If you haven't already, install Homebrew by running:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **Install MongoDB**: Use Homebrew to install MongoDB:
   ```bash
   brew tap mongodb/brew
   brew install mongodb-community@4.4
   ```
3. **Start MongoDB**: Start the MongoDB service:
   ```bash
   brew services start mongodb/brew/mongodb-community
   ```

#### On Linux:
1. **Import the MongoDB public GPG Key**:
   ```bash
   wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
   ```
2. **Create a list file for MongoDB**:
   ```bash
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
   ```
3. **Reload local package database**:
   ```bash
   sudo apt-get update
   ```
4. **Install MongoDB packages**:
   ```bash
   sudo apt-get install -y mongodb-org
   ```
5. **Start MongoDB**:
   ```bash
   sudo systemctl start mongod
   ```

### Verify MongoDB Installation
- **Check MongoDB Service**: Ensure MongoDB is running by checking the service status:
  ```bash
  # On Windows, use the Services app to check MongoDB status
  # On macOS/Linux:
  sudo systemctl status mongod
  ```

- **Access MongoDB Shell**: Open a terminal and type `mongo` to access the MongoDB shell.

### Set Up MongoDB Database
1. **Create a Database**: In the MongoDB shell, create a new database:
   ```javascript
   use ovaries_cancer
   ```
2. **Create a User (Optional)**: For added security, create a user with specific roles:
   ```javascript
   db.createUser({
     user: "yourUsername",
     pwd: "yourPassword",
     roles: [{ role: "readWrite", db: "ovaries_cancer" }]
   })
   ```

### Connect Django Application to MongoDB
1. **Install Djongo**: Djongo is a connector that allows Django to use MongoDB as a backend:
   ```bash
   pip install djongo
   ```

2. **Configure Django Settings**: Update your `settings.py` to connect to MongoDB:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'djongo',
           'NAME': 'ovaries_cancer',
           'CLIENT': {
               'host': 'mongodb://localhost:27017/',  # Update with your MongoDB connection string
               # 'username': 'yourUsername',  # Uncomment if using authentication
               # 'password': 'yourPassword',  # Uncomment if using authentication
           }
       }
   }
   ```

3. **Run Migrations**: Apply migrations to set up the database schema:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

## Step 5: ML Model Setup
1. Place your trained model file (`New_Test_model.keras`) in the imageapp directory.
2. Ensure the model is compatible with TensorFlow 2.x.

## Step 6: Django Setup and Run
```bash
# Make migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

## Step 7: Testing
1. Open browser and go to `http://127.0.0.1:8000`
2. Register a new user
3. Login with credentials
4. Upload an image for prediction
5. Test email functionality

## Troubleshooting
- **Connection Issues**: Ensure MongoDB service is running and the connection string is correct.
- **Authentication Errors**: Verify username and password if authentication is enabled.
- **Firewall/Network**: Ensure no firewall is blocking MongoDB's default port (27017).

## Security Considerations
- Change the Django SECRET_KEY in production.
- Set DEBUG = False in production.
- Update ALLOWED_HOSTS for production.
- Secure the MongoDB instance.
- Use environment variables for sensitive data.


# Authentication

The authentication system in this Django project is implemented using Django's built-in authentication framework, with a custom user model. Here's a detailed explanation of how authentication is set up and managed:

### Custom User Model

1. **CustomUser Model**: 
   - The project uses a custom user model `CustomUser` that extends Django's `AbstractUser`.
   - This model includes additional fields like `email` and `name`, and sets `email` as the unique identifier for authentication.

   ```python
   # models.py
   from django.contrib.auth.models import AbstractUser
   from django.db import models

   class CustomUser(AbstractUser):
       email = models.EmailField(unique=True)
       name = models.CharField(max_length=255)
       
       USERNAME_FIELD = 'email'
       REQUIRED_FIELDS = ['username', 'name']

       def __str__(self):
           return self.email
   ```

2. **Settings Configuration**:
   - The `AUTH_USER_MODEL` setting in `settings.py` is updated to use the custom user model.

   ```python
   # settings.py
   AUTH_USER_MODEL = 'imageapp.CustomUser'
   ```

### User Registration

1. **RegistrationForm**:
   - A custom registration form `RegistrationForm` is created using Django's `UserCreationForm`.
   - It includes fields for `email`, `name`, `password1`, and `password2`.

   ```python
   # forms.py
   from django import forms
   from django.contrib.auth.forms import UserCreationForm
   from .models import CustomUser

   class RegistrationForm(UserCreationForm):
       email = forms.EmailField(required=True)
       name = forms.CharField(required=True)

       class Meta:
           model = CustomUser
           fields = ('email', 'name', 'password1', 'password2')
   ```

2. **Registration View**:
   - The `register` view handles user registration. It processes the form data, creates a new user, and logs them in upon successful registration.

   ```python
   # views.py
   def register(request):
       if request.method == 'POST':
           form = RegistrationForm(request.POST)
           if form.is_valid():
               user = form.save()
               login(request, user)
               return redirect('home')
       else:
           form = RegistrationForm()
       return render(request, 'imageapp/register.html', {'form': form})
   ```

### User Login

1. **LoginForm**:
   - A simple login form `LoginForm` is created with fields for `email` and `password`.

   ```python
   # forms.py
   class LoginForm(forms.Form):
       email = forms.EmailField()
       password = forms.CharField(widget=forms.PasswordInput)
   ```

2. **Login View**:
   - The `user_login` view handles user authentication. It uses Django's `authenticate` function to verify credentials and logs the user in if they are valid.

   ```python
   # views.py
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
   ```

### User Logout

- **Logout**:
  - The project uses Django's built-in `LogoutView` to handle user logout. It is configured in `urls.py`.

  ```python
  # urls.py
  from django.contrib.auth.views import LogoutView

  urlpatterns = [
      # ... other paths ...
      path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
  ]
  ```

### Access Control

- **Login Required**:
  - The `@login_required` decorator is used on views that require user authentication, ensuring that only logged-in users can access certain pages.

  ```python
  # views.py
  from django.contrib.auth.decorators import login_required

  @login_required
  def home(request):
      return render(request, 'imageapp/home.html')
  ```


# Image upload and prediction

Here's a detailed explanation of how the image upload process works, how the image is fed into the machine learning model, and how the prediction results are obtained:

### Image Upload Process

1. **ImageUploadForm**:
   - The `ImageUploadForm` is a Django form that handles the image upload. It is based on the `UploadedImage` model, which stores the image file and associates it with a user.

   ```python
   # forms.py
   from django import forms
   from .models import UploadedImage

   class ImageUploadForm(forms.ModelForm):
       class Meta:
           model = UploadedImage
           fields = ['image']
   ```

2. **UploadedImage Model**:
   - This model stores the uploaded image and the timestamp of when it was uploaded. It also links the image to the user who uploaded it.

   ```python
   # models.py
   from django.db import models
   from .models import CustomUser

   class UploadedImage(models.Model):
       image = models.ImageField(upload_to='images/')
       uploaded_at = models.DateTimeField(auto_now_add=True)
       user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
   ```

3. **Image Upload View**:
   - The `image_upload` view handles the image upload process. It processes the form data, saves the image, and prepares it for prediction.

   ```python
   # views.py
   from PIL import Image

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
       else:
           form = ImageUploadForm()

       context['form'] = form
       return render(request, 'imageapp/upload.html', context)
   ```

### Image Preprocessing and Model Prediction

1. **Preprocessing Function**:
   - The `preprocess_image` function resizes the image to the required input size for the model, normalizes the pixel values, and adds a batch dimension.

   ```python
   # views.py
   import numpy as np

   def preprocess_image(image, target_size):
       """Preprocess the image to match the input format of the model."""
       image = image.resize(target_size)
       image = np.array(image) / 255.0  # Normalize to [0, 1]
       image = np.expand_dims(image, axis=0)  # Add batch dimension
       return image
   ```

2. **Model Prediction**:
   - The preprocessed image is fed into the machine learning model to obtain predictions. The model outputs a probability distribution over the defined classes.

   ```python
   # views.py
   predictions = model.predict(processed_image).flatten()
   ```

3. **Result Interpretation**:
   - The class with the highest probability is identified as the predicted class. The probabilities for all classes are also stored for display.

   ```python
   # views.py
   highest_class_index = np.argmax(predictions)
   highest_class_name = CLASS_MAPPING[highest_class_index]
   highest_probability = predictions[highest_class_index]

   context['predictions'] = {CLASS_MAPPING[i]: float(prob) for i, prob in enumerate(predictions)}
   context['highest_class'] = highest_class_name
   context['highest_probability'] = float(highest_probability)
   ```

### Displaying Results

- **Template Rendering**:
  - The prediction results are passed to the template context and displayed on the upload page. The user can see the predicted class and the probabilities for each class.

  ```html
  <!-- upload.html -->
  {% if predictions %}
      <div class="results">
          <h2>Prediction Results:</h2>
          <ul>
              {% for class_name, probability in predictions.items %}
                  <li>{{ class_name }}: {{ probability|floatformat:2 }}%</li>
              {% endfor %}
          </ul>
          <div>
              <h3>Highest Probability:</h3>
              <p>Class: <strong>{{ highest_class }}</strong></p>
              <p>Probability: <strong>{{ highest_probability|floatformat:2 }}%</strong></p>
          </div>
      </div>
  {% endif %}
  ```
