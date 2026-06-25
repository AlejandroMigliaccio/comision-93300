# Helpers de Django: render (renderiza template), get_object_or_404 (busca o devuelve 404), redirect (redirige)
from django.shortcuts import render, get_object_or_404, redirect
# Funciones de autenticación: login (inicia sesión), logout (cierra sesión), authenticate (verifica credenciales)
from django.contrib.auth import login, logout, authenticate
# Formularios de auth integrados de Django (traducidos al español por LANGUAGE_CODE = 'es')
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# Decoradores de acceso: login_required (solo usuarios autenticados), user_passes_test (condición personalizada)
from django.contrib.auth.decorators import login_required, user_passes_test
# reverse: convierte nombre de URL en su ruta real (ej: 'login' → '/login/')
from django.urls import reverse
# Sum: suma valores de un campo en múltiples filas; Value: valor constante para anotaciones
from django.db.models import Sum, Value
# Coalesce: reemplaza NULL por un valor alternativo (aquí convierte NULL en 0 para productos sin ventas)
from django.db.models.functions import Coalesce
from productos.models import Productos, Orden, OrdenItem, HistorialVisita, PerfilUsuario
from productos.forms import ProductoForm

# Decorador reutilizable: restringe la vista a usuarios con is_staff=True; redirige al inicio si no cumple
staff_required = user_passes_test(lambda u: u.is_staff, login_url='home')


def _cart_count(request):
    # Lee el carrito guardado en la sesión; si no existe usa un dict vacío
    carrito = request.session.get('carrito', {})
    # Suma las cantidades de todos los productos y devuelve el total de ítems
    return sum(datos['cantidad'] for datos in carrito.values())


def home(request):
    # Lee los parámetros GET: categoría para filtrar, q para búsqueda, orden para ordenamiento
    categoria_seleccionada = request.GET.get('categoria', '')
    busqueda = request.GET.get('q', '').strip()
    orden = request.GET.get('orden', '')

    list_productos = Productos.objects.all()

    # Filtro por categoría: si viene ?categoria=X, muestra solo esa categoría
    if categoria_seleccionada:
        list_productos = list_productos.filter(categoria=categoria_seleccionada)

    # Búsqueda por título: filtra productos cuyo nombre contenga el texto (sin distinguir mayúsculas)
    if busqueda:
        list_productos = list_productos.filter(titulo__icontains=busqueda)

    # Ordenamiento: se aplica después de los filtros y es acumulable con ellos
    if orden == 'mas_vendidos':
        # Anota cada producto con el total de unidades vendidas en todas las órdenes;
        # Coalesce convierte NULL (sin ventas) en 0 para que no queden excluidos
        list_productos = list_productos.annotate(
            total_vendido=Coalesce(Sum('ordenitem__cantidad'), Value(0))
        ).order_by('-total_vendido')
    elif orden == 'disponibles':
        # Muestra solo productos con stock mayor a 0
        list_productos = list_productos.filter(stock__gt=0)
    elif orden == 'precio_asc':
        list_productos = list_productos.order_by('precio')
    elif orden == 'precio_desc':
        list_productos = list_productos.order_by('-precio')

    # Historial reciente para mostrar al pie de la página (solo usuarios autenticados con historial activo)
    visitas_recientes = []
    historial_activo = False
    if request.user.is_authenticated:
        perfil = _perfil(request.user)
        historial_activo = perfil.historial_activo
        if historial_activo:
            visitas_recientes = (
                request.user.historial
                .select_related('producto')
                .order_by('-fecha')[:8]
            )

    return render(request, "productos/productos.html", {
        "lista_productos": list_productos,
        "categorias": Productos.CATEGORIAS,
        "categoria_seleccionada": categoria_seleccionada,
        "busqueda": busqueda,
        "orden": orden,
        "cart_count": _cart_count(request),
        "visitas_recientes": visitas_recientes,
        "historial_activo": historial_activo,
    })


def _perfil(user):
    # get_or_create garantiza que todo usuario tenga un perfil sin necesidad de crearlo manualmente
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user)
    return perfil


def ver_producto(request, code):
    # Busca el producto por su código único; devuelve 404 si no existe
    producto = get_object_or_404(Productos, code=code)
    # Registra la visita solo si el usuario está autenticado y tiene el historial activo
    if request.user.is_authenticated and _perfil(request.user).historial_activo:
        HistorialVisita.objects.update_or_create(
            usuario=request.user,
            producto=producto,
        )
    return render(request, "productos/producto.html", {
        "producto": producto,
        "cart_count": _cart_count(request),
    })


@login_required
def toggle_historial(request):
    # Invierte la preferencia del usuario: activo → desactivado y viceversa
    if request.method == 'POST':
        perfil = _perfil(request.user)
        perfil.historial_activo = not perfil.historial_activo
        perfil.save()
        # Al desactivar, elimina el historial existente para no conservar datos no deseados
        if not perfil.historial_activo:
            request.user.historial.all().delete()
    return redirect(request.POST.get('next', 'home'))


@login_required
def borrar_historial(request):
    # Elimina todos los registros de visitas del usuario sin cambiar la preferencia de seguimiento
    if request.method == 'POST':
        request.user.historial.all().delete()
    return redirect(request.POST.get('next', 'home'))


