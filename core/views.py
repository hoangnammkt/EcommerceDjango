import json
import datetime
from .models import *
from .filters import *
from django.http import JsonResponse
from .utils import cookieCart, cartData, guestOrder
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# Home page
class HomeView(ListView):
    def get(self, request):
        template_name = 'home.html'
        products = Product.objects.all().order_by('-id')
        paginator = Paginator(products, 8)
        page = request.GET.get('page', 1)

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        cartItems = cart_items(request)
        context = {
            'products': products,
            'cartItems': cartItems,
            'page': page,
        }
        return render(request, template_name, context)


# Product detail page
class ProductView(DetailView):
    def get(self, request, slug):
        template_name = 'product.html'
        product = get_object_or_404(Product, slug=slug)
        cartItems = cart_items(request)
        context = {'product': product, 'cartItems': cartItems}
        return render(request, template_name, context)


# Display product all categories
def categories(request):
    products = Product.objects.all().order_by('-id')
    categorys = Category.objects.all().order_by('-id')
    cartItems = cart_items(request)

    # Filter
    myFilter = ProductFilter(request.GET, queryset=products)
    products = myFilter.qs

    # Paginator
    paginator = Paginator(products, 9)
    page = request.GET.get('page', 1)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    template_name = 'category.html'
    context = {
        'products': products,
        'cartItems': cartItems,
        'categorys': categorys,
        'page': page,
        'myFilter': myFilter
    }
    return render(request, template_name, context)


# Display product in a category
def category(request, slug):
    category_title = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category_title).order_by('-id')
    cartItems = cart_items(request)
    # Filter
    myFilter = ProductFilter(request.GET, queryset=products)
    products = myFilter.qs

    context = {
        'products': products,
        'cartItems': cartItems,
        'category_title': category_title,
        'myFilter': myFilter
    }
    template_name = 'category_details.html'
    return render(request, template_name, context)


# Cart page
def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    quantity = data['quantity']
    cartItems = cart_items(request)
    context = {'items': items, 'order': order, 'quantity': quantity, 'cartItems': cartItems}
    return render(request, 'cart.html', context)


# Get cart items function
def cart_items(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
        cartItems = 0
        for i in cart:
            cartItems += cart[i]["quantity"]
    return cartItems


# Checkout page
def checkout(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    quantity = data['quantity']
    context = {'items': items, 'order': order, 'quantity': quantity}
    return render(request, 'checkout.html', context)


# Update quantity
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


# Process Order
def processOrder(request):
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = datetime.datetime.now().timestamp()

    if total == order.get_cart_total:
        order.complete = True
    order.save()
    Shipping.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
    )
    return JsonResponse('Payment submitted..', safe=False)


# Build PC
def build(request):
    mainboards = Product.objects.filter(category__title__contains="Motherboards")
    power = Product.objects.filter(category__title__contains="Power Supplies")
    monitors = Product.objects.filter(category__title__contains="Monitors")
    storage = Product.objects.filter(category__title__contains="Data Storage")
    videocard = Product.objects.filter(category__title__contains="Video Cards")
    cartItems = cart_items(request)
    context = {
        'cartItems': cartItems,
        'motherboards': mainboards,
        'power': power,
        'monitors': monitors,
        'storage': storage,
        'videocard': videocard,
    }
    return render(request, 'build.html', context)


# Load Processors (Build PC)
def load_cpu(request):
    socket_type = request.GET.get('socket')
    processors = Product.objects.filter(category__title="Processors", socket__title=socket_type)
    return render(request, 'processors.html', {'processors': processors})


# Load Memory (Build PC)
def load_ram(request):
    ram_type = request.GET.get('ramtype')
    memory = Product.objects.filter(category__title__contains="Memory", memory_type__title=ram_type)
    print(ram_type)
    return render(request, 'memory.html', {'memory': memory})


# About
def about(request):
    return render(request, 'about.html')


# Contact
def contact(request):
    return render(request, 'contact.html')


# Return Policy
def returnpolicy(request):
    return render(request, 'returnpolicy.html')
