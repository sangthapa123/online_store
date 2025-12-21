from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=60)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    image = models.ImageField(upload_to="products/",null =True, blank=True)
    featured = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    categories = models.ManyToManyField(Category, related_name="products")

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.OneToOneField("accounts.CustomUser",
    on_delete = models.CASCADE)

    
    products = models.ManyToManyField(Product, through="CartProduct")

    def __str__(self):
        return f"Cart {self.id}"
    
    
class CartProduct(models.Model): #through model
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="carts") 
    #related_name is used to access the related objects from the other side of the relationship
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_products") 
    #related_name is used to access the related objects from the other side of the relationship
    
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True, null=True)
    @property
    def total_price(self):
        return self.product.price * self.quantity
    
    

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in cart {self.cart.id}"