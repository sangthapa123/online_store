from django.contrib import admin
from .models import Cart, Product, Category,Payment


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Payment)

