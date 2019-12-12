from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from cart.models import OrderItem, Order
from shopping.forms import writereview
from .models import Category, Product, Review, DeliveryOptions
from .serializers import ProductSerializer, CategorySerializer
from user_auth.forms import DeliveryLocationForm
from user_auth.models import DeliveryLocation, Profile, Services
import requests


@login_required
def list_categories(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    form = DeliveryLocationForm()

    if DeliveryLocation.objects.filter(user_name=request.user).exists():
        delivery = DeliveryLocation.objects.get(user_name=request.user)
        form = DeliveryLocationForm(instance=delivery)
        if request.method == 'POST':
            form = DeliveryLocationForm(request.POST, instance=delivery)
            if form.is_valid():
                ord = Order.objects.filter(owner=Profile.objects.get(user_name=request.user), is_ordered=False)
                if ord.exists() and ord[0].items.exists():
                    msg = "Please checkout before updating your pincode"
                    request.session['msg'] = msg
                    return redirect(reverse('cart:order_summary', args=('0',)))
                else:
                    pincode = form.cleaned_data['pin_code']
                    url = 'https://api.postalpincode.in/pincode/' + str(pincode)
                    try:
                        response = requests.get(url)
                        postal_locations = response.json()
                        location = postal_locations[0]["PostOffice"][0]["Division"]
                        instance = DeliveryLocation.objects.get(user_name=request.user)
                        print('got responce', location)
                        location = location.split(' ')
                        location = location[0]
                        print('got responce', location.lower())
                        instance.pin_code = pincode
                        instance.location = location.lower()
                        instance.save()
                        return redirect('shopping:home')
                    except:
                        print('error')
                        return render(request, 'shopping/index.html',
                                      {'categories': categories, 'products': products, 'Shopping': 'active',
                                       'form': form,
                                       'msg': 'Enter a vaild pincode'})

        return render(request, 'shopping/index.html',
                      {'categories': categories, 'products': products, 'Shopping': 'active', 'form': form,
                       'delivery_exists': True})

    if request.method == 'POST':
        form = DeliveryLocationForm(request.POST)
        if form.is_valid():
            u = User.objects.get(username=request.user.username)
            pin_code = form.cleaned_data['pin_code']
            url = 'https://api.postalpincode.in/pincode/' + str(pin_code)
            try:
                response = requests.get(url)
                postal_locations = response.json()
                location = postal_locations[0]["PostOffice"][0]["Division"]
                DeliveryLocation.objects.create(user_name=u, pin_code=pin_code, location=location.lower())
                return redirect('shopping:home')
            except:
                print('error')
                return render(request, 'shopping/index.html',
                              {'categories': categories, 'products': products, 'Shopping': 'active', 'form': form,
                               'msg': 'Enter a vaild pincode'})
        else:
            print('The form is not valid')
            print(form.errors)

    return render(request, 'shopping/index.html',
                  {'categories': categories, 'products': products, 'Shopping': 'active', 'form': form})


def itemsview(request, pk):
    categories = Category.objects.all()
    cat = Category.objects.get(id=pk)
    current_order_products = []
    delivery = DeliveryLocation.objects.get(user_name=request.user)
    form = DeliveryLocationForm(instance=delivery)
    if request.method == 'POST':
        form = DeliveryLocationForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            return redirect(reverse('shopping:items', args=(pk,)))

    context = {
        'categories': categories,
        'cat': cat,
        'current_order_products': current_order_products,
        'Shopping': 'active',
        'form': form
    }

    return render(request, "shopping/items.html", context)


@login_required
def itemdetailview(request, ck, pk):
    print('The product key is', pk)
    print('The category key is', ck)
    categories = Category.objects.all()
    cat = Category.objects.get(id=ck)
    prod = Product.objects.get(id=pk)
    current_order_products = []
    delivery_exists = False
    p = Product.objects.get(pk=pk)
    user_pin_code = DeliveryLocation.objects.get(user_name=request.user)
    in_cart = False

    if OrderItem.objects.filter(product=Product.objects.get(id=pk), is_ordered=False).exists():
        print('Item in cart')
        in_cart = True

    if request.method == 'POST':
        form = writereview(request.POST)
        if form.is_valid():
            content = request.POST.get('content')
            rating = request.POST.get('rating')
            review1 = Review.objects.create(category=cat, product=prod, customer=request.user, content=content,
                                            rating=rating)
            review1.save()
            return redirect(reverse('shopping:specificitem', args=(ck, pk,)))
    else:
        form = writereview()
    if DeliveryOptions.objects.filter(product=p, location=user_pin_code.location).exists():
        vendorsList = DeliveryOptions.objects.filter(product=p, location=user_pin_code.location)
        print('The number of vendors are', len(vendorsList))
        delivery_exists = True
        return render(request, 'shopping/itemdetail.html', {'form': form,
                                                            'categories': categories,
                                                            'cat': cat,
                                                            'prod': prod,
                                                            'current_order_products': current_order_products,
                                                            'Shopping': 'active',
                                                            'delivery_exists': delivery_exists,
                                                            'vendorsList': vendorsList,
                                                            'in_cart': in_cart})
    return render(request, 'shopping/itemdetail.html', {'form': form,
                                                        'categories': categories,
                                                        'cat': cat,
                                                        'prod': prod,
                                                        'current_order_products': current_order_products,
                                                        'Shopping': 'active',
                                                        'in_cart': in_cart,
                                                        'delivery_exists': delivery_exists})


@login_required
def reviewtext(request, categ, product):
    prod = get_object_or_404(Product, pk=product)
    cat = get_object_or_404(Category, pk=categ)
    if request.method == 'POST':
        form = writereview(request.POST)
        if form.is_valid():
            content = request.POST.get('content')
            rating = request.POST.get('rating')
            review1 = Review.objects.create(category=cat, product=prod, customer=request.user, content=content,
                                            rating=rating)
            review1.save()
            return redirect(reverse('shopping:specificitem', args=(product, categ,)))
    else:
        form = writereview()
    return render(request, 'shopping/writereview.html', {'form': form, 'Shopping': 'active'})


@api_view(['GET'])
def productList(request):
    if request.method == 'GET':
        if Services.objects.filter(token=request.GET.get('api_key'), service_type='Products').exists():
            products = Product.objects.all()
            for product in products:
                product.stock *= 0.1
            serializer = ProductSerializer(products, many=True)
            return JsonResponse(serializer.data, safe=False)
        else:
            return Response('Invalid API Key', status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def categoriesList(request):
    if request.method == 'GET':
        if Services.objects.filter(token=request.GET.get('api_key'), service_type='Products').exists():
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return JsonResponse(serializer.data, safe=False)
        else:
            return Response('Invalid API Key', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def bidding(request):
    if Services.objects.filter(token=request.GET.get('api_key'), service_type='Bidding').exists():
        if request.method == 'POST':
            data = JSONParser().parse(request)
            # t = Tournaments.objects.get(name=data['tournament'])
            # data['tournament'] = t.pk

            # tournament = get_object_or_404(Tournaments, title=request.data.get('tournament'))
            p_id = data['product']
            name = data['name']
            name_id = data['name_id']
            days = data['days']
            cost = data['cost']
            location = data['location']
            print(name, location)
            if 'msg' in data and data['msg'] == 'delete':
                try:
                    product = Product.objects.get(pk=p_id)
                    instance = DeliveryOptions.objects.get(product=product, name_id=name_id, location=location.lower())
                    instance.delete()
                    print('deleted')
                except:
                    print('found error')
                    return Response({'data is not valid'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'data deleted'}, status=status.HTTP_201_CREATED)

            else:
                try:
                    product = Product.objects.get(pk=p_id)
                    if DeliveryOptions.objects.filter(product=product, name_id=name_id,
                                                      location=location.lower()).exists():
                        instance = DeliveryOptions.objects.get(product=product, name_id=name_id,
                                                               location=location.lower())
                        instance.cost = cost
                        instance.days = days
                        instance.name = name
                        instance.save()
                        return Response({'data update'}, status=status.HTTP_201_CREATED)
                    else:
                        print('creating new row')
                        DeliveryOptions.objects.create(product=product, name=name, name_id=name_id, days=days,
                                                       cost=cost,
                                                       location=location.lower())
                        return Response({'created'}, status=status.HTTP_201_CREATED)
                except:
                    pass
                return Response({'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response('Invalid API Key ', status=status.HTTP_400_BAD_REQUEST)
