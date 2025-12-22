from pyexpat.errors import messages
from urllib import request
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from .models import Cart, Product, CartProduct, Order, OrderItem
from django.core.paginator import Paginator
from .form import ProductFiltereForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F, Sum, DecimalField
from django.db.models.expressions import ExpressionWrapper
from .utils import generate_order_id
from django.db import transaction, IntegrityError


def home(request):

    featured_products = Product.objects.filter(featured=True).order_by("-created_at")[
        :8
    ]
    # [0:8] means we want only first 8 products

    context = {"products": featured_products}

    return render(request, "store/home.html", context)


def products(request):

    products = Product.objects.all().order_by("-created_at")

    filter_form = ProductFiltereForm(request.GET)

    # filtering by name
    if filter_form.is_valid():
        name = filter_form.cleaned_data.get("name")
        if name:
            products = products.filter(
                name__icontains=name
            )  # icontains is case insensitive, either the name is contains the search term or not

    # filtering by min price
    if filter_form.is_valid():
        min_price = filter_form.cleaned_data.get("min_price")
        if min_price is not None:
            products = products.filter(
                price__gte=min_price
            )  # gte means greater than or equal to

    # filtering by max price
    if filter_form.is_valid():
        max_price = filter_form.cleaned_data.get("max_price")
        if max_price:
            products = products.filter(
                price__lte=max_price
            )  # lte means less than or equal to

    # filtering by category
    if filter_form.is_valid():
        categories = filter_form.cleaned_data.get("categories")
        if categories:
            products = products.filter(
                categories__in=categories
            )  # __in is used to filter by multiple values

    # sorting
    sorting_key = filter_form.cleaned_data.get("sorting_key")
    if sorting_key:
        if sorting_key == "price_asc":
            products = products.order_by("price")  # price means ascending
        elif sorting_key == "price_desc":
            products = products.order_by("-price")  # -price means descending
        elif sorting_key == "oldest":
            products = products.order_by("created_at")  # oldest
        elif sorting_key == "latest":
            products = products.order_by("-created_at")  # latest

    # pagination
    products_paginator = Paginator(products, 16)
    page_number = request.GET.get("page")
    page_obj = products_paginator.get_page(page_number)

    context = {
        "products": page_obj,
        "filter_form": filter_form,
    }

    return render(request, "store/products.html", context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {"product": product}
    return render(request, "store/product_detail.html", context)


@login_required(login_url=reverse_lazy("accounts:login_page"))
def add_to_cart(request, pk):  # pk means primary key
    try:
        product = get_object_or_404(Product, pk=pk)
        logged_in_user = request.user
        cart, created = Cart.objects.get_or_create(user=logged_in_user)

        if CartProduct.objects.filter(cart=cart, product=product).exists():
            # to check if the product is already in the cart

            messages.success(request, f"{product.name} is already in your cart.")
            return redirect("store:product_detail_page", pk=pk)

        quantity = int(
            request.POST.get("quantity")
        )  # default quantity is 1 if not provided
        if quantity < 0:
            messages.error(request, "Quantity can not be Zero.")
            return redirect("store:product_detail_page", pk=pk)

        # cart.products.add(product)
        CartProduct.objects.create(
            cart=cart, product=product, quantity=quantity
        )  # creating a through model instance
        messages.success(request, f"{product.name} was added to your cart.")
    except Exception:
        # print(e)
        messages.error(
            request, "An error occurred while adding the product to your cart."
        )

    return redirect("store:product_detail_page", pk=pk)


def remove_from_cart(request, pk):  # pk means primary key
    try:
        cart_item = CartProduct.objects.get(pk=pk)

    except CartProduct.DoesNotExist:
        messages.error(request, "Item doesnot exist in your cart.")

    except Exception as e:
        print(e)
        messages.error(request, "Removing item from cart failed.")
    else:
        cart_item.delete()
        messages.success(
            request, f"{cart_item.product.name} was removed from your cart."
        )
        return redirect("store:cart_page")


def update_cart(request, pk):  # pk means primary key
    try:
        cart_item = CartProduct.objects.get(pk=pk)

    except CartProduct.DoesNotExist:
        messages.error(request, "Item doesnot exist in your cart.")

    except Exception as e:
        print(e)
        messages.error(request, "Updating item from cart failed.")
    else:
        try:
            updated_quantity = int(request.POST.get("quantity"))

        except ValueError:
            messages.error(request, "Quantity must be an integer.")

        else:
            if updated_quantity < 0:
                messages.error(request, "Quantity can not be Zero.")

            cart_item.quantity = updated_quantity
            cart_item.save()
            messages.success(request, f"{cart_item.product.name} quantity was updated.")

    return redirect("store:cart_page")


@login_required(login_url=reverse_lazy("accounts:login_page"))
def cart(request):
    try:
        user_cart = request.user.cart
        if cart is not None:
            # cart_products = CartProduct.objects.filter(cart=user_cart)
            # cart_total = 0
            # for cart_item in cart_products:
            #     cart_total += cart_item.get_total_price

            cart_products = CartProduct.objects.filter(cart=user_cart).annotate(
                subtotal=ExpressionWrapper(
                    F("product__price") * F("quantity"),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )

            cart_total = cart_products.aggregate(total=Sum("subtotal"))["total"] or 0

    except Exception:
        messages.error(request, "Something went wrong, please try again later")
        return redirect("store:home_page")

    context = {"products": cart_products, "cart_total": cart_total}

    return render(request, "store/cart.html", context)


@login_required(login_url=reverse_lazy("accounts:login_page"))
def place_order(request):
    # print("place order")
    user_cart = request.user.cart
    print(user_cart)

    cart_products = CartProduct.objects.filter(cart=user_cart).annotate(
        subtotal=ExpressionWrapper(
            F("product__price") * F("quantity"),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )
    )

    cart_sub_total = cart_products.aggregate(total=Sum("subtotal"))["total"] or 0

    try:
        order_id = generate_order_id(request.user.id)

        with transaction.atomic():
            # Create new order
            new_order = Order.objects.create(
                user=request.user,
                order_id=order_id,
                subtotal=cart_sub_total,
            )
        # Create order items for the new order
        for cart_item in cart_products:
            OrderItem.objects.create(
                order=new_order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
            )
        # remove ordered items from the cart
        for cart_item in cart_products:
            cart_item.delete()

    except IntegrityError:
        messages.error(request, "Something went wrong, please try again later")
        return redirect("store:cart_page")

    except Exception as e:
        print("unexpected error", e)
        return redirect("store:cart_page")

    else:
        messages.success(request, "Order placed successfully")

        return redirect("store:order_page")


@login_required(login_url=reverse_lazy("accounts:login_page"))
def cancel_order(request, pk):
    try:
        order_to_delete = Order.objects.get(pk=pk)

    except Order.DoesNotExist:
        messages.error(request, "Something went wrong, please try again later") 
    else:
        order_to_delete.delete()
        messages.success(request, "Order cancelled successfully")

    return redirect("store:order_page")    


@login_required(login_url=reverse_lazy("accounts:login_page"))
def order(request):
    orders = Order.objects.filter(user=request.user)

    context = {"orders": orders}
    return render(request, "store/order.html", context)
