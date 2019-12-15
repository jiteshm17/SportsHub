import json

import requests
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from decimal import Decimal
import datetime
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from cart.models import Order
from django.views.decorators.csrf import csrf_exempt
from cart.views import get_user_pending_order
from django.contrib.auth.models import User
from user_auth.models import Profile
from shopping.models import Product
from cart.models import Transaction, OrderItem
from shopping.models import DeliveryOptions
from user_auth.models import DeliveryLocation


# Create your views here.

@csrf_exempt
def payment_done(request):
    order_to_purchase = get_user_pending_order(request)
    order_to_purchase.is_ordered = True
    order_to_purchase.date_ordered = datetime.datetime.now()

    order_items = order_to_purchase.items.all()
    pincode = DeliveryLocation.objects.get(user_name=request.user)
    url = 'http://127.0.0.1:7000/ordered_log/'
    profile = Profile.objects.get(user_name=request.user)
    for item in order_items:
        product = Product.objects.get(prod_name=item.product)
        product.stock -= item.qty
        if item.delivery_cost > 0:
            print('before delivery options')
            d = DeliveryOptions.objects.get(product=product, cost=item.delivery_cost, location=pincode.location)
            print('entring json dump')
            data = json.dumps(
                {'name': d.name_id, 'product': d.product.id, 'location': pincode.location, 'pincode': pincode.pin_code,
                 'prod_name': d.product.prod_name,
                 'address': profile.address, 'phonenum': profile.phone_number,
                 'customer_name': request.user.username, 'mail': request.user.email, 'order_id': order_to_purchase.ref_code})
            print('requesting')
            requests.post(url=url, data=data)

        product.save()

    order_items.update(is_ordered=True, date_ordered=datetime.datetime.now())

    u = User.objects.get(pk=request.user.pk)
    profile = Profile.objects.get(user_name=u)
    transaction = Transaction(profile=profile,
                              order_id=order_to_purchase.ref_code,
                              amount=order_to_purchase.get_cart_total(),
                              success=True)

    transaction.save()
    order_to_purchase.save()
    subject = 'Your order has been successfully placed'
    context = {
        'ordre': order_to_purchase,
        'user': request.user,
        'total': order_to_purchase.get_cart_total(),
    }
    html = render_to_string('cart/message.html', context)
    message = render_to_string('cart/message.html', context)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [request.user.email]

    send_mail(subject, message, email_from, recipient_list, fail_silently=False, html_message=html)
    messages.info(request, "Thank you! Your purchase was successful!")
    return render(request, 'payment/done.html', {'Shopping': 'active'})


@csrf_exempt
def payment_canceled(request):
    return render(request, 'payment/canceled.html', {'Shopping': 'active'})


def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    host = request.get_host()

    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": '%.2f' % order.get_cart_total(),
        "item_name": 'Order {}'.format(order.ref_code),
        "invoice": order.ref_code,
        "notify_url": 'http://{}{}'.format(host, reverse('paypal-ipn')),
        "return": 'http://{}{}'.format(host, reverse('payment:done')),
        "cancel_return": 'http://{}{}'.format(host, reverse('payment:canceled')),

        "currency_code": "USD",
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form, 'order': order, 'Shopping': 'active'}
    return render(request, "payment/process.html", context)


def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    print('in show nme the money')
    payStatus = ipn_obj.POST.get('payment_status', '')

    if payStatus == 'Completed':
        print('done')
        print(ipn_obj.POST.get('txn_id'))
        print(ipn_obj.POST.get('mc_gross'))


def your_orders(request):
    orders = Order.objects.filter(owner=Profile.objects.get(user_name=request.user), is_ordered=True)
    return render(request, 'payment/your_orders.html', {'orders': orders, 'Your_Orders': 'active'})