import json
from .models import *


def cookieCart(request):
    items = []
    cart = {}
    order = {"get_cart_total": 0, "get_cart_quantity": 0}
    if request.COOKIES.get("cart"):
        cart = json.loads(request.COOKIES["cart"])
    for item in cart:
        cart_quantity = cart[item]["quantity"]
        order["get_cart_quantity"] += cart_quantity
        product = Product.objects.get(id=item)
        total = product.price * cart[item]["quantity"]
        order["get_cart_total"] += total
        item_product = {
            "product": {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "imageURL": product.imageURL,
            },
            "quantity": cart_quantity,
            "get_total_price": total,
        }
        items.append(item_product)
    return {"items": items, "order": order, "cartItems": order["get_cart_quantity"]}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = cookieData["cartItems"]
    else:
        cookieData = cookieCart(request)
        items = cookieData["items"]
        order = cookieData["order"]
        cartItems = cookieData["cartItems"]
    return {"items": items, "order": order, "cartItems": cartItems}


def getOrder(request, data):
    name = data["form"]["name"]
    email = data["form"]["email"]
    cookieData = cookieCart(request)
    items = cookieData["items"]
    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items:
        product = Product.objects.get(id=item["product"]["id"])
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item["quantity"],
        )
    return customer, order
