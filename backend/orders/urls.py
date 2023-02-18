from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('item/<int:pk>', views.ItemDetailView.as_view(), name='item'),
    path('success/', TemplateView.as_view(template_name='orders/success.html'), name='success'),
    path('cancel/', TemplateView.as_view(template_name='orders/cancel.html'), name='cancel'),
    path('', views.HomePageView.as_view(), name='home'),

    path('config/', views.stripe_config),
    path('create-checkout-session/<int:pk>/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session')

]