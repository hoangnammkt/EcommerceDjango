from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.db.models.signals import post_save


# Category
class Category(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title

    def get_category_url(self):
        return reverse('core:category', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


# All product type model
# Brand
class Brand(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.title


# Socket(main, CPU)
class Socket(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.title


# Series CPU
class SeriesCPU(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.title


# Wattage Power\
class Wattage(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.title


# Ram type
class MemoryType(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.title


# Ram, video card capacity
class Capacity(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.title


# Resolution monitor
class Resolution(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.title


# Screen size monitor
class ScreenSize(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.title


# Product
class Product(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    price = models.FloatField(max_length=5, null=False, blank=False)
    discount_price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, on_delete=models.SET_NULL, null=True)
    brandname = models.ForeignKey(Brand, blank=True, on_delete=models.SET_NULL, null=True)
    screensize = models.ForeignKey(ScreenSize, blank=True, on_delete=models.SET_NULL, null=True)
    resolution = models.ForeignKey(Resolution, blank=True, on_delete=models.SET_NULL, null=True)
    socket = models.ForeignKey(Socket, blank=True, on_delete=models.SET_NULL, null=True)
    wattage = models.ForeignKey(Wattage, blank=True, on_delete=models.SET_NULL, null=True)
    seriescpu = models.ForeignKey(SeriesCPU, blank=True, on_delete=models.SET_NULL, null=True)
    memory_type = models.ForeignKey(MemoryType, blank=True, on_delete=models.SET_NULL, null=True)
    capacity = models.ForeignKey(Capacity, blank=True, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(null=True, blank=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def get_absolute_url(self):
        return reverse('core:product', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


# All product type model - END

# Customer model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, blank=True)

    def create_customer(sender, **kwargs):
        if kwargs['created']:
            user_profile = Customer(user=kwargs['instance'], name=kwargs['instance'])
            user_profile.save()

    post_save.connect(create_customer, sender=User)

    def __str__(self):
        return self.name


# All order models
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_order = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True, unique=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_add = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Order ' + str(self.order)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class Shipping(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    phone = models.CharField(max_length=12, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    address = models.CharField(max_length=300, blank=False)
    city = models.CharField(max_length=30, blank=False)
    state = models.CharField(max_length=30, blank=False)
    zipcode = models.CharField(max_length=10, blank=False)
    date_add = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

# End order models
