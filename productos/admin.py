from django.contrib import admin
from productos.models import Productos

#admin.site.register(Productos)

@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ("titulo","descripcion","precio")

    list_display_links = ("titulo",)

    search_fields= ("sku", "categoria")

    list_filter = ("fecha_alta",)

    ordering = ("categoria",)
