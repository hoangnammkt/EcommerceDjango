from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.HomeView.as_view(), name='homepage'),
    path('product/<slug:slug>/', views.ProductView.as_view(), name='product'),
    path('update_item/', views.updateItem, name='update_item'),
    path('process_order/', views.processOrder, name='process_order'),
    path('category/', views.categories, name='categories'),
    path('category/<slug:slug>/', views.category , name='category'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('build/', views.build, name='buildpc'),
    path('load_cpu/', views.load_cpu, name='ajax_load_cpu'),
    path('load_ram/', views.load_ram, name='ajax_load_ram'),
    # Page
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('returnpolicy/', views.returnpolicy, name='returnpolicy'),
]