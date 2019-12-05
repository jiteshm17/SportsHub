from django.contrib import admin
from shopping.models import Category, Product, Review, DeliveryOptions

admin.site.register([Category, Product, Review, DeliveryOptions])
