from django.shortcuts import render, redirect
from django.views import generic
from django.conf import settings
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
from .models import Item


class HomePageView(generic.ListView):
    model = Item
    template_name = 'orders/home.html'
    context_object_name = 'items'


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': 50000,
                            'product_data': {
                                'name': 'Display 4k',
                                'description': '4K UHD IPS LED Monitor (27'' Diagonal)',
                                'images': ['https://www.lg.com/us/images/monitors/md05231065/gallery/DG01.jpg'],
                            },
                        },
                        'quantity': 1,
                    }
                ],
                success_url=domain_url+'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url+'cancel/',
                payment_method_types=['card'],
                mode='payment',
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})