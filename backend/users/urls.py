from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('registration/', views.MyRegistrationView.as_view(), name='registration'),
    path('', include('django.contrib.auth.urls')),
]