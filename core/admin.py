from django.contrib import admin
from .models import *


# Register your models here.

class ProductSlug(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


class CategorySlug(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Customer)
admin.site.register(Product, ProductSlug)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Shipping)
admin.site.register(Category, CategorySlug)
admin.site.register(Socket)
admin.site.register(MemoryType)
admin.site.register(Brand)
admin.site.register(ScreenSize)
admin.site.register(SeriesCPU)
admin.site.register(Capacity)
admin.site.register(Wattage)
admin.site.register(Resolution)
