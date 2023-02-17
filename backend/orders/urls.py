from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('success/', TemplateView.as_view(template_name='orders/success.html'), name='success'),
    path('cancel/', TemplateView.as_view(template_name='orders/cancel.html'), name='cancel'),
    path('', views.HomePageView.as_view(), name='home'),
    # path('/buy/{id}', views.BuyView.as_view(), name='buy'),
    # path('/item/{id}', views.ItemView.as_view(), name='item'),

    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session),

]