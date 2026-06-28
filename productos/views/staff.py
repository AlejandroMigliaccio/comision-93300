# staff.py — Vistas del panel de administración para usuarios staff.
# Permite listar, agregar y editar productos desde la interfaz web (sin usar el admin de Django).
# Todas las vistas están protegidas por el decorador @staff_required.

from django.shortcuts import render, get_object_or_404, redirect
from productos.models import Productos
from productos.forms import ProductoForm
from .helpers import _cart_count, staff_required


@staff_required
def staff_panel(request):
    # Lista todos los productos ordenados por categoría y título.
    # El template resalta el estado del stock con colores (verde/amarillo/rojo).
    productos = Productos.objects.all().order_by('categoria', 'titulo')
    return render(request, 'productos/staff/staff_panel.html', {
        'productos': productos,
        'cart_count': _cart_count(request),
    })


@staff_required
def staff_agregar(request):
    # Muestra y procesa el formulario para crear un nuevo producto.
    # En GET muestra el formulario vacío; en POST valida y guarda si es válido.
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_panel')
    else:
        form = ProductoForm()
    return render(request, 'productos/staff/staff_form.html', {
        'form': form,
        'titulo_pagina': 'Agregar producto',
        'cart_count': _cart_count(request),
    })


@staff_required
def staff_editar(request, code):
    # Muestra y procesa el formulario de edición de un producto existente.
    # instance=producto pre-carga el formulario con los valores actuales del producto.
    producto = get_object_or_404(Productos, code=code)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('staff_panel')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/staff/staff_form.html', {
        'form': form,
        'titulo_pagina': f'Editar: {producto.titulo}',
        'producto': producto,  # se usa en el template para mostrar la imagen actual
        'cart_count': _cart_count(request),
    })
