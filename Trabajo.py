import sys
import os
import requests

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QComboBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from yt_dlp import YoutubeDL


class MetaDataThread(QThread):
    datos_obtenidos = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            with YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.datos_obtenidos.emit(info)
        except Exception as e:
            self.error.emit(str(e))


class DownloadThread(QThread):
    terminado = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, output_path, formato="mp4", output_template=None):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.formato = formato
        self.output_template = output_template or os.path.join(output_path, "%(title)s.%(ext)s")

    def run(self):
        try:
            carpeta_script = os.path.dirname(os.path.abspath(__file__))
            ffmpeg_path = os.path.join(carpeta_script, "ffmpeg.exe")
            opciones = {
                'outtmpl': self.output_template,
                'quiet': False,
                'ffmpeg_location': ffmpeg_path,
            }

            if self.formato == "audio":
                opciones.update({
                    'format': 'bestaudio',
                    'extractaudio': True,
                    'audioformat': 'mp3',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            else:
                opciones['format'] = self.formato

            with YoutubeDL(opciones) as ydl:
                ydl.download([self.url])

            self.terminado.emit("Descarga completada")
        except Exception as e:
            self.error.emit(str(e))


class DescargadorSimple(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Descargar video con yt-dlp")
        self.setFixedSize(900, 500)
        self.label = QLabel("Pegá la URL del video:")
        self.url_input = QLineEdit()
        self.boton_descargar = QPushButton("Descargar")
        self.boton_descargar.setEnabled(False)
        self.estado = QLabel("")
        self.estado.setWordWrap(True)

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(480, 270)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)

        self.meta_label = QLabel("")
        self.meta_label.setWordWrap(True)

        self.combo_accion = QComboBox()
        self.combo_accion.addItems([
            "Descargar video (mp4)",
            "Descargar solo audio (mp3)",
            "Obtener solo información",
            "Descargar video calidad baja"
        ])
        self.combo_accion.setEnabled(False)

        self.combo_resoluciones = QComboBox()
        self.combo_resoluciones.setEnabled(False)

        input_layout = QVBoxLayout()
        input_layout.addWidget(self.label)
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.meta_label)
        input_layout.addWidget(self.combo_accion)
        input_layout.addWidget(self.combo_resoluciones)
        input_layout.addWidget(self.boton_descargar)
        input_layout.addWidget(self.estado)
        input_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        main_layout = QHBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.thumbnail_label)

        self.setLayout(main_layout)

        self.meta_thread = None
        self.download_thread = None
        self.info_video = None

        self.url_input.textChanged.connect(self.cargar_metadata)
        self.boton_descargar.clicked.connect(self.descargar_video)
        self.combo_accion.currentIndexChanged.connect(self.on_cambio_formato)

    def cargar_metadata(self):
        url = self.url_input.text().strip()
        self.boton_descargar.setEnabled(False)
        self.combo_accion.setEnabled(False)
        self.combo_resoluciones.clear()
        self.combo_resoluciones.setEnabled(False)
        self.meta_label.setText("")
        self.estado.setText("")
        self.thumbnail_label.clear()

        if not url:
            return

        self.estado.setText("Cargando metadatos...")
        if self.meta_thread and self.meta_thread.isRunning():
            self.meta_thread.terminate()

        self.meta_thread = MetaDataThread(url)
        self.meta_thread.datos_obtenidos.connect(self.mostrar_metadata)
        self.meta_thread.error.connect(self.error_metadata)
        self.meta_thread.start()

    def mostrar_metadata(self, info):
        self.info_video = info 
        titulo = info.get("title", "Desconocido")
        duracion = info.get("duration", 0)
        autor = info.get("uploader", "Desconocido")
        vistas = info.get("view_count", 0)
        thumb_url = info.get("thumbnail", "")

        duracion_minutos = duracion // 60
        duracion_segundos = duracion % 60

        texto_meta = (
            f"<b>Título:</b> {titulo}<br>"
            f"<b>Duración:</b> {duracion_minutos}m {duracion_segundos}s<br>"
            f"<b>Autor:</b> {autor}<br>"
            f"<b>Vistas:</b> {vistas:,}"
        )
        self.meta_label.setText(texto_meta)
        self.estado.setText("Metadatos cargados")
        self.boton_descargar.setEnabled(True)
        self.combo_accion.setEnabled(True)

        if thumb_url:
            try:
                respuesta = requests.get(thumb_url)
                if respuesta.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(respuesta.content)
                    pixmap = pixmap.scaled(self.thumbnail_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.thumbnail_label.setPixmap(pixmap)
            except Exception:
                self.thumbnail_label.clear()

        if self.combo_accion.currentText() == "Descargar video (mp4)":
            self.llenar_resoluciones(info)

    def llenar_resoluciones(self, info):
        self.combo_resoluciones.clear()
        formatos = info.get('formats', [])
        video_formats = [f for f in formatos if f.get('ext') == 'mp4' and f.get('vcodec') != 'none']
        video_formats.sort(key=lambda x: x.get('height', 0))

        for f in video_formats:
            altura = f.get('height', 0)
            fps = f.get('fps', 0)
            fmt_id = f.get('format_id')
            texto = f"{altura}p {fps}fps - id: {fmt_id}"
            self.combo_resoluciones.addItem(texto, userData=fmt_id)

        if self.combo_resoluciones.count() == 0:
            self.combo_resoluciones.addItem("No hay resoluciones mp4 disponibles", userData=None)
            self.combo_resoluciones.setEnabled(False)
        else:
            self.combo_resoluciones.setEnabled(True)

    def error_metadata(self, error_msg):
        self.estado.setText(f"Error al cargar metadatos: {error_msg}")
        self.meta_label.setText("")
        self.boton_descargar.setEnabled(False)
        self.combo_accion.setEnabled(False)
        self.combo_resoluciones.clear()
        self.combo_resoluciones.setEnabled(False)
        self.thumbnail_label.clear()

    def on_cambio_formato(self):
        accion = self.combo_accion.currentText()
        if accion == "Descargar video (mp4)":
            self.combo_resoluciones.setEnabled(True)
            if self.info_video:
                self.llenar_resoluciones(self.info_video)
        else:
            self.combo_resoluciones.clear()
            self.combo_resoluciones.setEnabled(False)

    def descargar_video(self):
        url = self.url_input.text().strip()
        if not url:
            self.estado.setText("Ingresá una URL válida")
            return 

        carpeta_script = os.path.dirname(os.path.abspath(__file__))
        carpeta_output = os.path.join(carpeta_script, "output")

        if not os.path.exists(carpeta_output):
            os.makedirs(carpeta_output)

        accion = self.combo_accion.currentText()

        if accion == "Obtener solo información":
            self.estado.setText("Solo información mostrada, no se descarga nada.")
            return

        self.estado.setText("Descargando...")
        self.boton_descargar.setEnabled(False)
        self.combo_accion.setEnabled(False)
        self.combo_resoluciones.setEnabled(False)

        output_template = os.path.join(carpeta_output, "%(title)s.%(ext)s")
        formato_descarga = ""

        if accion == "Descargar video (mp4)":
            fmt_id = self.combo_resoluciones.currentData()
            if fmt_id:
                formato_descarga = f"{fmt_id}+bestaudio/best"
            else:
                formato_descarga = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
        elif accion == "Descargar solo audio (mp3)":
            formato_descarga = "audio" 
        elif accion == "Descargar video calidad baja":
            
            formato_descarga = "worstvideo[ext=mp4]+bestaudio/best" 
        else:
        
            formato_descarga = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
        self.download_thread = DownloadThread(url, carpeta_output, formato_descarga, output_template)
        self.download_thread.terminado.connect(self.descarga_terminada)
        self.download_thread.error.connect(self.error_descarga)
        self.download_thread.start()


    def descarga_terminada(self, msg):
        self.estado.setText(msg)
        self.boton_descargar.setEnabled(True)
        self.combo_accion.setEnabled(True)
        self.combo_resoluciones.setEnabled(self.combo_accion.currentText() == "Descargar video (mp4)")

    def error_descarga(self, error_msg):
        self.estado.setText(f"Error en descarga: {error_msg}")
        self.boton_descargar.setEnabled(True)
        self.combo_accion.setEnabled(True)
        self.combo_resoluciones.setEnabled(self.combo_accion.currentText() == "Descargar video (mp4)")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if getattr(sys, 'frozen', False):
        carpeta_script = os.path.dirname(sys.executable)
    else:
        carpeta_script = os.path.dirname(os.path.abspath(__file__))

    ruta_estilo = os.path.join(carpeta_script, "estilo.css")

    with open(ruta_estilo, "r") as f:
        estilo = f.read()
    app.setStyleSheet(estilo)

    ventana = DescargadorSimple()
    ventana.show()
    sys.exit(app.exec_())
