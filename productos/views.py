from django.shortcuts import render, get_object_or_404, redirect
from productos.models import Productos, Orden, OrdenItem


def _cart_count(request):
    carrito = request.session.get('carrito', {})
    return sum(datos['cantidad'] for datos in carrito.values())


def home(request):
    list_productos = Productos.objects.all()
    return render(request, "productos/productos.html", {
        "lista_productos": list_productos,
        "cart_count": _cart_count(request),
    })


def ver_producto(request, code):
    producto = get_object_or_404(Productos, code=code)
    return render(request, "productos/producto.html", {
        "producto": producto,
        "cart_count": _cart_count(request),
    })


def agregar_al_carrito(request, code):
    if request.method != 'POST':
        return redirect('home')
    producto = get_object_or_404(Productos, code=code)
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
    if next_url == 'home':
        return redirect('home')
    return redirect('ver_carrito')


def ver_carrito(request):
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
    return render(request, 'productos/carrito.html', {
        'items': items,
        'total': total,
        'cart_count': _cart_count(request),
    })


def actualizar_cantidad(request, code):
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
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        carrito.pop(code, None)
        request.session['carrito'] = carrito
    return redirect('ver_carrito')


def checkout(request):
    if request.method != 'POST':
        return redirect('ver_carrito')
    carrito = request.session.get('carrito', {})
    if not carrito:
        return redirect('ver_carrito')
    total = sum(d['precio'] * d['cantidad'] for d in carrito.values())
    orden = Orden.objects.create(total=total)
    for code, datos in carrito.items():
        producto = get_object_or_404(Productos, code=code)
        OrdenItem.objects.create(
            orden=orden,
            producto=producto,
            cantidad=datos['cantidad'],
            precio_unitario=datos['precio'],
        )
    del request.session['carrito']
    return redirect('orden_confirmada', codigo=orden.codigo)


def orden_confirmada(request, codigo):
    orden = get_object_or_404(Orden, codigo=codigo)
    return render(request, 'productos/confirmacion.html', {
        'orden': orden,
        'cart_count': 0,
    })
