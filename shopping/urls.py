from django.conf.urls import url
from django.urls import path, include
from shopping import views

app_name = 'shopping'

urlpatterns = [
    path('home/', views.list_categories, name='home'),
    path('home/<int:pk>/', views.itemsview, name='items'),
    path('home/<int:ck>/<int:pk>/', views.itemdetailview, name='specificitem'),
    url(r'^review/(?P<categ>\w+)/(?P<product>\w+)/$', views.reviewtext, name='review'),

    path('product_list/', views.productList, name='product_list'),
    path('delivery_bid/', views.bidding, name='delivery_bid'),
    path('categories_list/', views.categoriesList, name='categories_list'),
]
