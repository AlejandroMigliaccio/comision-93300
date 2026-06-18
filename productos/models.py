from django.db import models
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
    precio = models.FloatField(default=0.0)
    sku = models.CharField(max_length=20)
    fecha_alta = models.DateField(auto_now_add=True)
    categoria =models.CharField(choices=CATEGORIAS, max_length=50)

    def __str__(self):
        return f"titulo:{self.titulo} - Descripcion:{self.descripcion} - Precio:{self.precio} - Categoria:{self.categoria}"