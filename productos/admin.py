from django.contrib import admin
from productos.models import Productos, Orden, OrdenItem


@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ("titulo", "descripcion", "precio")
    list_display_links = ("titulo",)
    search_fields = ("sku", "categoria")
    list_filter = ("fecha_alta",)
    ordering = ("categoria",)


class OrdenItemInline(admin.TabularInline):
    model = OrdenItem
    extra = 0
    readonly_fields = ("subtotal",)
    fields = ("producto", "cantidad", "precio_unitario", "subtotal")


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ("codigo", "fecha", "total")
    list_display_links = ("codigo",)
    readonly_fields = ("codigo", "fecha", "total")
    ordering = ("-fecha",)
    inlines = [OrdenItemInline]