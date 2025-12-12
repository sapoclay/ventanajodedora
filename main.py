"""
Ventana que reaparece aleatoriamente en la pantalla.
"""
import tkinter as tk
import random
import signal
import sys
import re
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageTk
from PIL.Image import Resampling

from mensaje_salida import imprimir_mensaje_salida


class VentanaJodedora:
    """Ventana que se oculta y reaparece en posiciones aleatorias."""
    
    # Constantes de configuración
    ANCHO = 200
    ALTO = 300
    TIEMPO_REAPARICION = 2000  # milisegundos
    IMAGEN_ANCHO = 150
    IMAGEN_ALTO = 150
    
    def __init__(self):
        self.root = tk.Tk()
        self.imagen_tk: ImageTk.PhotoImage | None = None
        self._monitor_principal: tuple[int, int, int, int] | None = None  # x, y, w, h
        self._ancho_actual = self.ANCHO
        self._alto_actual = self.ALTO
        self._configurar_ventana()
        self._crear_widgets()
        self._ajustar_tamano_y_posicion_inicial()
    
    def _configurar_ventana(self):
        """Configura las propiedades básicas de la ventana."""
        self.root.title("Ventana Básica")
        self.root.geometry(f"{self.ANCHO}x{self.ALTO}")
        self.root.overrideredirect(True)  # Sin bordes
        self.root.configure(bg="#2b2b2b")  # Fondo oscuro
    
    def _obtener_monitor_principal(self) -> tuple[int, int, int, int]:
        """Devuelve la geometría (x, y, w, h) del monitor principal.

        En Linux intenta usar `xrandr --listmonitors`. Si no está disponible (Wayland,
        contenedores, etc.), cae a (0, 0, screenwidth, screenheight).
        """
        if self._monitor_principal is not None:
            return self._monitor_principal

        self.root.update_idletasks()
        fallback = (0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight())

        if shutil.which("xrandr") is None:
            self._monitor_principal = fallback
            return self._monitor_principal

        try:
            proc = subprocess.run(
                ["xrandr", "--listmonitors"],
                check=False,
                capture_output=True,
                text=True,
            )
            out = (proc.stdout or "").splitlines()
            # Ejemplo:
            #  0: +*eDP-1 1920/344x1080/193+0+0  eDP-1
            #  1: +HDMI-1 1920/510x1080/290+1920+0  HDMI-1
            primary = None
            first = None
            rgx = re.compile(r"^\s*\d+:\s+\+(\*?)\S+\s+(\d+)/\d+x(\d+)/\d+\+(\d+)\+(\d+)")
            for line in out:
                m = rgx.match(line)
                if not m:
                    continue
                is_primary = m.group(1) == "*"
                w = int(m.group(2))
                h = int(m.group(3))
                x = int(m.group(4))
                y = int(m.group(5))
                rect = (x, y, w, h)
                if first is None:
                    first = rect
                if is_primary:
                    primary = rect
                    break

            self._monitor_principal = primary or first or fallback
            return self._monitor_principal
        except Exception:
            self._monitor_principal = fallback
            return self._monitor_principal

    def _obtener_tamano_requerido(self) -> tuple[int, int]:
        """Obtiene el tamaño real requerido por el contenido."""
        self.root.update_idletasks()
        # winfo_width/height puede ser 1 si está oculto; usar req como fallback.
        w = max(self.root.winfo_width(), self.root.winfo_reqwidth(), self.ANCHO)
        h = max(self.root.winfo_height(), self.root.winfo_reqheight(), self.ALTO)
        return w, h

    def _ajustar_tamano_a_pantalla(self) -> None:
        """Ajusta el tamaño de la ventana para que quepa en pantalla."""
        _, _, ancho_pantalla, alto_pantalla = self._obtener_monitor_principal()
        w_req, h_req = self._obtener_tamano_requerido()
        self._ancho_actual = min(w_req, ancho_pantalla)
        self._alto_actual = min(h_req, alto_pantalla)
        self.root.geometry(f"{self._ancho_actual}x{self._alto_actual}")

    def _ajustar_tamano_y_posicion_inicial(self) -> None:
        self._ajustar_tamano_a_pantalla()
        self._posicionar_aleatoriamente()
    
    def _posicionar_aleatoriamente(self):
        """Posiciona la ventana en una ubicación aleatoria de la pantalla."""
        self._ajustar_tamano_a_pantalla()
        mon_x, mon_y, mon_w, mon_h = self._obtener_monitor_principal()
        max_x = mon_x + max(0, mon_w - self._ancho_actual)
        max_y = mon_y + max(0, mon_h - self._alto_actual)
        x = random.randint(mon_x, max_x)
        y = random.randint(mon_y, max_y)
        self.root.geometry(f"{self._ancho_actual}x{self._alto_actual}+{x}+{y}")
    
    def _cargar_imagen(self) -> ImageTk.PhotoImage | None:
        """Carga y redimensiona la imagen PNG con transparencia."""
        directorio_script = Path(__file__).parent
        ruta_imagen = directorio_script / "corte_manga.png"
        
        if not ruta_imagen.exists():
            print(f"Advertencia: No se encontró la imagen en {ruta_imagen}")
            return None
        
        try:
            with Image.open(ruta_imagen) as imagen:
                # Asegurar modo RGBA para transparencia
                if imagen.mode != "RGBA":
                    imagen = imagen.convert("RGBA")
                
                imagen_redimensionada = imagen.resize(
                    (self.IMAGEN_ANCHO, self.IMAGEN_ALTO),
                    Resampling.LANCZOS
                )
                return ImageTk.PhotoImage(imagen_redimensionada)
        except Exception as e:
            print(f"Error al cargar la imagen: {e}")
            return None
    
    def _crear_widgets(self):
        """Crea todos los widgets de la ventana."""
        # Frame contenedor con padding
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Cargar y mostrar imagen
        self.imagen_tk = self._cargar_imagen()
        if self.imagen_tk:
            label_imagen = tk.Label(frame, image=self.imagen_tk, bg="#2b2b2b")
            label_imagen.pack(pady=10)
        
        # Botón de cerrar con estilo
        btn_cerrar = tk.Button(
            frame,
            text="Cerrar",
            command=self._ocultar_y_reaparecer,
            bg="#ff4444",
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn_cerrar.pack(pady=20)
        
        # Efectos hover para el botón
        btn_cerrar.bind("<Enter>", lambda e: btn_cerrar.configure(bg="#ff6666"))
        btn_cerrar.bind("<Leave>", lambda e: btn_cerrar.configure(bg="#ff4444"))
    
    def _ocultar_y_reaparecer(self):
        """Oculta la ventana y programa su reaparición."""
        self.root.withdraw()
        self.root.after(self.TIEMPO_REAPARICION, self._reaparecer)
    
    def _reaparecer(self):
        """Muestra la ventana en una nueva posición aleatoria."""
        self._posicionar_aleatoriamente()
        self.root.deiconify()
    
    def ejecutar(self):
        """Inicia el bucle principal de la aplicación."""
        self.root.mainloop()


def main():
    """Punto de entrada principal."""
    app = VentanaJodedora()

    def manejador_sigint(signum, frame):
        """Reacción a Ctrl+C con un mensaje personalizado."""
        imprimir_mensaje_salida()
        try:
            app.root.destroy()
        finally:
            raise SystemExit(0)

    signal.signal(signal.SIGINT, manejador_sigint)
    app.ejecutar()


if __name__ == "__main__":
    main()