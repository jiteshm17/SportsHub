from django.urls import path
from . import views
app_name = 'payment'

urlpatterns = [
    path('process/', views.payment_process, name='process'),
    path('notify/', views.show_me_the_money, name='notify'),
    path('done/', views.payment_done, name='done'),
    path('cancelled/', views.payment_canceled, name='canceled'),
    path('you_orders/',views.your_orders,name='show_orders')
]