import json
from .models import *
from django.shortcuts import get_object_or_404

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    items = []
    quantity = 1
    order = {'get_cart_total': 0, 'get_cart_items': 0}

    for i in cart:
        try:
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]["quantity"])
            order['get_cart_total'] += total
            item = {
                'product': {
                    'id': product.id,
                    'title': product.title,
                    'price': product.price,
                    'imageURL': product.imageURL,
                },
                'quantity': cart[i]["quantity"],
                'get_total': total
            }
            items.append(item)
        except:
            pass

    return {'items': items, 'order': order, 'quantity': quantity}

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        quantity = OrderItem.objects.filter(order=order)
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        quantity = cookieData['quantity']

    return {'items': items, 'order': order, 'quantity': quantity}

def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()
    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
        )
    return customer, order