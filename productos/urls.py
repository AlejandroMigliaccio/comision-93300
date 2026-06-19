from django.urls import path
from productos.views import (
    home, ver_producto,
    agregar_al_carrito, ver_carrito,
    actualizar_cantidad, eliminar_del_carrito,
    checkout, orden_confirmada,
)

urlpatterns = [
    path("", home, name="home"),
    path("ver/<str:code>/", ver_producto, name="ver_producto"),
    path("carrito/", ver_carrito, name="ver_carrito"),
    path("carrito/agregar/<str:code>/", agregar_al_carrito, name="agregar_al_carrito"),
    path("carrito/actualizar/<str:code>/", actualizar_cantidad, name="actualizar_cantidad"),
    path("carrito/eliminar/<str:code>/", eliminar_del_carrito, name="eliminar_del_carrito"),
    path("carrito/checkout/", checkout, name="checkout"),
    path("orden/<str:codigo>/", orden_confirmada, name="orden_confirmada"),
]