# Flet Music Player (MPD Client)

Cliente moderno, responsivo y ligero para [MPD (Music Player Daemon)](https://www.musicpd.org/) y [Mopidy](https://mopidy.com/), reescrito completamente en **Python 3 + Flet** con una interfaz inspirada en reproductores multimedia modernos (estilo VLC).

Diseñado específicamente para ofrecer una experiencia limpia, rápida y cómoda desde dispositivos móviles y navegadores web.

---

## Características

- 📱 **Diseño Móvil / Responsive**: UI moderna inspirada en VLC y Material Design con soporte para temas oscuros.
- ⏯️ **Controles de Reproducción**: Play, Pause, Stop, Siguiente, Anterior.
- 🔊 **Volumen y Búsqueda (Seek)**: Barras deslizantes interactivas para volumen y navegación en la pista actual.
- 🔀 **Aleatorio y Repetición**: Modos Random y Repeat fácilmente activables.
- 📋 **Gestión de Colas (Queue/Playlist)**: Visualiza la lista de reproducción actual, salta directamente a cualquier canción, elimina pistas individuales o vacía la cola.
- 📁 **Explorador de Biblioteca por Carpetas**: Navegación ágil por el árbol de directorios de música con botones rápidos para reproducir pistas o añadir carpetas completas a la cola.
- ⚙️ **Configuración Flexible**: Conexión a MPD mediante variables de entorno o mediante el diálogo de ajustes integrado.
- 🐳 **Preparado para Podman y Docker**: Empaquetado optimizado en contenedor ligero con soporte directo para Linux server.

---

## Requisitos

- Python 3.10 o superior
- Servidor [MPD][] o [Mopidy][] accesible en red local o en contenedor.

---

## Ejecución Local

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configurar variables de entorno (opcional, por defecto conecta a `localhost:6600`):
   ```bash
   export MPD_HOST=127.0.0.1
   export MPD_PORT=6600
   export PORT=7080
   ```

3. Ejecutar la aplicación:
   ```bash
   python -m app.main
   ```

4. Abrir en el navegador móvil o de escritorio:
   ```
   http://localhost:7080
   ```

---

## Despliegue con Podman en Linux Server

Puedes construir y ejecutar el contenedor usando **Podman**:

### 1. Construir la imagen
```bash
podman build -t flet-music-player:latest .
```

### 2. Ejecutar el contenedor
```bash
podman run -d \
  --name flet-music-player \
  -p 7080:7080 \
  -e MPD_HOST=192.168.1.100 \
  -e MPD_PORT=6600 \
  --restart unless-stopped \
  flet-music-player:latest
```

*(Reemplaza `192.168.1.100` por la IP o nombre de tu servidor MPD).*

### 3. Usar con Podman Compose / Docker Compose

Si deseas desplegar la aplicación junto a un servidor MPD:

```bash
podman compose up -d
# O con docker compose:
docker compose up -d
```

---

## Variables de Entorno

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `HOST` | Dirección IP donde escucha el servidor web Flet | `0.0.0.0` |
| `PORT` | Puerto HTTP para acceder a la app web | `7080` |
| `MPD_HOST` | Host o IP del servidor MPD | `mpd` o `localhost` |
| `MPD_PORT` | Puerto del demonio MPD | `6600` |
| `MPD_PASSWORD` | Contraseña del servidor MPD (si requiere) | `""` |

---

## Ejecutar Pruebas

Para ejecutar el conjunto de pruebas unitarias:
```bash
python3 -m pytest -v
```

---

## Licencia

Este proyecto está bajo los términos de la [GNU General Public License v3.0](COPYING).
