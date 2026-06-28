from django.urls import path
from productos.views import (
    home, ver_producto,
    agregar_al_carrito, ver_carrito,
    actualizar_cantidad, eliminar_del_carrito,
    checkout, orden_confirmada,
    mis_compras, historial, toggle_historial, borrar_historial,
    staff_panel, staff_agregar, staff_editar,
    registro, login_view, logout_view,
    pokedex,
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
    path("mis-compras/", mis_compras, name="mis_compras"),
    path("historial/", historial, name="historial"),
    path("historial/toggle/", toggle_historial, name="toggle_historial"),
    path("historial/borrar/", borrar_historial, name="borrar_historial"),
    path("staff/", staff_panel, name="staff_panel"),
    path("staff/agregar/", staff_agregar, name="staff_agregar"),
    path("staff/editar/<str:code>/", staff_editar, name="staff_editar"),
    path("registro/", registro, name="registro"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("pokedex/", pokedex, name="pokedex"),
]