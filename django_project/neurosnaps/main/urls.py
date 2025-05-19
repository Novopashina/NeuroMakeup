from django.urls import path
from .import views

urlpatterns = [
    path('', views.images_upload_view, name='home'),
]