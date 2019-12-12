from django.db import models
from django.forms import ValidationError
from django.contrib.auth.models import User
from shopping.models import Product


def phone_number_validation(ph_num):
    if len(str(ph_num)) != 10:
        raise ValidationError('The phone number must have 10 digits only')
    elif ph_num < 0:
        raise ValidationError('The phone number must be positive')


def pin_code_validation(pincode):
    if len(str(pincode)) != 6:
        raise ValidationError('The pincode must have 6 digits only!')


class DeliveryLocation(models.Model):
    user_name = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    pin_code = models.IntegerField(validators=[pin_code_validation])
    location = models.CharField(max_length=150)

    def __str__(self):
        return self.user_name.username


class Profile(models.Model):
    user_name = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    prod = models.ManyToManyField(Product, blank=True)
    location = models.CharField(max_length=100, null=True)
    address = models.TextField(max_length=1000, null=True)
    phone_number = models.BigIntegerField(null=True)

    def __str__(self):
        return self.user_name.username


service_choices = (('Tournaments', 'Tournaments'),
                   ('Products', 'Products'),
                   ('Bidding', 'Bidding'))


class Services(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=150, choices=service_choices)
    token = models.CharField(max_length=150)

    class Meta:
        unique_together = ('user_name', 'service_type')

    def __str__(self):
        return self.user_name.username
