from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http.response import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from decimal import Decimal
import stripe
from .models import Item, Order, OrderItem, Tax, Discount

User = get_user_model()


def get_list_of_taxes():
    list_of_taxes = [stripe.TaxRate.create(
        display_name=item.display_name,
        inclusive=item.inclusive,
        percentage=item.percentage,
        country=item.country,
        state=item.state,
    ) for item in Tax.objects.all()]

    list_of_taxes = [item.id for item in list_of_taxes]
    return list_of_taxes


def get_list_of_discounts():
    discount = Discount.objects.all().first()
    return stripe.Coupon.create(
        name=discount.name,
        currency=discount.currency,
        percent_off=discount.percent_off,
        max_redemptions=discount.max_redemptions,
    )


class HomePageView(generic.ListView):
    model = Item
    template_name = 'orders/home.html'
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)

        try:
            cart = Order.get_cart(self.request.user)
            context.update({
                'cart': cart,
            })
        except Exception:
            pass

        return context


class ItemDetailView(generic.DetailView):
    model = Item
    context_object_name = 'item'
    template_name = 'orders/item_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        context.update({
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLISHABLE_KEY
        })
        return context


class CartView(LoginRequiredMixin, generic.View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        cart = Order.get_cart(request.user)
        order_items = cart.orderitem_set.all()
        context = {
            'cart': cart,
            'order_items': order_items,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLISHABLE_KEY
        }
        return render(request, 'orders/cart.html', context=context)

    def post(self, request, *args, **kwargs):
        cart = Order.get_cart(request.user)
        order_items = cart.orderitem_set.all()
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            if len(Tax.objects.all()):
                if len(Discount.objects.all()):
                    checkout_session = stripe.checkout.Session.create(
                        line_items=[
                            {
                                'price_data': {
                                    'currency': 'usd',
                                    'unit_amount': order_item.item.get_cents,
                                    'product_data': {
                                        'name': order_item.item.name,
                                        'description': order_item.item.description,
                                    },
                                },
                                'quantity': order_item.quantity,
                                'dynamic_tax_rates': get_list_of_taxes(),
                            } for order_item in order_items
                        ],
                        success_url=domain_url + 'success/',
                        cancel_url=domain_url + 'cancel/',
                        payment_method_types=['card', 'us_bank_account'],
                        mode='payment',
                        discounts=[{'coupon': get_list_of_discounts().id}],
                    )
                else:
                    checkout_session = stripe.checkout.Session.create(
                        line_items=[
                            {
                                'price_data': {
                                    'currency': 'usd',
                                    'unit_amount': order_item.item.get_cents,
                                    'product_data': {
                                        'name': order_item.item.name,
                                        'description': order_item.item.description,
                                    },
                                },
                                'quantity': order_item.quantity,
                                'dynamic_tax_rates': get_list_of_taxes(),
                            } for order_item in order_items
                        ],
                        success_url=domain_url + 'success/',
                        cancel_url=domain_url + 'cancel/',
                        payment_method_types=['card', 'us_bank_account'],
                        mode='payment',
                    )
            elif len(Discount.objects.all()):
                checkout_session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'usd',
                                'unit_amount': order_item.item.get_cents,
                                'product_data': {
                                    'name': order_item.item.name,
                                    'description': order_item.item.description,
                                },
                            },
                            'quantity': order_item.quantity,
                        } for order_item in order_items
                    ],
                    success_url=domain_url + 'success/',
                    cancel_url=domain_url + 'cancel/',
                    payment_method_types=['card', 'us_bank_account'],
                    mode='payment',
                    discounts=[{'coupon': get_list_of_discounts().id}],
                )
            else:
                checkout_session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'usd',
                                'unit_amount': order_item.item.get_cents,
                                'product_data': {
                                    'name': order_item.item.name,
                                    'description': order_item.item.description,
                                },
                            },
                            'quantity': order_item.quantity,
                        } for order_item in order_items
                    ],
                    success_url=domain_url + 'success/',
                    cancel_url=domain_url + 'cancel/',
                    payment_method_types=['card', 'us_bank_account'],
                    mode='payment',
                )
            return JsonResponse({
                'id': checkout_session.id
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})


