from django.contrib import admin
from cart.models import Order, OrderItem, Transaction, OrderLogs

admin.site.register((Order, OrderItem, Transaction, OrderLogs))
