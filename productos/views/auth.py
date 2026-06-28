# auth.py — Vistas de autenticación: registro, inicio y cierre de sesión.
# Usa los formularios integrados de Django (UserCreationForm, AuthenticationForm),
# que se traducen automáticamente al español gracias a LANGUAGE_CODE = 'es'.

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


def registro(request):
    # Crea una nueva cuenta de usuario.
    # Si el formulario es válido, inicia sesión automáticamente y redirige al inicio.
    # Si el usuario ya tiene sesión activa, redirige al inicio sin mostrar el formulario.
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
    return render(request, 'productos/auth/registro.html', {'form': form})


def login_view(request):
    # Inicia sesión con usuario y contraseña.
    # Si venía de una página protegida (?next=...), redirige allí después de autenticarse.
    # Si ya tiene sesión, redirige al inicio directamente.
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
    return render(request, 'productos/auth/login.html', {'form': form})


def logout_view(request):
    # Cierra la sesión del usuario y redirige al inicio.
    # Solo acepta POST para evitar que un link externo pueda cerrar la sesión (protección CSRF).
    if request.method == 'POST':
        logout(request)
    return redirect('home')
