from djongo import models   # important: use djongo.models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    _id = models.ObjectIdField(primary_key=True)  # MongoDB ObjectId as PK
    email = models.EmailField(unique=True, blank=False, null=False)
    name = models.CharField(max_length=255)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    def __str__(self):
        return self.email


class UploadedImage(models.Model):
    _id = models.ObjectIdField(primary_key=True)  # MongoDB ObjectId as PK
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
