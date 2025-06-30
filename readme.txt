# Descargador de videos con yt-dlp y PyQt5

Aplicación hecha en Python con PyQt5 para descargar videos o audio de YouTube usando yt-dlp.

---

## Qué hace

- Pegás un link de YouTube
- Muestra título, duración, autor y miniatura
- Podés elegir entre descargar video, solo audio o solo ver la info
- Descarga el archivo según lo que elijas

---

Para hacer este programa usamos Python junto con la biblioteca PyQt5, que nos permitió crear toda la interfaz gráfica: los botones, los cuadros de texto y la parte visual en general. También usamos requests para poder descargar la miniatura del video desde internet, y json para interpretar los datos que devuelve yt-dlp.
Como el programa se encarga de ejecutar yt-dlp por detrás para obtener la información del video y también para descargarlo, usamos subprocess, que nos permite ejecutar comandos como si los estuviéramos escribiendo en la terminal. Además, usamos sys y os para manejar rutas y para saber si el programa se está ejecutando como script .py o como .exe, y así adaptarse según el caso.
Todo lo que tenga que ver con hilos lo hicimos con QThread, que es parte de PyQt, para que mientras se descargan cosas o se cargan los metadatos, la interfaz no se congele.
Por fuera de Python, usamos el programa yt-dlp.exe, que tiene que estar en la misma carpeta que el .exe del programa, porque es el que realmente se encarga de hacer el trabajo pesado de buscar la info y descargar el video o audio. Y para compilar el .py a .exe usamos PyInstaller, con la opción --noconsole para que no aparezca una ventana negra, y --add-data para incluir archivos como el estilo.css.
Además de eso, es importante que estén todos los archivos en la misma carpeta: el .exe, el yt-dlp.exe, el archivo estilo.css y, si se quiere, una carpeta output para que los videos se guarden ahí. Todo eso hace que la app sea portable y funcione sin necesidad de instalar nada.
