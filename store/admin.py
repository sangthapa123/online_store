from django.contrib import admin
from .models import Cart, Product, Category


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)

