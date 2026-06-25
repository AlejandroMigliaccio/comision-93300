# Borderline 3D Store

Proyecto final de la comisión 93300 — Alejandro Migliaccio.

E-commerce de productos de impresión 3D desarrollado con Django 6. Permite navegar el catálogo, gestionar un carrito de compras, registrarse, iniciar sesión y realizar pedidos. Incluye un panel de administración propio para usuarios staff.

---

## Funcionalidades

### Catálogo y búsqueda
- Listado de productos con imagen, precio, categoría y stock disponible
- Filtro por categoría desde la barra lateral
- Búsqueda por nombre de producto
- Página de detalle por producto con todos sus datos
- Ordenamiento desde el sidebar (acumulable con categoría y búsqueda):
  - 🏆 Más vendidos — por unidades totales vendidas, de mayor a menor
  - ✅ Con stock — muestra solo productos con disponibilidad
  - 💲 Precio: menor a mayor
  - 💲 Precio: mayor a menor

### Carrito de compras
- Agregar, actualizar cantidad y eliminar productos
- Resumen con subtotales y total general
- El carrito persiste en la sesión del usuario

### Autenticación
- Registro de nuevos usuarios
- Inicio y cierre de sesión
- Menú desplegable en el header con el nombre del usuario
- Acceso al historial de compras desde el menú

### Compras
- Requiere estar autenticado para agregar al carrito y hacer checkout
- Al confirmar una compra se genera una orden con código único
- El stock del producto se descuenta automáticamente al comprar
- Página de confirmación con detalle de la orden

### Historial de compras
- Cada usuario puede ver todas sus órdenes anteriores
- Se muestra código de orden, fecha, productos comprados, cantidades, precios y total

### Panel Staff (`/staff/`)
- Accesible solo para usuarios con permisos staff
- Tabla de todos los productos con estado de stock resaltado por color (verde / amarillo / rojo)
- Formulario para agregar nuevos productos
- Formulario para editar cualquier producto (título, imagen, descripción, precio, SKU, categoría, stock)
- Vista previa de imagen en tiempo real al cargar o editar

### Extras
- Banner de Instagram con link al perfil [@borderline3d](https://www.instagram.com/borderline3d/)
- UI completamente en español (labels, mensajes de validación, fechas)
- Zona horaria configurada para Argentina

---

## Tecnologías

| Herramienta | Versión |
|-------------|---------|
| Python | 3.14 |
| Django | 6.0.6 |
| Base de datos | SQLite |

---

## Instalación y uso local

### 1. Clonar el repositorio

```bash
git clone https://github.com/alejandromigliaccio/comision-93300.git
cd comision-93300
```

### 2. Crear el entorno virtual e instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 3. Aplicar migraciones

```bash
python manage.py migrate
```

### 4. Crear un superusuario (administrador)

```bash
python manage.py createsuperuser
```

### 5. Levantar el servidor de desarrollo

```bash
python manage.py runserver
```

Abrir en el navegador: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Estructura del proyecto

```
comision-93300/
├── tp_final/                  # Configuración del proyecto Django
│   ├── settings.py
│   └── urls.py
├── productos/                 # App principal
│   ├── models.py              # Modelos: Productos, Orden, OrdenItem
│   ├── views.py               # Todas las vistas (tienda, carrito, auth, staff)
│   ├── forms.py               # Formulario de producto para el panel staff
│   ├── urls.py                # Rutas de la aplicación
│   ├── admin.py               # Configuración del admin de Django
│   ├── migrations/            # Historial de migraciones
│   └── templates/productos/
│       ├── productos.html     # Página principal / catálogo
│       ├── producto.html      # Detalle de producto
│       ├── carrito.html       # Carrito de compras
│       ├── confirmacion.html  # Confirmación de compra
│       ├── mis_compras.html   # Historial de compras del usuario
│       ├── login.html         # Inicio de sesión
│       ├── registro.html      # Registro de nuevo usuario
│       ├── staff_panel.html   # Panel staff — listado de productos
│       └── staff_form.html    # Panel staff — formulario agregar/editar
├── db.sqlite3                 # Base de datos (generada al migrar)
├── manage.py
└── requirements.txt
```

---

## Rutas principales

| URL | Descripción |
|-----|-------------|
| `/` | Catálogo de productos |
| `/ver/<code>/` | Detalle de un producto |
| `/carrito/` | Ver carrito |
| `/carrito/agregar/<code>/` | Agregar producto al carrito |
| `/carrito/checkout/` | Confirmar compra |
| `/orden/<codigo>/` | Confirmación de orden |
| `/mis-compras/` | Historial de compras del usuario |
| `/login/` | Iniciar sesión |
| `/registro/` | Crear cuenta |
| `/logout/` | Cerrar sesión |
| `/staff/` | Panel staff — listado |
| `/staff/agregar/` | Panel staff — nuevo producto |
| `/staff/editar/<code>/` | Panel staff — editar producto |
| `/admin/` | Administrador de Django |

---

## Acceso al panel staff

Desde el admin de Django (`/admin/`) → **Users** → seleccionar el usuario → activar **"Staff status"**.

Una vez marcado, el usuario verá la opción **⚙ Panel Staff** en el menú desplegable del header.
