# Importa helpers de Django para renderizar templates, buscar objetos y redirigir
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from productos.models import Productos, Orden, OrdenItem
from productos.forms import ProductoForm

staff_required = user_passes_test(lambda u: u.is_staff, login_url='home')


def _cart_count(request):
    # Lee el carrito guardado en la sesión; si no existe usa un dict vacío
    carrito = request.session.get('carrito', {})
    # Suma la cantidad de cada producto y devuelve el total de ítems
    return sum(datos['cantidad'] for datos in carrito.values())


def home(request):
    categoria_seleccionada = request.GET.get('categoria', '')
    busqueda = request.GET.get('q', '').strip()
    orden = request.GET.get('orden', '')

    list_productos = Productos.objects.all()

    if categoria_seleccionada:
        list_productos = list_productos.filter(categoria=categoria_seleccionada)
    if busqueda:
        list_productos = list_productos.filter(titulo__icontains=busqueda)

    if orden == 'mas_vendidos':
        list_productos = list_productos.annotate(
            total_vendido=Coalesce(Sum('ordenitem__cantidad'), Value(0))
        ).order_by('-total_vendido')
    elif orden == 'disponibles':
        list_productos = list_productos.filter(stock__gt=0)
    elif orden == 'precio_asc':
        list_productos = list_productos.order_by('precio')
    elif orden == 'precio_desc':
        list_productos = list_productos.order_by('-precio')

    return render(request, "productos/productos.html", {
        "lista_productos": list_productos,
        "categorias": Productos.CATEGORIAS,
        "categoria_seleccionada": categoria_seleccionada,
        "busqueda": busqueda,
        "orden": orden,
        "cart_count": _cart_count(request),
    })


def ver_producto(request, code):
    # Busca el producto por su código; si no existe devuelve error 404
    producto = get_object_or_404(Productos, code=code)
    return render(request, "productos/producto.html", {
        "producto": producto,               # datos del producto al template
        "cart_count": _cart_count(request), # badge del carrito
    })


def agregar_al_carrito(request, code):
    # Solo acepta POST; si alguien entra por GET lo manda al inicio
    if request.method != 'POST':
        return redirect('home')
    if not request.user.is_authenticated:
        # Redirige al login con next apuntando al producto para volver tras autenticarse
        return redirect(f"{reverse('login')}?next={reverse('ver_producto', args=[code])}")
    # Busca el producto por código o devuelve 404
    producto = get_object_or_404(Productos, code=code)
    if producto.stock <= 0:
        # Si no hay stock, redirige sin agregar nada
        next_url = request.POST.get('next', 'ver_carrito')
        return redirect('home' if next_url == 'home' else 'ver_carrito')
    # Lee el carrito actual de la sesión
    carrito = request.session.get('carrito', {})
    if code in carrito:
        # Si el producto ya está en el carrito, incrementa su cantidad
        carrito[code]['cantidad'] += 1
    else:
        # Si es nuevo, lo agrega con cantidad 1
        carrito[code] = {
            'titulo': producto.titulo,
            'precio': producto.precio,
            'foto': producto.foto,
            'cantidad': 1,
        }
    # Guarda el carrito actualizado en la sesión
    request.session['carrito'] = carrito
    # Lee hacia dónde redirigir después (parámetro 'next' del formulario)
    next_url = request.POST.get('next', 'ver_carrito')
    if next_url == 'home':
        return redirect('home')
    return redirect('ver_carrito')


def ver_carrito(request):
    # Lee el carrito de la sesión
    carrito = request.session.get('carrito', {})
    items = []
    total = 0.0
    for code, datos in carrito.items():
        # Calcula precio × cantidad para ese producto
        subtotal = datos['precio'] * datos['cantidad']
        # Acumula al total general
        total += subtotal
        # Agrega el ítem enriquecido con subtotal a la lista
        items.append({
            'code': code,
            'titulo': datos['titulo'],
            'precio': datos['precio'],
            'foto': datos['foto'],
            'cantidad': datos['cantidad'],
            'subtotal': subtotal,
        })
    return render(request, 'productos/carrito.html', {
        'items': items,                     # lista de productos con subtotales
        'total': total,                     # total del carrito
        'cart_count': _cart_count(request),
    })


