from django.db import models
from django.contrib.auth.models import User
import uuid


def generar_code():
    return uuid.uuid4().hex

class Productos(models.Model):
    CATEGORIAS = (
        ("Juguetes para niños","Juguetes"),
        ("Decoración general","Decoración"),
        ("Piezas de repuesto","Repuestos"),
        ("Juegos de mesa","Juegos"),
        ("Pokemones de uso carios","Pokemon"),
    )

    code = models.CharField(max_length=32, unique=True, default=generar_code)
    titulo = models.CharField(max_length=50)
    foto = models.CharField(max_length=500)
    descripcion = models.CharField(max_length=300)
    precio = models.FloatField(default=0.00)
    sku = models.CharField(max_length=20)
    fecha_alta = models.DateField(auto_now_add=True)
    categoria =models.CharField(choices=CATEGORIAS, max_length=50)
    stock = models.IntegerField(default=0)
    def __str__(self):
        return f"titulo:{self.titulo} - Descripcion:{self.descripcion} - Precio:{self.precio} - Categoria:{self.categoria}"


class Orden(models.Model):
    codigo = models.CharField(max_length=32, unique=True, default=generar_code)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.FloatField(default=0.0)
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='ordenes')

    def __str__(self):
        return f"Orden {self.codigo} — ${self.total}"


class OrdenItem(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Productos, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.FloatField()

    def subtotal(self):
        return self.cantidad * self.precio_unitario


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    historial_activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class HistorialVisita(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='historial')
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE, related_name='visitas')
    fecha = models.DateTimeField(auto_now=True)

    class Meta:
        # Un registro por usuario+producto; se actualiza la fecha en cada visita
        unique_together = ('usuario', 'producto')
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario.username} → {self.producto.titulo}"