@login_required
def historial(request):
    # Trae las últimas 30 visitas del usuario ordenadas por fecha descendente
    visitas = (
        request.user.historial
        .select_related('producto')
        .order_by('-fecha')[:30]
    )
    return render(request, 'productos/historial.html', {
        'visitas': visitas,
        'cart_count': _cart_count(request),
    })


def agregar_al_carrito(request, code):
    # Solo acepta POST; cualquier GET redirige al inicio
    if request.method != 'POST':
        return redirect('home')
    # Requiere sesión iniciada: redirige al login con ?next apuntando al producto
    # para que después de autenticarse el usuario vuelva directamente a ese producto
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={reverse('ver_producto', args=[code])}")
    producto = get_object_or_404(Productos, code=code)
    # Si no hay stock disponible, redirige sin modificar el carrito
    if producto.stock <= 0:
        next_url = request.POST.get('next', 'ver_carrito')
        return redirect('home' if next_url == 'home' else 'ver_carrito')
    carrito = request.session.get('carrito', {})
    if code in carrito:
        # El producto ya está en el carrito: incrementa la cantidad en 1
        carrito[code]['cantidad'] += 1
    else:
        # Primera vez que se agrega: crea la entrada con cantidad 1
        carrito[code] = {
            'titulo': producto.titulo,
            'precio': producto.precio,
            'foto': producto.foto,
            'cantidad': 1,
        }
    request.session['carrito'] = carrito
    # El parámetro 'next' del formulario indica si volver a home o al carrito
    next_url = request.POST.get('next', 'ver_carrito')
    return redirect('home' if next_url == 'home' else 'ver_carrito')


def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    items = []
    total = 0.0
    for code, datos in carrito.items():
        subtotal = datos['precio'] * datos['cantidad']
        total += subtotal
        # Enriquece cada ítem con su subtotal para mostrarlo en el template
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
            # Si el valor recibido no es un número válido, usa 1 como fallback
            cantidad = 1
        if code in carrito:
            if cantidad > 0:
                carrito[code]['cantidad'] = cantidad
            else:
                # Cantidad 0 o negativa equivale a eliminar el producto del carrito
                del carrito[code]
            request.session['carrito'] = carrito
    return redirect('ver_carrito')


def eliminar_del_carrito(request, code):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        # pop con default None evita KeyError si el código no existe
        carrito.pop(code, None)
        request.session['carrito'] = carrito
    return redirect('ver_carrito')


@login_required
def checkout(request):
    # Solo acepta POST; GET redirige al carrito
    if request.method != 'POST':
        return redirect('ver_carrito')
    carrito = request.session.get('carrito', {})
    # Carrito vacío: no hay nada que procesar
    if not carrito:
        return redirect('ver_carrito')
    total = sum(d['precio'] * d['cantidad'] for d in carrito.values())
    # Crea la orden asociada al usuario autenticado
    orden = Orden.objects.create(total=total, usuario=request.user)
    for code, datos in carrito.items():
        producto = get_object_or_404(Productos, code=code)
        cantidad = datos['cantidad']
        # Registra cada ítem de la orden con su precio al momento de la compra
        OrdenItem.objects.create(
            orden=orden,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=datos['precio'],
        )
        # Descuenta el stock; max(0, ...) evita valores negativos ante posible concurrencia
        producto.stock = max(0, producto.stock - cantidad)
        producto.save()
    # Vacía el carrito de la sesión una vez confirmada la compra
    del request.session['carrito']
    return redirect('orden_confirmada', codigo=orden.codigo)


def orden_confirmada(request, codigo):
    # Busca la orden por su código único; devuelve 404 si no existe
    orden = get_object_or_404(Orden, codigo=codigo)
    return render(request, 'productos/confirmacion.html', {
        'orden': orden,
        'cart_count': 0,    # el carrito se vació en el checkout; el badge muestra 0
    })


@staff_required
def staff_panel(request):
    # Lista todos los productos ordenados por categoría y título para facilitar la navegación
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
    # instance=producto pre-carga el formulario con los datos actuales del producto
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
        'producto': producto,       # se usa en el template para mostrar la imagen actual
        'cart_count': _cart_count(request),
    })


@login_required
def mis_compras(request):
    # prefetch_related evita N+1 queries al acceder a items y sus productos en el template
    ordenes = request.user.ordenes.prefetch_related('items__producto').order_by('-fecha')
    return render(request, 'productos/mis_compras.html', {
        'ordenes': ordenes,
        'cart_count': _cart_count(request),
    })


def registro(request):
    # Si ya tiene sesión, no tiene sentido mostrar el formulario de registro
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Inicia sesión automáticamente después de registrarse
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'productos/registro.html', {'form': form})


def login_view(request):
    # Si ya tiene sesión, redirige al inicio directamente
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Si venía de una página protegida (?next=...), vuelve a ella; si no, va al inicio
            return redirect(request.GET.get('next', 'home'))
    else:
        form = AuthenticationForm()
    return render(request, 'productos/login.html', {'form': form})


def logout_view(request):
    # Solo acepta POST para evitar que un link externo cierre la sesión del usuario (CSRF)
    if request.method == 'POST':
        logout(request)
    return redirect('home')
