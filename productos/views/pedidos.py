# pedidos.py — Vistas relacionadas con el proceso de compra y órdenes.
# Incluye el checkout, la confirmación de orden y el historial de compras del usuario.

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from productos.models import Productos, Orden, OrdenItem
from .helpers import _cart_count


@login_required
def checkout(request):
    # Procesa la compra: crea una Orden, registra cada ítem y descuenta el stock.
    # Solo acepta POST. Si el carrito está vacío, redirige sin crear nada.
    if request.method != 'POST':
        return redirect('ver_carrito')
    carrito = request.session.get('carrito', {})
    if not carrito:
        return redirect('ver_carrito')
    total = sum(d['precio'] * d['cantidad'] for d in carrito.values())
    # Crea la orden asociada al usuario autenticado
    orden = Orden.objects.create(total=total, usuario=request.user)
    for code, datos in carrito.items():
        producto = get_object_or_404(Productos, code=code)
        cantidad = datos['cantidad']
        # Guarda el precio unitario al momento de la compra para preservar el historial
        OrdenItem.objects.create(
            orden=orden,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=datos['precio'],
        )
        # max(0, ...) evita valores negativos en caso de concurrencia
        producto.stock = max(0, producto.stock - cantidad)
        producto.save()
    # Vacía el carrito de la sesión una vez confirmada la compra
    del request.session['carrito']
    return redirect('orden_confirmada', codigo=orden.codigo)


def orden_confirmada(request, codigo):
    # Muestra la pantalla de confirmación de una orden ya procesada.
    # cart_count es 0 porque el carrito se vació en el checkout.
    orden = get_object_or_404(Orden, codigo=codigo)
    return render(request, 'productos/pedidos/confirmacion.html', {
        'orden': orden,
        'cart_count': 0,
    })


@login_required
def mis_compras(request):
    # Lista todas las órdenes del usuario autenticado ordenadas por fecha descendente.
    # prefetch_related evita N+1 queries al acceder a los ítems y sus productos en el template.
    ordenes = request.user.ordenes.prefetch_related('items__producto').order_by('-fecha')
    return render(request, 'productos/pedidos/mis_compras.html', {
        'ordenes': ordenes,
        'cart_count': _cart_count(request),
    })
