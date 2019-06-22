from django.contrib import admin
from .models import Category, Manufacturer, Product, CartItem, Cart, Order


admin.site.register(Category)
admin.site.register(Manufacturer)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Order)
