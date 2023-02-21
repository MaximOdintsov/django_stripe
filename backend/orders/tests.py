from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from decimal import Decimal
from .models import Item, Order, OrderItem, Discount, Tax

User = get_user_model()


class TestDataBase(TestCase):
    fixtures = [
        "orders/fixtures/db.json"
    ]

    def setUp(self):
        self.user = User.objects.get(username='maxim')
        self.item_1 = Item.objects.get(id=1)
        self.item_2 = Item.objects.get(id=2)
        self.discount = Discount.objects.create(name='discount',
                                                currency='usd',
                                                percent_off=10)
        self.tax_inclusive_true = Tax.objects.create(display_name='tax_true', 
                                                     inclusive=True,
                                                     percentage=50,
                                                     country='PL')
        self.tax_inclusive_false = Tax.objects.create(display_name='tax_true', 
                                                      inclusive=False,
                                                      percentage=50,
                                                      country='PL')

    def test_get_data(self):
        self.assertGreater(User.objects.all().count(), 0)
        self.assertGreater(Item.objects.all().count(), 0)
        self.assertGreater(OrderItem.objects.all().count(), 0)
        self.assertGreater(Order.objects.all().count(), 0)

    def cart_number(self):
        cart_number = Order.objects.filter(user=self.user,
                                           status=Order.STATUS_CART).count()
        return cart_number

    def test_function_cart(self):
        """
        Checking quantity carts:
        1. No cart
        2. Create cart
        3. Delete cart
        ========================
        Add: @staticmethod Order.get_cart(user: User)
        """

        # 1. No cart
        self.assertEqual(self.cart_number(), 0)

        # 2. Create cart
        cart = Order.get_cart(self.user)
        self.assertEqual(self.cart_number(), 1)

        # 3. Delete cart
        cart.delete()
        self.assertEqual(self.cart_number(), 0)

    def test_recalculation_of_the_order_amount(self):
        """
        1. The price is recalculated when a new OrderItem is added
        2. The price is recalculated when the Item.price changes
        3. Order.amount should not change if the Order.status != STATUS_CART
        4. The price is recalculated when a OrderItem is deleted
        ====================================================================
        Add: Item.save_all_related_order_items_fields()
             @receiver Item.save_order_items_after_save()
             Order.get_amount()
             Order.make_order()
             OrderItem.get_order_item_price()
             @receiver OrderItem.recalculate_order_amount_after_save()
             @receiver OrderItem.recalculate_order_amount_after_delete()
        """

        # 1. The price is recalculated when a new OrderItem is added
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(0))
        self.assertEqual(self.item_1.price, Decimal(400))
        OrderItem.objects.create(id=5, order=cart, item=self.item_1, quantity=2)

        self.assertEqual(cart.amount, Decimal(800))

        # 2. The price is recalculated when the Item.price changes
        self.item_1.price = 100
        self.item_1.save()

        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(200))

        # 3. Order.amount should not change if the Order.status != STATUS_CART
        self.assertEqual(cart.id, 5)
        cart.make_order()
        self.item_1.price = 300
        self.item_1.save()

        order = Order.objects.get(id=5)
        self.assertEqual(order.amount, Decimal(200))

        # 4. The price is recalculated when a OrderItem is deleted
        cart = Order.get_cart(self.user)
        self.assertEqual(self.item_2.price, Decimal(200))
        order_item = OrderItem.objects.create(order=cart, item=self.item_2, quantity=1)

        self.assertEqual(cart.amount, Decimal(200))
        order_item.delete()

        self.assertEqual(cart.amount, Decimal(0))

    def test_discount_and_tax_order_recalculation(self):
        """
        1. Order amount is recalculated when discount is added
        2.1. Order amount is recalculated when tax is added (inclusive=False)
        2.2. Order amount is recalculated when tax is added (inclusive=True)
        ======================================================
        Add: Order.calculate_amount_discount()
             @receiver Order.recalculate_amount_pre_save()
             Order.calculate_amount_tax()
        """

        # 1. Order amount is recalculated when discount is added
        self.assertEqual(self.item_1.price, Decimal(400))
        cart = Order.get_cart(self.user)
        OrderItem.objects.create(order=cart, item=self.item_1)
        self.assertEqual(cart.final_amount, Decimal(400))

        cart.discount = self.discount
        cart.save()

        self.assertEqual(cart.final_amount, Decimal(360))

        # 2.1. Order amount is recalculated when tax is added (inclusive=False)
        self.assertEqual(self.tax_inclusive_false.percentage, 50)
        cart.tax = self.tax_inclusive_false
        cart.save()

        cart = Order.get_cart(self.user)
        self.assertEqual(cart.final_amount, Decimal(540))
        # 2.2. Order amount is recalculated when tax is added (inclusive=True)
        cart.tax = self.tax_inclusive_true
        cart.save()
        
        self.assertEqual(cart.final_amount, Decimal(360))