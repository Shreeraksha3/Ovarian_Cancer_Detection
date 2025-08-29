# Image Prediction App

## 📌 Overview

This project is an **image prediction web application** built with **Django** and **MongoDB**. It allows users to register, log in, upload images, and receive predictions from a trained machine learning model.

---

## ⚙️ System Requirements

* **Python**: 3.8 or higher
* **MongoDB**: 4.4 or higher
* **OS**: Windows/Linux/MacOS
* **RAM**: Minimum 8GB (recommended for ML tasks)
* **Storage**: At least 2GB free
* **GPU**: Optional but recommended for faster predictions

---

## 🚀 Setup Instructions

### Step 1: Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install django djongo pillow numpy pymongo tensorflow
```

### Step 3: Project Structure

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

### Step 4: MongoDB Setup

Follow official MongoDB installation instructions for your OS. Once installed:

```bash
# Start MongoDB service (Linux/Mac)
sudo systemctl start mongod
```

Create database:

```js
use ovaries_cancer
```

(Optional) Create user:

```js
db.createUser({
  user: "yourUsername",
  pwd: "yourPassword",
  roles: [{ role: "readWrite", db: "ovaries_cancer" }]
})
```

Update **settings.py**:

```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'ovaries_cancer',
        'CLIENT': {
            'host': 'mongodb://localhost:27017/',
            # 'username': 'yourUsername',
            # 'password': 'yourPassword',
        }
    }
}
```

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: ML Model Setup

* Place your trained model file (`New_Test_model.keras`) in `imageapp/`
* Ensure compatibility with **TensorFlow 2.x**

### Step 6: Run Django App

```bash
python manage.py createsuperuser   # Create admin user
python manage.py runserver
```

Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🔑 Authentication

* Custom user model (`CustomUser`) using **email** as the unique identifier
* Registration, login, and logout handled via Django auth
* Access control with `@login_required`

---

## 🖼️ Image Upload & Prediction

1. Users upload an image via a form
2. Image is preprocessed (`224x224`, normalized, batch dimension added)
3. Model predicts probabilities for each class
4. Results displayed with highest probability class highlighted

Example (template snippet):

```html
{% if predictions %}
  <h2>Prediction Results:</h2>
  <ul>
    {% for class_name, probability in predictions.items %}
      <li>{{ class_name }}: {{ probability|floatformat:2 }}%</li>
    {% endfor %}
  </ul>
  <p>Most likely: <strong>{{ highest_class }}</strong> ({{ highest_probability|floatformat:2 }}%)</p>
{% endif %}
```

---

## 🛠️ Troubleshooting

* Ensure MongoDB service is running
* Check connection string in `settings.py`
* Open firewall for port `27017` if using remote DB
* Use environment variables for sensitive credentials

---

## 🔒 Security Recommendations

* Change `SECRET_KEY` in production
* Set `DEBUG = False`
* Configure `ALLOWED_HOSTS`
* Secure MongoDB with authentication & firewall

---

## 📧 Email Notifications

* Email alerts can be sent using `send_mail.py`
* Configure SMTP settings in `settings.py`

---

## ✅ Features

* User registration & login (custom auth)
* Image upload & storage
* ML model prediction
* Email notifications
* MongoDB backend
* Clean UI with templates & CSS
