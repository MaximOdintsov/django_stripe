from django import template
from ..models import Order, OrderItem
register = template.Library()


@register.simple_tag
def check_if_the_item_is_in_the_cart(item, user):
    try:
        cart = Order.get_cart(user)
        if OrderItem.objects.get(order=cart, item=item):
            return True
        return False
    except Exception:
        return False

