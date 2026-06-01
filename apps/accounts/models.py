from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    email = models.EmailField(unique=True)

    phone_number = models.CharField(max_length=15)

    is_verified = models.BooleanField(default=False)

    is_blocked = models.BooleanField(default=False)

    referral_code = models.CharField(max_length=20, blank=True)

    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username']
