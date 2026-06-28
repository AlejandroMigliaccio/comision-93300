# carrito.py — Vistas del carrito de compras.
# El carrito se guarda en la sesión del usuario como un diccionario {code: {datos}}.

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from productos.models import Productos
from .helpers import _cart_count


def agregar_al_carrito(request, code):
    # Agrega un producto al carrito o incrementa su cantidad si ya existe.
    # Solo acepta POST. Si el usuario no está autenticado, lo redirige al login
    # con ?next apuntando al producto para que vuelva después de iniciar sesión.
    if request.method != 'POST':
        return redirect('home')
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={reverse('ver_producto', args=[code])}")
    producto = get_object_or_404(Productos, code=code)
    # Si no hay stock, redirige sin modificar el carrito
    if producto.stock <= 0:
        next_url = request.POST.get('next', 'ver_carrito')
        return redirect('home' if next_url == 'home' else 'ver_carrito')
    carrito = request.session.get('carrito', {})
    if code in carrito:
        carrito[code]['cantidad'] += 1
    else:
        carrito[code] = {
            'titulo': producto.titulo,
            'precio': producto.precio,
            'foto': producto.foto,
            'cantidad': 1,
        }
    request.session['carrito'] = carrito
    next_url = request.POST.get('next', 'ver_carrito')
    return redirect('home' if next_url == 'home' else 'ver_carrito')


def ver_carrito(request):
    # Muestra el contenido del carrito con subtotales por producto y total general.
    # Lee la sesión y construye una lista de ítems enriquecida con el subtotal.
    carrito = request.session.get('carrito', {})
    items = []
    total = 0.0
    for code, datos in carrito.items():
        subtotal = datos['precio'] * datos['cantidad']
        total += subtotal
        items.append({
            'code': code,
            'titulo': datos['titulo'],
            'precio': datos['precio'],
            'foto': datos['foto'],
            'cantidad': datos['cantidad'],
            'subtotal': subtotal,
        })
    return render(request, 'productos/carrito/carrito.html', {
        'items': items,
        'total': total,
        'cart_count': _cart_count(request),
    })


def actualizar_cantidad(request, code):
    # Modifica la cantidad de un producto en el carrito.
    # Si la cantidad enviada es 0 o negativa, elimina el producto del carrito.
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except ValueError:
            cantidad = 1
        if code in carrito:
            if cantidad > 0:
                carrito[code]['cantidad'] = cantidad
            else:
                del carrito[code]
            request.session['carrito'] = carrito
    return redirect('ver_carrito')


def eliminar_del_carrito(request, code):
    # Elimina un producto del carrito usando pop() con default None
    # para evitar un KeyError si el código ya no existe en la sesión.
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        carrito.pop(code, None)
        request.session['carrito'] = carrito
    return redirect('ver_carrito')
