from django.db import models

from shopping.models import Product
from user_auth.models import Profile


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    is_ordered = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    date_ordered = models.DateTimeField(null=True)
    qty = models.IntegerField(null=True, default=1)
    ref_code = models.CharField(max_length=20)
    delivery_cost = models.FloatField(default=0.0)

    def __str__(self):
        return self.product.prod_name

    def __unicode__(self):
        return '%s' % self.product.prod_name


class OrderLogs(models.Model):
    user = models.CharField(max_length=150)
    product = models.CharField(max_length=150)
    cost = models.FloatField()
    qty = models.IntegerField()


class Order(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='o')
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem, related_name='item')
    is_ordered = models.BooleanField(default=False)
    date_ordered = models.DateTimeField(null=True)

    def get_cart_item(self):
        return self.items.all()

    def get_cart_total(self):
        return sum([(item.product.cost * item.qty) + item.delivery_cost for item in self.items.all()])


class Transaction(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    success = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return self.order_id

    class Meta:
        ordering = ['-timestamp']