class BuyOneItemView(generic.View):
    def post(self, request, *args, **kwargs):
        item_id = self.kwargs["pk"]
        item = Item.objects.get(id=item_id)
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            order = Order.get_cart(request.user)
            OrderItem.objects.create(order=order, item=item, quantity=1)
        except:
            pass

        try:
            if len(Tax.objects.all()):
                if len(Discount.objects.all()):
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
                                'dynamic_tax_rates': get_list_of_taxes(),
                            }
                        ],
                        success_url=domain_url + 'success/',
                        cancel_url=domain_url + 'cancel/',
                        payment_method_types=['card', 'us_bank_account'],
                        mode='payment',
                        discounts=[{'coupon': get_list_of_discounts().id}],
                    )
                else:
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
                                'dynamic_tax_rates': get_list_of_taxes(),
                            }
                        ],
                        success_url=domain_url + 'success/',
                        cancel_url=domain_url + 'cancel/',
                        payment_method_types=['card', 'us_bank_account'],
                        mode='payment',
                    )
            elif len(Discount.objects.all()):
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
                    success_url=domain_url + 'success/',
                    cancel_url=domain_url + 'cancel/',
                    payment_method_types=['card', 'us_bank_account'],
                    mode='payment',
                    discounts=[{'coupon': get_list_of_discounts().id}],
                )
            else:
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
                    success_url=domain_url + 'success/',
                    cancel_url=domain_url + 'cancel/',
                    payment_method_types=['card', 'us_bank_account'],
                    mode='payment',
                )
            return JsonResponse({
                'id': checkout_session.id
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        amount_tax = event['data']['object']['total_details']['amount_tax']
        amount_discount = event['data']['object']['total_details']['amount_discount']
        country = event['data']['object']['customer_details']['address']['country']
        state = event['data']['object']['customer_details']['address']['state']
        final_amount = event['data']['object']['amount_total']
        try:
            username = request.META['USERNAME']
            user = User.objects.get(username=username)
            cart = Order.get_cart(user)
        except Exception:
            cart = Order.objects.create()

        if amount_tax:
            taxes = Tax.objects.filter(country=country)
            for tax in taxes:
                if tax.state == state:
                    cart.tax = tax
                    break
                cart.tax = tax
            if cart.tax.inclusive is True:
                amount = final_amount + amount_discount
            else:
                amount = final_amount + amount_discount - amount_tax
        else:
            amount = final_amount + amount_discount

        if amount_discount:
            percent = 100 - (final_amount-amount_tax)/amount * 100
            discount = Discount.objects.filter(percent_off=percent).first()
            cart.discount = discount

        cart.amount = Decimal(amount / 100)
        cart.save()
        cart.make_order()
    return HttpResponse(status=200)


class AddOneItemToCart(LoginRequiredMixin, generic.View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def post(self, request, pk):
        cart = Order.get_cart(request.user)
        item = get_object_or_404(Item, pk=pk)
        try:
            order_item = cart.orderitem_set.get(item=item)
            order_item.quantity += 1
            order_item.save()
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        except Exception:
            cart.orderitem_set.create(order=cart,
                                      item=item,
                                      quantity=1)
            return redirect('cart')


class RemoveOneItemFromCart(LoginRequiredMixin, generic.View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def post(self, request, pk):
        cart = Order.get_cart(request.user)
        item = get_object_or_404(Item, pk=pk)
        try:
            order_item = cart.orderitem_set.get(item=item)
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            elif order_item.quantity == 1:
                order_item.delete()
            else:
                raise ValidationError('This item cannot be removed')
        finally:
            return redirect('cart')


class RemoveItemFromCart(LoginRequiredMixin, generic.View):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def post(self, request, pk):
        cart = Order.get_cart(request.user)
        item = get_object_or_404(Item, pk=pk)
        try:
            order_item = cart.orderitem_set.get(item=item)
            order_item.delete()
        finally:
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
