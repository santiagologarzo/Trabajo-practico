Explicación del programa
Este programa es una app con ventana hecha en Python usando PyQt5, que te permite descargar videos o audios de YouTube (y otros sitios que soporte yt-dlp) de forma fácil.

Lo que hace básicamente es:

Le pegás la URL del video que querés bajar.

El programa consulta los datos del video (como título, duración, autor, vistas, y la miniatura) usando yt-dlp, y te los muestra.

Podés elegir si querés bajar el video en mp4, solo el audio en mp3, o simplemente ver la info sin descargar nada.

Si elegís bajar video, te muestra las resoluciones disponibles para que elijas la que te guste.

Cuando empezás a descargar, el programa baja el video/audio y lo guarda en una carpeta llamada output que crea automáticamente si no existe.

Usa hilos (QThread) para que la interfaz no se quede congelada mientras está bajando o consultando info.

Usa ffmpeg.exe para procesar el audio/video (por ejemplo, convertir el audio a mp3), y este archivo tiene que estar en la misma carpeta que el programa para que funcione.

Si el programa está compilado a .exe o lo corrés como script, detecta bien la ruta donde está para encontrar los archivos que necesita.

Además muestra la miniatura del video en la ventana para que sea más visual.

En resumen, es una interfaz simple y rápida para usar yt-dlp sin tener que usar la terminal, y con opciones para elegir formato y resolución, todo hecho con Python y PyQt5.
