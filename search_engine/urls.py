from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_files, name='upload_files'),
    path('search/', views.search_product_by_files, name='search_product_by_files'),
    path('finish/', views.finish_search, name='finish_search'),
]
