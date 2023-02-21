from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from decimal import Decimal

User = get_user_model()


class Item(models.Model):
    name = models.CharField(verbose_name='Item name', max_length=255)
    description = models.TextField(verbose_name='Item description')
    price = models.DecimalField(verbose_name='Item price', max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        return self.name

    @property
    def get_cents(self):
        return int(self.price) * 100

    def save_all_related_order_items_fields(self):
        order_items = self.orderitem_set.all()
        for item in order_items:
            item.save()


@receiver(post_save, sender=Item)
def save_order_items_after_save(sender, instance, **kwargs):
    item = instance
    item.save_all_related_order_items_fields()


class Discount(models.Model):
    name = models.CharField(verbose_name='Name', max_length=100)
    currency = models.CharField(verbose_name='Currency', max_length=3)
    percent_off = models.PositiveSmallIntegerField(verbose_name='Discount percentage', default=0,
                                                   validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_redemptions = models.IntegerField('Max redemptions', default=100)

    class Meta:
        verbose_name = 'Discount'
        verbose_name_plural = 'Discounts'

    def __str__(self):
        return f'{self.name} -{self.percent_off}%'


class Tax(models.Model):
    display_name = models.CharField(verbose_name='Tax type', max_length=150)
    inclusive = models.BooleanField(verbose_name='Tax is included in the order amount', default=True)
    percentage = models.PositiveSmallIntegerField(verbose_name='Tax percentage', default=0,
                                                  validators=[MinValueValidator(0), MaxValueValidator(100)])
    country = models.CharField(verbose_name='Valid two-letter ISO country code', max_length=2)
    state = models.CharField(verbose_name='Valid two-letter ISO state code (for USA)', max_length=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Tax'
        verbose_name_plural = 'Taxes'

    def __str__(self):
        if self.state is not None:
            return f'{self.display_name}: {self.country} - {self.state}'
        else:
            return f'{self.display_name}: {self.country}'


class Order(models.Model):
    STATUS_CART = 1
    STATUS_CONFIRMED = 2
    STATUS_CHOICES = [
        (STATUS_CART, 'Cart'),
        (STATUS_CONFIRMED, 'Order confirmed'),
    ]

    discount = models.ForeignKey(to=Discount, verbose_name='Discount', on_delete=models.CASCADE, null=True, blank=True)
    tax = models.ForeignKey(to=Tax, verbose_name='Tax', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(to=User, verbose_name='Customer', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(verbose_name='Amount', max_digits=12, decimal_places=2, default=0)
    final_amount = models.DecimalField(verbose_name='Final amount', max_digits=12, decimal_places=2, default=0)
    creation_time = models.DateTimeField('Order creation time', default=timezone.now)
    status = models.PositiveSmallIntegerField('Order status', choices=STATUS_CHOICES, default=STATUS_CART)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        if self.status == self.STATUS_CART:
            return f'Cart  №{self.id}'
        return f'Order №{self.id}'

    @staticmethod
    def get_cart(user: User):
        cart = Order.objects.filter(user=user,
                                    status=Order.STATUS_CART
                                    ).first()
        if not cart:
            cart = Order.objects.create(user=user,
                                        status=Order.STATUS_CART,
                                        amount=0)
        return cart

    @property
    def get_amount(self):
        amount = 0
        for item in self.orderitem_set.all():
            amount += item.get_order_item_price
        return amount

    @property
    def get_amount_cents(self):
        return int(self.amount) * 100

    @property
    def get_final_amount_cents(self):
        return int(self.final_amount) * 100

    def make_order(self):
        if self.status == self.STATUS_CART:
            if self.final_amount == Decimal(0):
                self.final_amount = self.amount
            self.status = self.STATUS_CONFIRMED
            self.save()

    @property
    def calculate_amount_discount(self):
        amount_discount = self.amount/100 * self.discount.percent_off
        return amount_discount

    @property
    def calculate_amount_tax(self):
        if self.tax.inclusive is False:
            amount_tax = self.final_amount/100 * self.tax.percentage
            return amount_tax
        return Decimal(0)


@receiver(pre_save, sender=Order)
def recalculate_amount_pre_save(sender, instance, **kwargs):
    order = instance
    order.final_amount = order.amount
    if order.discount:
        order.final_amount -= order.calculate_amount_discount
    if order.tax:
        order.final_amount += order.calculate_amount_tax


class OrderItem(models.Model):
    order = models.ForeignKey(to=Order, verbose_name='Order', on_delete=models.CASCADE)
    item = models.ForeignKey(to=Item, verbose_name='Item', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(verbose_name='Quantity', default=1)

    @property
    def get_order_item_price(self):
        return Decimal(self.item.price * self.quantity)


@receiver(post_save, sender=OrderItem)
def recalculate_order_amount_after_save(sender, instance, **kwargs):
    order = instance.order
    if order.status == order.STATUS_CART:
        order.amount = order.get_amount
        order.final_amount = order.get_amount
        order.save()


@receiver(post_delete, sender=OrderItem)
def recalculate_order_amount_after_delete(sender, instance, **kwargs):
    order = instance.order
    if order.status == order.STATUS_CART:
        order.amount = order.get_amount
        order.final_amount = order.get_amount
        order.save()