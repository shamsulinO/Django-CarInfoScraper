from django.urls import path

from .views import *

urlpatterns = [
    path('', AllCars.as_view(), name='home'),
    path('avitocar/<int:car_id>', AvitoCar.as_view(), name='avitocar'),
    path('vin/<str:vin_num>/', VinCar.as_view(), name='vincar'),
    path('settings/', Settings.as_view(), name='settings'),
    path('check/', Check.as_view(), name='check'),
    path('logout/', logout_user, name='logout'),
    path('login/', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='register'),
]