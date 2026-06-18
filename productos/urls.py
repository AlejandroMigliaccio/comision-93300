from django.urls import path
from productos.views import home, ver_producto

urlpatterns = [
    path("", home, name="home"),
    path("ver/<str:code>/", ver_producto, name="ver_producto"),
]