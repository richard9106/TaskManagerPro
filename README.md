# Task Manager Pro

Un sistema profesional de gestión de tareas construido con Django, diseñado con colores corporativos azules oscuros para una experiencia de usuario moderna y elegante.

## 🚀 Características

### Funcionalidades Principales
- **Dashboard Completo**: Vista general con estadísticas y tareas recientes
- **Gestión de Tareas**: Crear, editar, eliminar y gestionar tareas
- **Asignación de Usuarios**: Asignar tareas a miembros del equipo
- **Sistema de Prioridades**: Prioridades desde baja hasta urgente
- **Fechas de Vencimiento**: Control de fechas límite con alertas de retraso
- **Sistema de Etiquetas**: Organización de tareas con tags personalizables
- **Seguimiento de Horas**: Estimación y registro de tiempo real
- **Filtrado y Búsqueda**: Buscar tareas por título, descripción o tags
- **Paginación**: Carga eficiente de grandes cantidades de tareas

### Características Técnicas
- **Interfaz Responsive**: Diseño adaptativo para móviles y escritorio
- **Admin Panel**: Panel de administración personalizado con badges de estado y prioridad
- **Autenticación**: Sistema de usuario integrado
- **Permisos**: Control de acceso basado en roles
- **Formularios Avanzados**: Validación completa y autocompletado
- **Animaciones**: Transiciones suaves y efectos visuales profesionales

## 🎨 Diseño

### Paleta de Colores Corporativos
- **Azul Primario**: `#2b6cb0` - Color principal para elementos importantes
- **Azul Oscuro**: `#1a365d` - Navbar y elementos de navegación
- **Azul Claro**: `#4299e1` - Elementos de resaltado y contraste
- **Colores de Estado**: Verde para completado, amarillo para en progreso, rojo para urgentes
- **Elementos Gráficos**: Sombras sutiles y bordes redondeados para aspecto moderno

### Diseño de Interfaz
- **Cards Profesionales**: Cada tarea se presenta en tarjetas elegantes
- **Badges de Estado**: Insignias coloridas para estados y prioridades
- **Iconografía**: Font Awesome para iconos consistentes y profesionales
- **Tipografía**: Fuentes modernas con jerarquía clara de información
- **Espaciado**: Diseño limpio con espacios apropiados entre elementos

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 4.2+**: Framework web robusto y seguro
- **Python**: Lenguaje principal de desarrollo
- **SQLite**: Base de datos para desarrollo (configurable)

### Frontend
- **Bootstrap 5**: Framework CSS para diseño responsive
- **Font Awesome**: Biblioteca de iconos profesionales
- **CSS personalizado**: Diseño corporativo único
- **JavaScript vanilla**: Interactividad moderna sin dependencias externas

### Dependencias Adicionales
- **Django REST Framework**: Para futuras APIs
- **JWT Authentication**: Autenticación segura
- **Swagger/OpenAPI**: Documentación automática de APIs

## 📁 Estructura del Proyecto

```
task_manager/
├── core/                    # Aplicación principal
│   ├── models.py           # Modelo Task con características completas
│   ├── views.py            # Vistas CRUD y dashboard
│   ├── forms.py            # Formularios avanzados
│   ├── admin.py            # Panel administrativo personalizado
│   ├── urls.py             # Rutas de la aplicación
│   └── migrations/         # Migraciones de base de datos
├── task_manager/           # Configuración del proyecto
│   ├── settings.py         # Configuración Django
│   ├── urls.py            // URL principal del proyecto
│   └── wsgi.py            # Servidor WSGI
├── templates/             # Plantillas HTML
│   ├── base.html          # Plantilla base con diseño corporativo
│   └── core/              # Plantillas específicas
│       ├── dashboard.html  # Panel principal
│       ├── task_list.html # Lista de tareas con filtros
│       ├── task_detail.html # Detalle de tarea
│       ├── task_form.html # Formulario crear/editar
│       └── task_confirm_delete.html # Confirmación de eliminación
├── static/               # Archivos estáticos
│   ├── css/
│   │   └── style.css     # Estilos corporativos personalizados
│   └── js/
│       └── main.js       # JavaScript para interactividad
├── requirements.txt      # Dependencias del proyecto
├── manage.py           # Script de gestión Django
├── Procfile           # Configuración para despliegue
└── README.md          # Este archivo
```

