from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import status
from rest_framework.response import Response
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from cart.models import OrderItem, Order, Transaction
from shopping.models import Product
from user_auth.forms import Contact_Form
from user_auth.models import Profile, Services
from cart.extra import generate_order_id
import datetime
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from paypal.standard.forms import PayPalPaymentsForm
from cart.models import OrderLogs


def make_payment(request):
    # What you want the button to do.
    paypal_dict = {
        "business": "manojmnayala@gmail.com",
        "amount": "10.00",
        "item_name": "name of the item",
        "invoice": "unique-invoice-id",
        # "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        # "return": request.build_absolute_uri(reverse('your-return-view')),
        # "cancel_return": request.build_absolute_uri(reverse('your-cancel-view')),
        "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
        "currency_code": "INR",
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form, 'Shopping': 'active'}
    return render(request, "cart/payment.html", context)


def get_user_pending_order(request):
    u = User.objects.get(pk=request.user.pk)
    user_profile = Profile.objects.get(user_name=u)
    ord = Order.objects.filter(owner=user_profile, is_ordered=False)

    # print(ord.is_ordered)

    if ord.exists():
        return ord[0]
    return 0


@login_required
@csrf_exempt
def add_to_cart(request, prod_id):
    product = Product.objects.get(id=prod_id)

    # print(product.stock)
    # shippingcost = request.POST['ShippingCost']
    # shippingcost = int(shippingcost)
    # print('Shipping cost is', shippingcost)
    # return HttpResponse('hello')
    # if request.GET:
    #     vendorid = request.GET['vendorid']
    #     print(vendorid)
    #     ven_qty = VendorQty.objects.get(id=vendorid)
    #     ven = ven_qty.Vendor
    #     print(ven)
    #     print(ven_qty)

    u = User.objects.get(pk=request.user.pk)
    user_profile = Profile.objects.get(user_name=u)
    # print(user_profile)

    user_order, status = Order.objects.get_or_create(owner=user_profile, is_ordered=False)

    # print(user_order, status)

    if status:
        ref_code = generate_order_id()
        print(ref_code)
        order_item, status = OrderItem.objects.get_or_create(product=product, ref_code=ref_code)
        if request.method == 'POST' and 'select-vendor' in request.POST:
            cost = request.POST['select-vendor']
            order_item.delivery_cost = cost
            order_item.save()
        order_item.save()
        user_order.items.add(order_item)
        user_order.ref_code = ref_code
        user_order.save()
    else:
        order_item, status = OrderItem.objects.get_or_create(product=product, ref_code=user_order.ref_code)
        if request.method == 'POST' and 'select-vendor' in request.POST:
            cost = request.POST['select-vendor']
            order_item.delivery_cost = cost
            order_item.save()
        user_order.items.add(order_item)
        user_order.save()

    # if request.GET:
    #     nextto = request.GET["nextto"]
    #     return redirect(nextto)

    # return reverse(redirect('cart:order_summary'), args=(shippingcost,))
    if request.method == 'POST' and 'select-vendor' in request.POST:
        cost = request.POST['select-vendor']
        cost = str(cost)
        return redirect(reverse('cart:order_summary', args=(cost,)))
    return redirect(reverse('cart:order_summary', args=('0',)))


@login_required
def delete_from_cart(request, item_id):
    item_to_delete = OrderItem.objects.filter(pk=item_id)
    if item_to_delete.exists():
        item_to_delete[0].delete()
    return redirect(reverse('cart:order_summary', args=('0',)))


@login_required
def order_details(request, cost):
    existing_order = get_user_pending_order(request)

    context = {
        'order': existing_order,
        'Shopping': 'active'
    }
    if request.session.get('msg'):
        context['msg'] = request.session.get('msg')
        request.session['msg'] = None
    return render(request, 'cart/order_summary.html', context)


@login_required
def checkout(request, **kwargs):
    existing_order = get_user_pending_order(request)
    context = {
        'ordre': existing_order,
        'Shopping': 'active'
    }

    return render(request, 'cart/checkout.html', context)


def get_user_details(request):
    u = Profile.objects.get(user_name=request.user)
    user_form = Contact_Form(instance=u)

    if request.method == 'POST':
        user_form = Contact_Form(request.POST, instance=u)
        if user_form.is_valid():
            return redirect(reverse('payment:process'))

    return render(request, 'cart/get_user_details.html', {'form': user_form})


@login_required
def update_transaction_records(request):
    order_to_purchase = get_user_pending_order(request)
    request.session['order_id'] = order_to_purchase.pk
    u = Profile.objects.get(user_name=request.user)
    user_form = Contact_Form(instance=u)
    if request.method == 'POST':
        user_form = Contact_Form(request.POST, instance=u)
        if user_form.is_valid():
            user_form.save()
            return redirect(reverse('payment:process'))

    return render(request, 'cart/get_user_details.html', {'form': user_form})


def qtyupdate(request):
    a = request.POST.get('item_id')
    if request.method == "POST":
        order_id = request.POST["order_id"]
        item_id = request.POST["item_id"]
        qty = request.POST["z"]
        order = get_user_pending_order(request)
        item = order.items.get(pk=item_id)
        item.qty = qty
        print("data: " + item_id + "        " + order_id + "           " + qty)
        item.save()
        order.save()
    return HttpResponse(" ")


@api_view(['POST'])
def get_logs(request):
    if Services.objects.filter(token=request.GET.get('api_key'), service_type='Products').exists():
        if request.method == 'POST':
            data = JSONParser().parse(request)
            try:
                user = data['user']
                print('User is',user)
                product = data['product']
                print('Product is',product)
                cost = data['cost']
                print('Cost is',cost)
                qty = data['qty']
                print('qty is',qty)
                # print(user, product, cost, qty)
                OrderLogs.objects.create(user=user, product=product, cost=cost, qty=qty)

                return Response('User Logs created', status=status.HTTP_200_OK)
            except:
                return Response('Data not valid/sufficient', status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response('Invalid API Key', status=status.HTTP_400_BAD_REQUEST)
