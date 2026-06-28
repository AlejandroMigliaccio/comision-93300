# historial.py — Vistas del historial de visitas de productos.
# Permite ver, activar/desactivar y borrar el registro de productos visitados.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .helpers import _cart_count, _perfil


@login_required
def historial(request):
    # Muestra las últimas 30 visitas del usuario con detalle de cada producto.
    # select_related('producto') carga el producto en la misma query para evitar N+1.
    visitas = (
        request.user.historial
        .select_related('producto')
        .order_by('-fecha')[:30]
    )
    return render(request, 'productos/historial/historial.html', {
        'visitas': visitas,
        'cart_count': _cart_count(request),
    })


@login_required
def toggle_historial(request):
    # Activa o desactiva el seguimiento de visitas para el usuario.
    # La preferencia se guarda en PerfilUsuario y persiste entre sesiones.
    # Al desactivar, elimina todos los registros existentes para respetar la privacidad.
    if request.method == 'POST':
        perfil = _perfil(request.user)
        perfil.historial_activo = not perfil.historial_activo
        perfil.save()
        if not perfil.historial_activo:
            request.user.historial.all().delete()
    return redirect(request.POST.get('next', 'home'))


@login_required
def borrar_historial(request):
    # Elimina todos los registros de visitas del usuario sin cambiar la preferencia.
    # El usuario puede volver a acumular historial si el seguimiento sigue activo.
    if request.method == 'POST':
        request.user.historial.all().delete()
    return redirect(request.POST.get('next', 'home'))
