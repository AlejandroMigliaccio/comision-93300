# helpers.py — Utilidades compartidas por todas las vistas.
# Contiene el decorador de acceso staff, el contador del carrito y el helper de perfil.

from django.contrib.auth.decorators import user_passes_test
from productos.models import PerfilUsuario

# Decorador reutilizable: restringe el acceso a usuarios con is_staff=True.
# Si el usuario no cumple la condición, lo redirige al inicio (login_url='home').
staff_required = user_passes_test(lambda u: u.is_staff, login_url='home')


def _cart_count(request):
    # Lee el carrito guardado en la sesión y devuelve la cantidad total de ítems.
    # Se usa en todas las vistas para mostrar el badge del carrito en el header.
    carrito = request.session.get('carrito', {})
    return sum(datos['cantidad'] for datos in carrito.values())


def _perfil(user):
    # Devuelve el PerfilUsuario asociado al usuario.
    # get_or_create garantiza que exista un perfil aunque no se haya creado explícitamente.
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user)
    return perfil