def actualizar_cantidad(request, code):
    if request.method == 'POST':
        # Lee el carrito de la sesión
        carrito = request.session.get('carrito', {})
        try:
            # Convierte el valor del formulario a entero
            cantidad = int(request.POST.get('cantidad', 1))
        except ValueError:
            # Si el valor no es número, usa 1 como fallback
            cantidad = 1
        if code in carrito:
            if cantidad > 0:
                # Actualiza la cantidad del producto
                carrito[code]['cantidad'] = cantidad
            else:
                # Si la cantidad es 0 o negativa, elimina el producto del carrito
                del carrito[code]
            # Guarda los cambios en la sesión
            request.session['carrito'] = carrito
    return redirect('ver_carrito')


def eliminar_del_carrito(request, code):
    if request.method == 'POST':
        # Lee el carrito de la sesión
        carrito = request.session.get('carrito', {})
        # Elimina el producto del dict; si no existe no hace nada (None evita KeyError)
        carrito.pop(code, None)
        # Guarda el carrito sin ese producto
        request.session['carrito'] = carrito
    return redirect('ver_carrito')


@login_required
def checkout(request):
    # Solo acepta POST
    if request.method != 'POST':
        return redirect('ver_carrito')
    # Lee el carrito de la sesión
    carrito = request.session.get('carrito', {})
    if not carrito:
        # Si el carrito está vacío, redirige sin procesar
        return redirect('ver_carrito')
    # Calcula el total de la orden
    total = sum(d['precio'] * d['cantidad'] for d in carrito.values())
    # Crea el registro de la orden en la base de datos
    orden = Orden.objects.create(total=total, usuario=request.user)
    for code, datos in carrito.items():
        producto = get_object_or_404(Productos, code=code)
        cantidad = datos['cantidad']
        OrdenItem.objects.create(
            orden=orden,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=datos['precio'],
        )
        # Descuenta el stock; nunca baja de 0 por si hubo concurrencia
        producto.stock = max(0, producto.stock - cantidad)
        producto.save()
    # Vacía el carrito de la sesión una vez confirmada la orden
    del request.session['carrito']
    # Redirige a la página de confirmación con el código de la orden
    return redirect('orden_confirmada', codigo=orden.codigo)


def orden_confirmada(request, codigo):
    # Busca la orden por su código único; devuelve 404 si no existe
    orden = get_object_or_404(Orden, codigo=codigo)
    return render(request, 'productos/confirmacion.html', {
        'orden': orden,     # datos de la orden al template
        'cart_count': 0,    # el carrito ya se vació, muestra 0 en el badge
    })


@staff_required
def staff_panel(request):
    productos = Productos.objects.all().order_by('categoria', 'titulo')
    return render(request, 'productos/staff_panel.html', {
        'productos': productos,
        'cart_count': _cart_count(request),
    })


@staff_required
def staff_agregar(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_panel')
    else:
        form = ProductoForm()
    return render(request, 'productos/staff_form.html', {
        'form': form,
        'titulo_pagina': 'Agregar producto',
        'cart_count': _cart_count(request),
    })


@staff_required
def staff_editar(request, code):
    producto = get_object_or_404(Productos, code=code)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('staff_panel')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/staff_form.html', {
        'form': form,
        'titulo_pagina': f'Editar: {producto.titulo}',
        'producto': producto,
        'cart_count': _cart_count(request),
    })


@login_required
def mis_compras(request):
    ordenes = request.user.ordenes.prefetch_related('items__producto').order_by('-fecha')
    return render(request, 'productos/mis_compras.html', {
        'ordenes': ordenes,
        'cart_count': _cart_count(request),
    })


def registro(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'productos/registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
    else:
        form = AuthenticationForm()
    return render(request, 'productos/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')
