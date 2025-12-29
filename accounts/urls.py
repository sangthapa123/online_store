from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    
    path("register/", views.register_view, name="register_page"),
    path("login/", views.login_view, name="login_page"),
    path("logout/", views.logout_view, name="logout_page"),
    path("home/", views.home_view, name="home_page"),

    #profile
    path("profile/", views.customer_profile, name="customer_profile"),
    # delivery person
    path(
            "delivery/<order_id>/delivered/",
            views.set_as_delivered,
            name="set_as_delivered",
        ),

    # dummy admin
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
]
