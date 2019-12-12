from django.contrib import admin
from user_auth.models import *

admin.site.register([Profile, DeliveryLocation, Services])
