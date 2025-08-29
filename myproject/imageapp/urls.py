from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('upload/', views.image_upload, name='upload'),
    path('send-prediction-email/', views.send_prediction_email, name='send_prediction_email'),
]
