# __init__.py — Re-exporta todas las vistas del paquete.
# Esto permite que urls.py importe desde 'productos.views' sin cambios,
# aunque las vistas estén distribuidas en archivos separados.

from .catalogo import landing, home, ver_producto, pokedex
from .carrito import agregar_al_carrito, ver_carrito, actualizar_cantidad, eliminar_del_carrito
from .pedidos import checkout, orden_confirmada, ticket_orden, mis_compras
from .historial import historial, toggle_historial, borrar_historial
from .staff import staff_panel, staff_agregar, staff_editar
from .auth import registro, login_view, logout_view
