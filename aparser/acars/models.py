from django.contrib.auth.models import User
from django.db import models

class Cars(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Author")
    email = models.EmailField(max_length=255)
    search_link = models.URLField(null=True)
    status = models.BooleanField(default=True)
    car_image = models.TextField(null=True, default=0)
    car_link = models.TextField(null=True, default=0)
    car_name = models.TextField(null=True, default=0)
    car_price = models.TextField(null=True, default=0)
    car_specific_params = models.TextField(null=True, default=0)
    car_description = models.TextField(null=True, default=0)
    car_pushed = models.TextField(null=True, default=0)
    car_geo = models.TextField(null=True, default=0)
    car_date = models.TextField(null=True, default=0)

class News(models.Model):
    time_create = models.DateTimeField(auto_now_add=True)
    title = models.TextField(null=True)
    content = models.TextField(null=True)