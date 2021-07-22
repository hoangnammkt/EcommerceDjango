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

    path('recommend/', views.recommend, name='recommend'),
    path('recommend/crawl/', views.crawl, name='crawl'),
    # Page
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('returnpolicy/', views.returnpolicy, name='returnpolicy'),


    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/product/', views.product, name='product'),
    path('dashboard/product/add/', views.addproduct, name='add_product'),
    path('dashboard/product/delete/<int:id>', views.deleteprod, name='delete_product'),
    path('dashboard/product/edit/<int:id>', views.editprod, name='edit_product'),
    path('dashboard/product/update/<int:id>', views.updateprod, name='update_product'),
    path('dashboard/product/add/add_by_category', views.add_by_category, name='add_by_category'),

    path('dashboard/orders/', views.orders, name='all_orders'),
    path('dashboard/orders/delete/<int:id>', views.delete_order, name='delete_order'),
    path('dashboard/orders/<int:id>', views.view_order, name='view_order'),
    path('dashboard/orders/update/<int:id>', views.update_status, name='update_status'),
]