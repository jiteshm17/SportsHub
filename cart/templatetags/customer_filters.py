from django import template

from shopping.models import Product

register = template.Library()


@register.filter
def get_qty(stock):
    try:
        stock = int(stock)
    except ValueError:
        raise ValueError('Stock should be an integer!')
    if stock <= 10:
        return list(range(stock))
    else:
        return list(range(10))


@register.filter
def get_qty_number(item):
    product = Product.objects.get(prod_name=item.product)
    arr = get_qty(product.stock)
    return arr


@register.simple_tag()
def multiply(qty, unit_price, *args, **kwargs):
    return qty * unit_price


@register.simple_tag()
def sum(cost, delivery, *args, **kwargs):
    return cost + delivery


@register.simple_tag()
def sum_multiply(qty, unit_price, delivery, *args, **kwargs):
    return (qty * unit_price) + delivery
