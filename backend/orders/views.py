from django.shortcuts import render, redirect
from django.views import generic
from django.conf import settings
from django.http.response import JsonResponse, HttpResponseBadRequest
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


class CreateCheckoutSessionView(generic.View):
    def post(self, request, *args, **kwargs):

        item_id = self.kwargs["pk"]
        item = Item.objects.get(id=item_id)
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': item.get_cents,
                            'product_data': {
                                'name': item.name,
                                'description': item.description,
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
            return JsonResponse({
                'id': checkout_session.id
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})


class ItemDetailView(generic.DetailView):
    model = Item
    context_object_name = 'item'
    template_name = 'orders/item_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        context.update({
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLISHABLE_KEY
        })
        return context