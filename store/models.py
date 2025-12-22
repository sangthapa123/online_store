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
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    featured = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    categories = models.ManyToManyField(Category, related_name="products")

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField("accounts.CustomUser", on_delete=models.CASCADE)

    products = models.ManyToManyField(Product, through="CartProduct")

    def __str__(self):
        return f"Cart {self.id}"


class CartProduct(models.Model):  # through model
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="carts")
    # related_name is used to access the related objects from the other side of the relationship

    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="cart_products"
    )
    # related_name is used to access the related objects from the other side of the relationship

    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True, null=True)

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in cart {self.cart.id}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        PAID = "Paid", "paid"
        CANCELLED = "Cancelled", "Cancelled"
        SHIPPED = "Shipped", "Shipped"
        DELIVERED = "Delivered", "Delivered"

    user = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.PROTECT,
        related_name="orders",
    )

    order_id = models.CharField(max_length=30, unique=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} ({self.user.email})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )
    product_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in order {self.order.order_id}"
