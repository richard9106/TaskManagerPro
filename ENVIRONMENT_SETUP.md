# 🔐 Configuración de Variables de Entorno - Task Manager Pro

## 📋 Descripción

Este proyecto utiliza un sistema de variables de entorno para manejar configuraciones sensibles y específicas del entorno. Todas las configuraciones se gestionan a través del archivo `env.py`.

## 🚀 Configuración Inicial

### 1. Copiar el archivo de ejemplo
```bash
cp env.example env.py
```

### 2. Editar las variables según tu entorno
Abre `env.py` y ajusta los valores según tus necesidades:

```python
# 🔐 SECRET KEY
os.environ.setdefault("DJANGO_SECRET_KEY", "tu-clave-secreta-super-segura")

# 🌍 ENTORNO
os.environ.setdefault("DJANGO_DEBUG", "true")  # false para producción
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "tu-dominio.com,www.tu-dominio.com")
```

## 🔧 Variables Disponibles

### 🔐 Configuración Básica
- `DJANGO_SECRET_KEY`: Clave secreta de Django (¡OBLIGATORIA!)
- `DJANGO_DEBUG`: Modo debug (true/false)
- `DJANGO_ALLOWED_HOSTS`: Hosts permitidos (separados por comas)

### 🗄️ Base de Datos
- `DJANGO_DB_ENGINE`: Motor de base de datos
- `DJANGO_DB_NAME`: Nombre de la base de datos
- `DJANGO_DB_USER`: Usuario de la base de datos
- `DJANGO_DB_PASSWORD`: Contraseña de la base de datos
- `DJANGO_DB_HOST`: Host de la base de datos
- `DJANGO_DB_PORT`: Puerto de la base de datos

### 📧 Configuración de Email
- `DJANGO_EMAIL_BACKEND`: Backend de email
- `DJANGO_EMAIL_HOST`: Servidor SMTP
- `DJANGO_EMAIL_PORT`: Puerto SMTP
- `DJANGO_EMAIL_USE_TLS`: Usar TLS (true/false)
- `DJANGO_EMAIL_HOST_USER`: Usuario de email
- `DJANGO_EMAIL_HOST_PASSWORD`: Contraseña de email

### 🔒 Configuración de Seguridad
- `DJANGO_SECURE_SSL_REDIRECT`: Redirección SSL (true/false)
- `DJANGO_SESSION_COOKIE_SECURE`: Cookies seguras (true/false)
- `DJANGO_CSRF_COOKIE_SECURE`: CSRF seguro (true/false)
- `DJANGO_SECURE_HSTS_SECONDS`: Segundos HSTS

### 🌐 Configuración del Sitio
- `DJANGO_SITE_ID`: ID del sitio
- `DJANGO_SITE_DOMAIN`: Dominio del sitio
- `DJANGO_SITE_NAME`: Nombre del sitio

### 🔑 Configuración de Allauth
- `DJANGO_ACCOUNT_EMAIL_VERIFICATION`: Verificación de email
- `DJANGO_ACCOUNT_EMAIL_REQUIRED`: Email requerido (true/false)
- `DJANGO_ACCOUNT_USERNAME_REQUIRED`: Username requerido (true/false)
- `DJANGO_ACCOUNT_AUTHENTICATION_METHOD`: Método de autenticación

### 🚀 Rendimiento y Caché
- `DJANGO_CACHE_BACKEND`: Backend de caché
- `DJANGO_CACHE_LOCATION`: Ubicación del caché

### 📊 Logging
- `DJANGO_LOG_LEVEL`: Nivel de logging
- `DJANGO_LOG_FILE`: Archivo de logs

## 🏗️ Configuraciones por Entorno

### 🧪 Desarrollo
```python
# env.py para desarrollo
os.environ.setdefault("DJANGO_DEBUG", "true")
os.environ.setdefault("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
os.environ.setdefault("DJANGO_SECURE_SSL_REDIRECT", "false")
os.environ.setdefault("DJANGO_CACHE_BACKEND", "django.core.cache.backends.locmem.LocMemCache")
```

### 🚀 Producción
```python
# env.py para producción
os.environ.setdefault("DJANGO_DEBUG", "false")
os.environ.setdefault("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
os.environ.setdefault("DJANGO_SECURE_SSL_REDIRECT", "true")
os.environ.setdefault("DJANGO_CACHE_BACKEND", "django.core.cache.backends.redis.RedisCache")
os.environ.setdefault("DJANGO_DB_ENGINE", "django.db.backends.postgresql")
```

## 🔒 Seguridad

### ⚠️ Importante
- **NUNCA** subas `env.py` al repositorio
- **NUNCA** compartas tu `SECRET_KEY`
- **SIEMPRE** usa HTTPS en producción
- **SIEMPRE** configura variables de seguridad para producción

### 🛡️ Buenas Prácticas
1. Usa claves secretas únicas para cada entorno
2. Configura SSL/TLS en producción
3. Usa contraseñas seguras para la base de datos
4. Configura logging apropiado
5. Revisa regularmente las configuraciones de seguridad

## 📁 Estructura de Archivos

```
task_manager/
├── env.py              # Variables de entorno (NO subir al repo)
├── env.example         # Ejemplo de configuración
├── task_manager/
│   └── settings.py     # Configuración de Django
├── logs/               # Directorio de logs
└── .gitignore          # Archivos ignorados por Git
```

## 🚀 Comandos Útiles

### Verificar configuración
```bash
python manage.py check
```

### Ejecutar servidor
```bash
python manage.py runserver
```

### Ver logs
```bash
tail -f logs/django.log
```

## 🔧 Troubleshooting

### Error: "SECRET_KEY not set"
- Verifica que `env.py` existe
- Asegúrate de que `DJANGO_SECRET_KEY` esté configurado

### Error: "Database connection failed"
- Verifica las credenciales de la base de datos
- Asegúrate de que la base de datos esté ejecutándose

### Error: "Email not sending"
- Verifica la configuración SMTP
- Revisa las credenciales de email

## 📞 Soporte

Si tienes problemas con la configuración, revisa:
1. Los logs en `logs/django.log`
2. La configuración en `env.py`
3. La documentación de Django
4. Los issues del proyecto

---

**¡Recuerda mantener tus datos sensibles seguros!** 🔐
