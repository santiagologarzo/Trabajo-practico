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

## Problemas que tuvimos al hacerlo

1. **Guardaba en una carpeta temporal**
   - Cuando lo compilamos con `--onefile`, el .exe se ejecutaba desde una carpeta temporal y no guardaba las cosas donde estaba el .exe.
   - Lo solucionamos sacando la ruta real con `sys.executable` y guardando ahí.

2. **No encontraba `estilo.css`**
   - Si no estaba en la misma carpeta o no lo incluíamos bien al compilar, daba error.
   - Lo agregamos con `--add-data` y también pusimos un try para evitar que se rompa si no lo encuentra.

3. **Aparecía una consola negra**
   - Cada vez que abríamos el programa, también se abría una consola que no servía para nada.
   - Se arregló usando `--noconsole` al compilar.

4. **Error al cargar metadatos (WinError 2)**
   - El programa no encontraba `yt-dlp` cuando se lo pasamos a otra persona.
   - Lo resolvimos copiando `yt-dlp.exe` al lado del .exe y usando su ruta directamente en el código.

5. **El .exe no funciona solo**
   - Si le falta `yt-dlp.exe` o el CSS, no arranca bien.
   - Por eso decidimos no usar `--onefile` y distribuir directamente la carpeta con todos los archivos.

6. **Rutas distintas entre .py y .exe**
   - El programa funcionaba distinto si lo corrías desde el script que si lo corrías compilado.
   - Detectamos si está compilado y usamos la ruta correcta según el caso.

7. **Demasiados archivos en la carpeta**
   - Cuando se compila con PyInstaller, aparecen muchas DLL y archivos que parecen de más.
   - No es un error, son dependencias necesarias. Se ve desordenado, pero tiene que estar así.

---