## 🚀 Instalación y Configuración

### 1. Clonar el Proyecto
```bash
cd task_manager
```

### 2. Crear Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate  # En Linux/Mac
# o venv\Scripts\activate  # En Windows
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 6. Ejecutar Servidor
```bash
python manage.py runserver
```

## 👥 Uso del Sistema

### Acceso
- Visita `http://localhost:8000/` para el dashboard principal
- Accede al panel de administración en `http://localhost:8000/admin/`

### Características Principales

#### Dashboard
- Estadísticas generales de tareas
- Lista de tareas recientes
- Alertas de tareas urgentes
- Acceso rápido a funciones principales

#### Gestión de Tareas
- **Crear**: Formulario completo con todos los campos
- **Ver**: Vista detallada con toda la información
- **Editar**: Modificación completa de tareas
- **Eliminar**: Confirmación de seguridad
- **Completar**: Marcado rápido de tareas terminadas

#### Filtros y Búsqueda
- Buscar por título, descripción o tags
- Filtrar por estado (pendiente, en progreso, completado, cancelado)
- Filtrar por prioridad (baja, media, alta, urgente)
- Filtrar por asignación (mias, asignadas a mí, todas)

## 🎯 Funcionalidades Avanzadas

### Sistema de Prioridades Visual
- **Verde**: Prioridad baja
- **Amarillo**: Prioridad media
- **Naranja**: Prioridad alta
- **Rojo**: Prioridad urgente

### Estados de Tareas
- **Gris**: Pendiente
- **Azul**: En progreso
- **Verde**: Completado
- **Rojo**: Cancelado

### Alertas Inteligentes
- Tareas vencidas marcadas en rojo
- Avisos prominentes en el dashboard
- Contadores de tiempo en las tareas

### Panel Administrativo
- Vista de tabla con badges visuales
- Filtros avanzados para administradores
- Edición inline de campos importantes
- Indicadores visuales de estado

## 🔧 Configuración Adicional

### Personalización del Diseño
El archivo `static/css/style.css` contiene todas las variables CSS personalizables para ajustar colores, tipografías y espaciado según las necesidades corporativas.

### Configuración de Base de Datos
Para producción, modifica `settings.py` para usar PostgreSQL, MySQL, o la base de datos de tu preferencia.

### Variables de Entorno
Considera usar django-environ para variables sensibles como SECRET_KEY en producción.

## 🚀 Despliegue

El proyecto incluye un `Procfile` para despliegue en plataformas como Heroku. También está configurado para servir archivos estáticos en desarrollo.

### Para Producción
1. Configurar variables de entorno seguras
2. Cambiar DEBUG = False
3. Configurar ALLOWED_HOSTS apropiadamente
4. Configurar base de datos de producción
5. Ejecutar collectstatic

## 📝 Notas de Desarrollo

Este sistema está diseñado para ser:
- **Escalable**: Fácil agregar nuevas funcionalidades
- **Mantenible**: Código limpio y bien documentado
- **Seguro**: Sistema de permisos robusto
- **Profesional**: Diseño corporativo moderno

## 🎨 Palette de Colores Utilizada

```css
:root {
    --primary-dark: #1a365d;     /* Azul muy oscuro para navbar */
    --primary-blue: #2b6cb0;     /* Azul corporativo principal */
    --primary-light: #4299e1;    /* Azul más claro para acentos */
    --primary-lighter: #e6f3ff;  /* Azul muy claro para fondos */
}
```

## 📞 Soporte

El sistema está completamente documentado y es fácil de personalizar. Todas las funciones están implementadas y probadas.

---

**Task Manager Pro** - Una solución profesional de gestión de tareas diseñada para equipos modernos. 🚀# TaskManagerPro
