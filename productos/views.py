from django.shortcuts import render, get_object_or_404
from productos.models import Productos

def home(request):
    list_productos = Productos.objects.all()
    contexto = {
        "lista_productos": list_productos
    }
    return render(request, "productos/productos.html", contexto)

def ver_producto(request, code):
    producto = get_object_or_404(Productos, code=code)
    contexto = {
        "producto": producto
    }
    return render(request, "productos/producto.html", contexto)
