"""
Aplicacion web Flask - Riesgo de Inundacion por Parroquia (Provincia del Guayas)
----------------------------------------------------------------------------
Sirve un mapa interactivo (Leaflet) con los poligonos de las parroquias del
Guayas, coloreados segun la categoria de riesgo de inundacion predicha por el
modelo (notebook riesgo_inundacion_guayas.ipynb).

Emparejamiento geo <-> prediccion: por codigo de parroquia (pcode / DPA_PARROQ),
tal como recomienda el enunciado del proyecto.

NO se ejecuta en modo debug (requisito del proyecto).
"""

import json
import os
from datetime import datetime

import pandas as pd
from flask import Flask, jsonify, render_template, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEOJSON_PATH = os.path.join(BASE_DIR, "parroquias_guayas.geojson")
PRED_CSV_PATH = os.path.join(BASE_DIR, "predicciones_riesgo_guayas.csv")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__)

RISK_COLORS = {
    "bajo": "#2ecc71",
    "medio": "#f1c40f",
    "alto": "#e74c3c",
}


def _norm_pcode(x):
    """Normaliza el codigo de parroquia a string de 6 digitos (con ceros a la izquierda)."""
    return str(x).strip().zfill(6)


def _modelo_final_nombre():
    try:
        pred = pd.read_csv(PRED_CSV_PATH)
        if "modelo_final" in pred.columns and len(pred):
            return str(pred["modelo_final"].iloc[0])
    except Exception:
        pass
    return "Ensamble (LR+DT+SVM+RF)"


def load_map_data():
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geo = json.load(f)

    pred = pd.read_csv(PRED_CSV_PATH, dtype={"pcode": str})
    pred["pcode"] = pred["pcode"].apply(_norm_pcode)
    pred_map = pred.set_index("pcode")[["riesgo_inundacion", "score"]].to_dict(orient="index")

    matched, unmatched = 0, 0
    for feature in geo["features"]:
        props = feature["properties"]
        pcode = _norm_pcode(props.get("pcode", ""))
        info = pred_map.get(pcode)
        if info:
            riesgo = info["riesgo_inundacion"]
            props["riesgo_inundacion"] = riesgo
            props["score"] = info["score"]
            props["color"] = RISK_COLORS.get(riesgo, "#999999")
            matched += 1
        else:
            props["riesgo_inundacion"] = "sin dato"
            props["score"] = None
            props["color"] = "#999999"
            unmatched += 1

    app.logger.info(f"Emparejamiento geo<->prediccion: {matched} ok, {unmatched} sin dato")
    return geo


@app.route("/")
def index():
    ultima_actualizacion = datetime.fromtimestamp(os.path.getmtime(PRED_CSV_PATH)).strftime("%d/%m/%Y")
    return render_template(
        "index.html",
        risk_colors=RISK_COLORS,
        modelo_final=_modelo_final_nombre(),
        ultima_actualizacion=ultima_actualizacion,
    )


@app.route("/api/parroquias")
def api_parroquias():
    geo = load_map_data()
    return jsonify(geo)


@app.route("/api/resumen")
def api_resumen():
    pred = pd.read_csv(PRED_CSV_PATH)
    resumen = pred["riesgo_inundacion"].value_counts().reindex(["bajo", "medio", "alto"]).fillna(0).to_dict()
    return jsonify(resumen)


@app.route("/descargar-predicciones")
def descargar_predicciones():
    return send_from_directory(STATIC_DIR, "predicciones_riesgo_guayas.csv", as_attachment=True)


if __name__ == "__main__":
    # Ejecucion local de desarrollo. En produccion (PythonAnywhere / Render /
    # Railway) el servidor WSGI (gunicorn / passenger_wsgi) importa `app`
    # directamente; ver README.md para instrucciones de despliegue.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
