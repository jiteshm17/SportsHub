from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    cat_name = models.CharField(max_length=150)

    def __str__(self):
        return self.cat_name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    prod_name = models.CharField(max_length=150)
    description = models.TextField(max_length=264, blank=True)
    stock = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)
    brand = models.CharField(max_length=150, blank=True)
    prod_pic = models.FileField(upload_to='documents/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    weight = models.PositiveIntegerField(default=2)

    def __str__(self):
        return self.prod_name

    def get_qty(self):
        return self.stock


class DeliveryOptions(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    name_id = models.IntegerField()
    days = models.PositiveIntegerField()
    cost = models.FloatField()
    location = models.CharField(max_length=150)

    class Meta:
        unique_together = ('name_id', 'product', 'location')

    def __str__(self):
        return self.name


class Review(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    rating = models.IntegerField(null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.content
