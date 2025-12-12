# ventanaJodedora

Aplicación de escritorio en Python (Tkinter) que muestra una ventana sin bordes con una imagen y un botón **Cerrar**. Al pulsar este botón, la ventana se oculta y reaparece tras unos segundos en una posición aleatoria.

## Requisitos

- Linux con Python 3
- Dependencias Python (ver `requirements.txt`):
  - `Pillow`

## Archivos

- `main.py`: aplicación Tkinter (ventana, imagen, botón y reaparición).
- `run_app.py`: lanzador que crea un entorno virtual en `venv/`, instala dependencias y ejecuta `main.py`.
- `corte_manga.png`: imagen que se muestra (se recomienda PNG con transparencia).

## Cómo ejecutar

### Opción recomendada (con entorno virtual automático)

```bash
cd /var/www/html/Python/VentanaJodedora
python3 ./run_app.py
```

`run_app.py`:
- crea `venv/` si no existe,
- instala dependencias desde `requirements.txt` (evita reinstalar si no cambió),
- ejecuta la app.

### Opción manual (si ya gestionas tu venv)

```bash
cd /var/www/html/Python/VentanaJodedora
python3 ./main.py
```

## Funcionamiento

- La ventana:
  - no tiene bordes (`overrideredirect(True)`),
  - muestra `corte_manga.png` redimensionada,
  - incluye un botón **Cerrar**.

- Botón **Cerrar**:
  - oculta la ventana,
  - tras `TIEMPO_REAPARICION` milisegundos reaparece,
  - reaparece en una posición aleatoria **dentro del monitor principal**.

## Monitor principal

En Linux, `main.py` intenta detectar el monitor principal usando `xrandr --listmonitors` (elige el marcado con `*`) y limita la ventana a ese rectángulo para que no se salga de la pantalla principal. Si `xrandr` no está disponible, usa un fallback con el tamaño de pantalla que reporta Tk.

## Salir de la aplicación

- En la terminal, `Ctrl+C` cierra la app mostrando un mensaje personalizado.
- Si estás ejecutando con `run_app.py`, el lanzador también captura `Ctrl+C` para evitar tracebacks y mostrar el mismo mensaje.
