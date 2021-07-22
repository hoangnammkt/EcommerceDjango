from django import template
from ..models import Shipping

register = template.Library()

@register.filter
def filter_item(order_items, order):
    return order_items.filter(order=order)

@register.filter
def total(price, quantity):
    return price * quantity