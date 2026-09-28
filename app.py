import os
import base64
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify
from tracker_engine import NASAObjectTracker

app = Flask(__name__)

# Configuración de límites de seguridad aeroespacial para archivos subidos (máximo 10MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 
tracker = NASAObjectTracker()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process_image", methods=["POST"])
def process_image():
    if 'file' not in request.files:
        return jsonify({"error": "No se encontró el flujo de datos del archivo"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Identificador de archivo vacío"}), 400

    try:
        # Decodificación segura de búfer de imagen
        file_bytes = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"error": "Flujo de imagen corrupto o formato no compatible con OpenCV"}), 400

        # Procesamiento de visión por computador y persistencia controlada
        processed_frame, detected_objects = tracker.process_frame(frame)
        tracker.save_to_json()

        # Codificación optimizada a Base64 para transmisión con baja latencia al frontend
        success, buffer = cv2.imencode('.jpg', processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        if not success:
            return jsonify({"error": "Fallo en la codificación del frame visual"}), 500
            
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            "success": True,
            "metrics": detected_objects,
            "image": f"data:image/jpeg;base64,{img_base64}"
        })
        
    except Exception as e:
        return jsonify({"error": f"Excepción crítica en subsistema de telemetría: {str(e)}"}), 500

if __name__ == "__main__":
    # Configuración segura para producción/desarrollo basada en entorno
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
