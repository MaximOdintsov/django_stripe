from django.db import models


class Item(models.Model):
    name = models.CharField('Название товара', max_length=255)
    description = models.TextField('Описание товара')
    price = models.DecimalField('Цена', max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    @property
    def get_cents(self):
        return int(self.price) * 100


# class Discount(models.Model):
#     pass
#
#
# class Tax(models.Model):
#     pass
#
#
# class Order(models.Model):
#     # discount = models.ForeignKey(verbose_name='Скидка', primary_key=Discount, on_delete=models.PROTECT)
#     # tax = models.ForeignKey(verbose_name='Налог', primary_key=Tax, on_delete=models.PROTECT)
#     amount = models.DecimalField('Цена без скидки', max_digits=12, decimal_places=2, default=0)
#
#
# class OrderItem(models.Model):
#     order = models.ForeignKey(verbose_name='Заказ', primary_key=Order, on_delete=models.CASCADE)
#     item = models.ForeignKey(verbose_name='Товар', primary_key=Item, on_delete=models.PROTECT)