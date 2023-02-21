from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('item/<int:pk>', views.ItemDetailView.as_view(), name='item'),
    path('success/', TemplateView.as_view(template_name='orders/success.html'), name='success'),
    path('cancel/', TemplateView.as_view(template_name='orders/cancel.html'), name='cancel'),
    path('', views.HomePageView.as_view(), name='home'),

    path('add-one-item-to-cart/<int:pk>', views.AddOneItemToCart.as_view(), name='add_one_item_to_cart'),
    path('remove-one-item-from-cart/<int:pk>', views.RemoveOneItemFromCart.as_view(), name='remove_one_item_from_cart'),
    path('remove-item-from-cart/<int:pk>', views.RemoveItemFromCart.as_view(), name='remove_item_from_cart'),

    path('buy/<int:pk>/', views.BuyOneItemView.as_view(), name='buy_item'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),

]