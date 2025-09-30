# 🚀 Guía de Despliegue - Task Manager Pro

## 📋 Configuración para Producción con Neon PostgreSQL

### 🗄️ Base de Datos Neon

Tu proyecto está configurado para usar **Neon PostgreSQL** en producción. La configuración ya está lista en `env.production.py`.

#### 🔗 Cadena de Conexión
```
postgresql://neondb_owner:npg_hbRu1ioJxev7@ep-lucky-smoke-a9c4bhho-pooler.gwc.azure.neon.tech/neondb?sslmode=require&channel_binding=require
```

### 🛠️ Pasos para Despliegue

#### 1. **Configurar Variables de Entorno**

Para producción, usa el archivo `env.production.py`:

```bash
# Copiar configuración de producción
cp env.production.py env.py

# Editar variables específicas de tu dominio
nano env.py
```

#### 2. **Variables Importantes a Configurar**

```python
# 🌍 ENTORNO
os.environ.setdefault("DJANGO_DEBUG", "false")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "tu-dominio.com,www.tu-dominio.com")

# 🔐 SECRET KEY (¡CAMBIAR!)
os.environ.setdefault("DJANGO_SECRET_KEY", "tu-clave-secreta-super-segura")

# 📧 EMAIL (Configurar SMTP real)
os.environ.setdefault("DJANGO_EMAIL_HOST_USER", "tu-email@gmail.com")
os.environ.setdefault("DJANGO_EMAIL_HOST_PASSWORD", "tu-app-password")

# 🌐 SITIO
os.environ.setdefault("DJANGO_SITE_DOMAIN", "tu-dominio.com")
```

#### 3. **Instalar Dependencias**

```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias (incluye psycopg2-binary para PostgreSQL)
pip install -r requirements.txt
```

#### 4. **Migraciones de Base de Datos**

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones a Neon PostgreSQL
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

#### 5. **Recolectar Archivos Estáticos**

```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

### 🔧 Configuración de Servidor

#### **Nginx (Recomendado)**

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    
    location /static/ {
        alias /ruta/a/tu/proyecto/staticfiles/;
    }
    
    location /media/ {
        alias /ruta/a/tu/proyecto/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### **Gunicorn**

```bash
# Instalar Gunicorn
pip install gunicorn

# Ejecutar con Gunicorn
gunicorn --bind 0.0.0.0:8000 task_manager.wsgi:application
```

### 🔒 Configuración de Seguridad

#### **SSL/HTTPS (Let's Encrypt)**

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

#### **Variables de Seguridad Activas**

En producción, estas configuraciones están activas:

```python
# 🔒 SECURITY SETTINGS - PRODUCCIÓN
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 📊 Monitoreo y Logs

#### **Configuración de Logs**

```python
# Los logs se guardan en logs/django.log
DJANGO_LOG_LEVEL = "WARNING"  # En producción
```

#### **Comandos Útiles**

```bash
# Ver logs en tiempo real
tail -f logs/django.log

# Verificar estado de la aplicación
python manage.py check --deploy

# Verificar conexión a la base de datos
python manage.py dbshell
```

### 🚀 Despliegue en Plataformas

#### **Heroku**

```bash
# Instalar Heroku CLI
# Crear app
heroku create tu-app-name

# Configurar variables de entorno
heroku config:set DJANGO_DEBUG=false
heroku config:set DJANGO_SECRET_KEY=tu-clave-secreta
heroku config:set DJANGO_ALLOWED_HOSTS=tu-app-name.herokuapp.com

# Desplegar
git push heroku main

# Ejecutar migraciones
heroku run python manage.py migrate
```

#### **DigitalOcean App Platform**

1. Conectar repositorio
2. Configurar variables de entorno
3. Configurar build command: `pip install -r requirements.txt`
4. Configurar run command: `gunicorn task_manager.wsgi:application`

#### **Railway**

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login y deploy
railway login
railway init
railway up
```

### 🔍 Verificación Post-Despliegue

#### **Checklist de Verificación**

- [ ] ✅ Aplicación carga correctamente
- [ ] ✅ Base de datos conectada (Neon PostgreSQL)
- [ ] ✅ Archivos estáticos servidos
- [ ] ✅ SSL/HTTPS funcionando
- [ ] ✅ Email configurado
- [ ] ✅ Logs funcionando
- [ ] ✅ Admin accesible
- [ ] ✅ Usuarios pueden registrarse/login

#### **Comandos de Verificación**

```bash
# Verificar configuración
python manage.py check --deploy

# Verificar base de datos
python manage.py dbshell

# Verificar archivos estáticos
python manage.py collectstatic --dry-run

# Verificar logs
tail -n 50 logs/django.log
```

### 🆘 Troubleshooting

#### **Error de Conexión a Base de Datos**

```bash
# Verificar variables de entorno
echo $DJANGO_DB_HOST
echo $DJANGO_DB_NAME

# Probar conexión manual
psql "postgresql://neondb_owner:npg_hbRu1ioJxev7@ep-lucky-smoke-a9c4bhho-pooler.gwc.azure.neon.tech/neondb?sslmode=require&channel_binding=require"
```

#### **Error de Archivos Estáticos**

```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Verificar permisos
chmod -R 755 staticfiles/
```

#### **Error de SSL**

```bash
# Verificar certificado
sudo certbot certificates

# Renovar certificado
sudo certbot renew
```

### 📞 Soporte

Si tienes problemas:

1. **Revisar logs**: `tail -f logs/django.log`
2. **Verificar configuración**: `python manage.py check --deploy`
3. **Probar base de datos**: `python manage.py dbshell`
4. **Verificar variables**: `env | grep DJANGO`

---

**¡Tu Task Manager Pro está listo para producción con Neon PostgreSQL!** 🚀
