from django.urls import path

from cart import views

app_name = 'cart'

urlpatterns = [
    path('order-summary/<str:cost>', views.order_details, name='order_summary'),
    path('add-to-cart/<int:prod_id>/', views.add_to_cart, name='add_to_cart'),
    path('delete-from-cart/<int:item_id>/', views.delete_from_cart, name='delete_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('get_user_details/', views.get_user_details, name='get_user_details'),
    path('update_transaction_records/', views.update_transaction_records, name='update'),
    path('qtyupdate/', views.qtyupdate, name='qtyupate'),
    path('payment/', views.make_payment, name='make_payment'),
    path('get_logs/', views.get_logs, name='get_logs'),
]
