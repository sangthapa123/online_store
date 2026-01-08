from background_task import background
from django.core.mail import send_mail
import time


@background()
def order_placed_mail_send_task(from_email,user_email, order_id, init_payment_url):

    time.sleep(5)  # Simulate delay for email sending
    print("Sending order placed email...", user_email)
    send_mail(
                subject="Order Placed Successfully", 
                message=f"""Your order with order id {order_id} has been placed successfully.\nPlease forward with payment to get your order delivered.""",

                html_message=f"""
                Your Order ID: {order_id}.\nYou can click here to pay:
                <a href="{init_payment_url}">Pay Now</a>

                """,

                from_email=from_email,
                recipient_list=[user_email],
                fail_silently=False
            ) 

    