import json
import datetime
from .models import *
from .filters import *
from django.http import JsonResponse
from .utils import cookieCart, cartData, guestOrder
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from .decorators import admin_only
from django.core.files.storage import FileSystemStorage
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


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
        phone=data['shipping']['phone'],
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


################################
@login_required(login_url='/login/')
@admin_only
def dashboard(request):
    product = Product.objects.all().count()
    sales = Shipping.objects.all().count()
    delivered = Shipping.objects.filter(status='D').count()
    pending = Shipping.objects.filter(status='P').count()

    shipping = Shipping.objects.order_by('-date_add')[:5]
    ship_earn = Shipping.objects.all()
    order_item = OrderItem.objects.all()
    order = Order.objects.all()

    args = {'product': product, 'sales': sales, 'delivered': delivered, 'pending': pending, 'order_item': order_item, 'order': order,
            'shipping': shipping, 'ship_earn': ship_earn}
    return render(request, 'dashboard/index.html', args)


@login_required(login_url='/login/')
@admin_only
def product(request):
    products = Product.objects.all()
    args = {'products': products}
    return render(request, 'dashboard/product/product.html', args)


@login_required(login_url='/login/')
@admin_only
def deleteprod(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    return redirect('/dashboard/product/')


@login_required(login_url='/login/')
@admin_only
def editprod(request, id):
    product = Product.objects.get(id=id)
    categories = Category.objects.all()
    brands = Brand.objects.all()
    screensize = ScreenSize.objects.all()
    resolution = Resolution.objects.all()
    sockets = Socket.objects.all()
    wattage = Wattage.objects.all()
    seriescpu = SeriesCPU.objects.all()
    memory_type = MemoryType.objects.all()
    capacity = Capacity.objects.all()
    args = {'product': product, 'categories': categories, 'brands': brands, 'screensize': screensize,
            'resolution': resolution, 'sockets': sockets, 'wattage': wattage, 'seriescpu': seriescpu,
            'memory_type': memory_type, 'capacity': capacity}
    return render(request, 'dashboard/product/editproduct.html', args)


@login_required(login_url='/login/')
@admin_only
def updateprod(request, id):
    if request.method == 'POST':
        title = request.POST.get('title')
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price')
        if not discount_price:
            discount_price = None
        description = request.POST.get('description')
        category = request.POST.get('category')
        brandname = request.POST.get('brandname')
        screensize = request.POST.get('screensize')
        resolution = request.POST.get('resolution')
        socket = request.POST.get('socket')
        wattage = request.POST.get('wattage')
        seriescpu = request.POST.get('seriescpu')
        memory_type = request.POST.get('memory_type')
        capacity = request.POST.get('capacity')
        data = Product.objects.filter(id=id)
        data.update(title=title, price=price, discount_price=discount_price,
                    description=description, category=category, brandname=brandname,
                    screensize=screensize, resolution=resolution, socket=socket,
                    wattage=wattage, seriescpu=seriescpu, memory_type=memory_type,
                    capacity=capacity)
        image = request.FILES.get('product_image')
        if image:
            fs = FileSystemStorage()
            fs.save(image.name, image)
            data.update(image=image)

    return redirect('/dashboard/product/')

@login_required(login_url='/login/')
@admin_only
def addproduct(request):
    brands = Brand.objects.all()
    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price')
        if not discount_price:
            discount_price = None
        category = Category.objects.get(id=request.POST.get('category'))
        brandname = Brand.objects.get(id=request.POST.get('brandname'))
        description = request.POST.get('description')
        image = request.FILES.get('product_image')
        fs = FileSystemStorage()
        fs.save(image.name, image)
        print(image.name)
        cat = str(category)
        if cat == 'Memory':
            print(category)
            capacity = Capacity.objects.get(id=request.POST.get('capacity'))
            memory_type = MemoryType.objects.get(id=request.POST.get('memory_type'))
            Product.objects.create(title=title, price=price, discount_price=discount_price, category=category,
                                   brandname=brandname, description=description, image=image, capacity=capacity,
                                   memory_type=memory_type)

        elif cat == 'Video Cards':
            capacity = Capacity.objects.get(id=request.POST.get('capacity'))
            Product.objects.create(title=title, price=price, discount_price=discount_price, category=category,
                                   brandname=brandname, description=description, image=image, capacity=capacity)

        elif cat == 'Data Storage':
            capacity = Capacity.objects.get(id=request.POST.get('capacity'))
            Product.objects.create(title=title, price=price, discount_price=discount_price, category=category,
                                   brandname=brandname, description=description, image=image, capacity=capacity)

        elif cat == 'Motherboards':
            socket = Socket.objects.get(id=request.POST.get('socket'))
            memory_type = MemoryType.objects.get(id=request.POST.get('memory_type'))
            Product.objects.create(title=title, price=price, discount_price=discount_price, category=category,
                                   brandname=brandname, description=description, image=image, socket=socket,
                                   memory_type=memory_type)

        elif cat == 'Monitors':
            screensize = ScreenSize.objects.get(id=request.POST.get('screensize'))
            resolution = Resolution.objects.get(id=request.POST.get('resolution'))
            Product.objects.create(title=title, price=price, discount_price=discount_price, category=category,
                                   brandname=brandname, description=description, image=image, screensize=screensize,
                                   resolution=resolution)

        elif cat == 'Processors':
            socket = Socket.objects.get(id=request.POST.get('socket'))
            seriescpu = SeriesCPU.objects.get(id=request.POST.get('seriescpu'))
            Product.objects.create(title=title, price=price, discount_price=discount_price, category=category,
                                   brandname=brandname, description=description, image=image, socket=socket,
                                   seriescpu=seriescpu)

        elif cat == 'Power Supplies':
            wattage = Wattage.objects.get(id=request.POST.get('wattage'))
            Product.objects.create(title=title, price=price, discount_price=discount_price, category=category,
                                   brandname=brandname, description=description, image=image, wattage=wattage)

        return redirect('/dashboard/product/')

    args = {'brands': brands, 'categories': categories}
    return render(request, 'dashboard/product/addproduct.html', args)

# Add Motherboards
@login_required(login_url='/login/')
@admin_only
def add_by_category(request):
    get_category = request.GET.get('category')
    category = str(Category.objects.get(id=get_category))

    capacity = Capacity.objects.all()
    memory = MemoryType.objects.all()
    socket = Socket.objects.all()
    screensize = ScreenSize.objects.all()
    resolution = Resolution.objects.all()
    cpu = SeriesCPU.objects.all()
    wattage = Wattage.objects.all()

    args = {'capacity': capacity, 'memory': memory, 'socket': socket, 'screensize': screensize,
            'resolution': resolution, 'cpu': cpu, 'wattage': wattage}

    if category == 'Memory':
        return render(request, 'dashboard/product/add_memory.html', args)
    elif category == 'Video Cards':
        return render(request, 'dashboard/product/add_card.html', args)
    elif category == 'Data Storage':
        return render(request, 'dashboard/product/add_storage.html', args)
    elif category == 'Motherboards':
        return render(request, 'dashboard/product/add_motherboards.html', args)
    elif category == 'Monitors':
        return render(request, 'dashboard/product/add_monitors.html', args)
    elif category == 'Processors':
        return render(request, 'dashboard/product/add_processors.html', args)
    else:
        return render(request, 'dashboard/product/add_power.html', args)


@login_required(login_url='/login/')
@admin_only
def orders(request):
    order_items = OrderItem.objects.all()
    orders = Order.objects.all()
    shipping = Shipping.objects.all()

    args = {'order_items': order_items, 'orders': orders, 'shipping': shipping}
    return render(request, 'dashboard/orders.html', args)


@login_required(login_url='/login/')
@admin_only
def delete_order(request, id):
    order = Order.objects.get(id=id)
    order.delete()
    return redirect('/dashboard/orders/')

@login_required(login_url='/login/')
@admin_only
def view_order(request, id):
    status = Shipping.objects.values_list('status', flat=True).distinct()
    shipping_order = Shipping.objects.get(id=id)
    order_item = OrderItem.objects.all()
    args = {'ship': shipping_order, 'status': status, 'order_item': order_item}
    return render(request, 'dashboard/view_order.html', args)

@login_required(login_url='/login/')
@admin_only
def update_status(request, id):
    if request.method == 'POST':
        status = request.POST.get('ship_status')
        data = Shipping.objects.filter(id=id)
        data.update(status=status)
    return redirect('/dashboard/orders/')


# Selenium
def recommend(request):
    cartItems = cart_items(request)
    return render(request, 'recommend.html', {'cartItems': cartItems})


def crawl(request):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--disable-software-rasterizer')
    driver = webdriver.Chrome('core/chromedriver.exe', options=options)
    budget = request.GET.get('budget')
    driver.get('https://choosemypc.net/build/?budget=' + budget + '&oc=false&options=')

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="buildTable"]/tbody')))
    # GET TITLE
    cpu = driver.find_element_by_xpath('//*[@id="cpu"]/td[3]/a').text
    cooler = driver.find_element_by_xpath('//*[@id="cooler"]/td[3]/a').text
    mobo = driver.find_element_by_xpath('//*[@id="mobo"]/td[3]/a').text
    ram = driver.find_element_by_xpath('//*[@id="ram"]/td[3]/a').text
    try:
        ssd = driver.find_element_by_xpath('//*[@id="ssd"]/td[3]/a').text
    except NoSuchElementException:
        ssd = driver.find_element_by_xpath('//*[@id="ssd"]/td[3]/em').text
    hdd = driver.find_element_by_xpath('//*[@id="hdd"]/td[3]/a').text
    gpu = driver.find_element_by_xpath('//*[@id="gpu"]/td[3]/a').text
    case = driver.find_element_by_xpath('//*[@id="case"]/td[3]/a').text
    try:
        power = driver.find_element_by_xpath('//*[@id="psu"]/td[3]/a').text
    except NoSuchElementException:
        power = driver.find_element_by_xpath('//*[@id="psu"]/td[3]/em').text

    # GET PRICE
    cpu_price = driver.find_element_by_xpath('//*[@id="cpu"]/td[5]/a').text
    cooler_price = driver.find_element_by_xpath('//*[@id="cooler"]/td[5]/a').text
    mobo_price = driver.find_element_by_xpath('//*[@id="mobo"]/td[5]/a').text
    ram_price = driver.find_element_by_xpath('//*[@id="ram"]/td[5]/a').text
    try:
        ssd_price = driver.find_element_by_xpath('//*[@id="ssd"]/td[5]/a').text
    except NoSuchElementException:
        ssd_price = '0.00'
    hdd_price = driver.find_element_by_xpath('//*[@id="hdd"]/td[5]/a').text
    gpu_price = driver.find_element_by_xpath('//*[@id="gpu"]/td[5]/a').text
    case_price = driver.find_element_by_xpath('//*[@id="case"]/td[5]/a').text
    try:
        power_price = driver.find_element_by_xpath('//*[@id="psu"]/td[5]/a').text
    except NoSuchElementException:
        power_price = '0.00'

    price_be = driver.find_element_by_xpath('//*[@id="totalbefore"]').text
    args = {'cpu': cpu, 'cooler': cooler, 'mobo': mobo, 'ram': ram, 'ssd': ssd, 'hdd': hdd, 'gpu': gpu, 'case': case,
            'power': power, 'cpu_price': cpu_price, 'cooler_price': cooler_price, 'mobo_price': mobo_price,
            'ram_price': ram_price, 'ssd_price': ssd_price, 'hdd_price': hdd_price, 'gpu_price': gpu_price,
            'case_price': case_price, 'power_price': power_price, 'price_be': price_be}

    return render(request, 'buildTable.html', args)
