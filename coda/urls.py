from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_new_acc', views.add_new_acc_to_coda, name='add_new_acc'),
]