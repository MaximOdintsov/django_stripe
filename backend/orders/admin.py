from django.contrib import admin
from .models import Item, Order, OrderItem, Tax, Discount


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('item', 'quantity')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'price']
    list_display = ['name', 'description', 'price']
    list_editable = ['description', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fields = ('user', 'tax')
    list_display = ['id', 'creation_time', 'user', 'tax', 'amount', 'status']
    list_editable = ['amount', 'status']
    inlines = [OrderItemInline]


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    fields = ['name', 'currency', 'percent_off', 'max_redemptions']
    list_display = ['name', 'currency', 'percent_off', 'max_redemptions']
    list_editable = ['currency', 'percent_off', 'max_redemptions']


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    fields = ['display_name', 'inclusive', 'percentage', 'country', 'state']
    list_display = ['display_name', 'inclusive', 'percentage', 'country', 'state']
    list_editable = ['inclusive', 'percentage']
