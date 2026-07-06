# Riesgo de Inundación por Parroquia — Provincia del Guayas

Aplicación Flask con mapa interactivo (Leaflet) que muestra la categoría de
riesgo de inundación (bajo / medio / alto) predicha por el modelo de
clasificación para las 54 parroquias de la provincia del Guayas, Ecuador.

## Estructura

```
webapp/
├── app.py                          # Backend Flask (rutas /, /api/*, /descargar-predicciones)
├── wsgi.py                         # Entrypoint WSGI (PythonAnywhere, Hostinger, etc.)
├── Procfile                        # Entrypoint para Render / Railway (gunicorn)
├── requirements.txt
├── parroquias_guayas.geojson       # Polígonos de parroquias (WGS84)
├── predicciones_riesgo_guayas.csv  # Salida del notebook (pcode, riesgo, confianza, modelo_final)
├── templates/
│   └── index.html                  # Mapa Leaflet + panel lateral (buscador, top-5, metodología)
└── static/
    └── predicciones_riesgo_guayas.csv  # Copia servida para descarga directa
```

El emparejamiento entre el GeoJSON y las predicciones se realiza por
**`pcode`** (código DPA de parroquia, 6 dígitos), tal como recomienda el
enunciado del proyecto.

## Ejecución local

```bash
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py                       # http://localhost:5000
```

La app **no se ejecuta en modo debug** (`debug=False` en `app.py`), tal como
exige el enunciado.

## Regenerar las predicciones

Las predicciones se generan desde el notebook
`notebook/riesgo_inundacion_guayas.ipynb` (sección 13), que escribe
automáticamente `webapp/predicciones_riesgo_guayas.csv`. Si se reentrena el
modelo, basta con volver a ejecutar el notebook y redesplegar.

## Despliegue en producción

El enunciado del proyecto exige desplegar en **PythonAnywhere, Render o
Railway** (no se aceptan aplicaciones solo en local). A continuación las tres
opciones:

### Opción recomendada: PythonAnywhere
1. Crear cuenta gratuita en https://www.pythonanywhere.com
2. Subir la carpeta `webapp/` (Files → Upload, o `git clone` de tu repo).
3. En **Web → Add a new web app → Flask → Python 3.10+**.
4. Editar el archivo WSGI que genera PythonAnywhere para que apunte a
   `wsgi.py` de este proyecto (importa `application` desde `app.py`).
5. En **Web → Virtualenv**, indicar la ruta de un virtualenv con
   `pip install -r requirements.txt`.
6. **Reload** de la web app. URL pública: `https://<usuario>.pythonanywhere.com`.

### Opción: Render
1. Crear un repositorio Git con el contenido de `webapp/`.
2. En https://render.com → **New → Web Service** → conectar el repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT` (ya incluido en `Procfile`).
5. Render asigna una URL pública tipo `https://<nombre>.onrender.com`.

## Notas de robustez para producción
- El servidor de desarrollo de Flask (`python app.py`) **no debe usarse en
  producción**; en PythonAnywhere se usa su propio servidor WSGI, y en
  Render/Railway se usa `gunicorn` (ver `Procfile`).
- Si el hosting reinicia la app por inactividad (plan gratuito), la primera
  carga puede tardar unos segundos.
