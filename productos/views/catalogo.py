# catalogo.py — Vistas del catálogo de productos.
# Maneja la página principal con filtros, el detalle de un producto y la Pokédex.

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from productos.models import Productos, HistorialVisita
from .helpers import _cart_count, _perfil


def landing(request):
    return render(request, 'productos/catalogo/index.html', {
        'cart_count': _cart_count(request),
        'total_productos': Productos.objects.count(),
    })


def home(request):
    # Página principal: muestra el catálogo completo con filtros opcionales.
    # Acepta los parámetros GET: ?categoria=, ?q= (búsqueda) y ?orden=.
    categoria_seleccionada = request.GET.get('categoria', '')
    busqueda = request.GET.get('q', '').strip()
    orden = request.GET.get('orden', '')

    list_productos = Productos.objects.all()

    # Filtra por categoría si viene el parámetro
    if categoria_seleccionada:
        list_productos = list_productos.filter(categoria=categoria_seleccionada)

    # Búsqueda por título (sin distinguir mayúsculas)
    if busqueda:
        list_productos = list_productos.filter(titulo__icontains=busqueda)

    # Aplica el ordenamiento seleccionado (acumulable con los filtros anteriores)
    if orden == 'mas_vendidos':
        # Coalesce convierte NULL (productos sin ventas) en 0 para no excluirlos
        list_productos = list_productos.annotate(
            total_vendido=Coalesce(Sum('ordenitem__cantidad'), Value(0))
        ).order_by('-total_vendido')
    elif orden == 'disponibles':
        list_productos = list_productos.filter(stock__gt=0)
    elif orden == 'precio_asc':
        list_productos = list_productos.order_by('precio')
    elif orden == 'precio_desc':
        list_productos = list_productos.order_by('-precio')

    # Historial reciente: últimas 8 visitas para mostrar al pie de la página
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

    return render(request, 'productos/catalogo/productos.html', {
        'lista_productos': list_productos,
        'categorias': Productos.CATEGORIAS,
        'categoria_seleccionada': categoria_seleccionada,
        'busqueda': busqueda,
        'orden': orden,
        'cart_count': _cart_count(request),
        'visitas_recientes': visitas_recientes,
        'historial_activo': historial_activo,
    })


def ver_producto(request, code):
    # Muestra el detalle de un producto identificado por su código único.
    # Si el usuario tiene el historial activo, registra la visita con update_or_create
    # para no duplicar registros (visitar el mismo producto actualiza la fecha).
    producto = get_object_or_404(Productos, code=code)
    if request.user.is_authenticated and _perfil(request.user).historial_activo:
        HistorialVisita.objects.update_or_create(
            usuario=request.user,
            producto=producto,
        )
    return render(request, 'productos/catalogo/producto.html', {
        'producto': producto,
        'cart_count': _cart_count(request),
    })


def pokedex(request):
    # Renderiza la Pokédex interactiva que carga datos desde la PokéAPI via JavaScript.
    return render(request, 'productos/catalogo/pokedex.html')
