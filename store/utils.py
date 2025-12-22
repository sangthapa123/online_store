from datetime import datetime

# generate order id for user
def generate_order_id(user_id):
    now = datetime.now()
    return f"{now.year}{now.month}{now.day}{user_id}{now.hour}{now.minute}"
