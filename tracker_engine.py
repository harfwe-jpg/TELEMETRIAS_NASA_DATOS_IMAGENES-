import json
import time
import cv2
import numpy as np
import os
import threading

class NASAObjectTracker:
    def save_frame_snapshot(self, frame, detected_objects):
        """Guarda una captura fotográfica física en disco si hay objetos detectados en la misión."""
        if not detected_objects:
            return  # No desperdiciar espacio si el espacio está vacío
            
        os.makedirs("mission_archives", exist_ok=True)
        timestamp_str = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        filename = f"mission_archives/capture_{timestamp_str}.jpg"
        
        # Guardar la imagen procesada con el HUD de telemetría impreso
        cv2.imwrite(filename, frame)
        print(f"[REGISTRO DE MISIÓN]: Fotograma guardado exitosamente en {filename}")

    def __init__(self):
        self.json_output_file = "data_telemetria.json"
        self.pixel_to_cm_ratio = 10.0  # Relación de escala: 10 píxeles = 1 cm
        self.prev_positions = {}         # Diccionario de seguimiento: {id: {'cx': x, 'cy': y, 'last_time': t}}
        self.telemetry_data = []         # Lista de almacenamiento de telemetría acotada
        self.next_id = 1
        self.last_frame_time = time.time()
        self.lock = threading.Lock()     # Bloqueo de seguridad para concurrencia multiusuario
        self.max_history_records = 50    # Límite estricto para evitar desbordamiento de memoria/disco

    def process_frame(self, frame):
        with self.lock:
            current_time = time.time()
            dt = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Reseteo de seguridad si la sesión está inactiva más de 5 segundos (evita vectores fantasmas entre imágenes distintas)
            if dt > 5.0 or dt <= 0:
                dt = 0.033
                self.prev_positions.clear()
                self.next_id = 1

            # 1. Preprocesamiento de imagen con corrección de ruido avanzada
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
            
            # 2. Detección de siluetas
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detected_objects = []
            current_centroids = {}

            for cnt in contours:
                if cv2.contourArea(cnt) < 500:
                    continue
                
                # 3. Cálculos geométricos de precisión
                x, y, w, h = cv2.boundingRect(cnt)
                width_cm = w / self.pixel_to_cm_ratio
                height_cm = h / self.pixel_to_cm_ratio
                area_cm2 = (w * h) / (self.pixel_to_cm_ratio ** 2)
                area_m2 = area_cm2 / 10000.0
                
                cx, cy = x + w // 2, y + h // 2
                
                # 4. Asignación de ID Único por proximidad euclidiana
                obj_id = None
                min_dist = float('inf')
                for pid, pdata in self.prev_positions.items():
                    dist = np.sqrt((cx - pdata['cx'])**2 + (cy - pdata['cy'])**2)
                    if dist < min_dist and dist < 100:
                        min_dist = dist
                        obj_id = pid
                
                if obj_id is None:
                    obj_id = self.next_id
                    self.next_id += 1
                    
                current_centroids[obj_id] = {'cx': cx, 'cy': cy, 'last_time': current_time}
                
                # 5. Cálculo de velocidad instantánea de telemetría (m/s)
                if obj_id in self.prev_positions:
                    prev = self.prev_positions[obj_id]
                    dist_px = np.sqrt((cx - prev['cx'])**2 + (cy - prev['cy'])**2)
                    dist_m = (dist_px / self.pixel_to_cm_ratio) / 100.0
                    velocity_ms = dist_m / dt
                else:
                    velocity_ms = 0.0
                    
                detected_objects.append({
                    "id": obj_id,
                    "width_cm": round(width_cm, 2),
                    "height_cm": round(height_cm, 2),
                    "area_cm2": round(area_cm2, 2),
                    "area_m2": round(area_m2, 4),
                    "velocity_ms": round(velocity_ms, 2),
                    "centroid": {"cx": cx, "cy": cy}
                })
                
                # 6. Renderizado de telemetría visual sobre el HUD del frame
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {obj_id}", (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"Area: {area_cm2:.1f} cm2", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                cv2.putText(frame, f"Vel: {velocity_ms:.2f} m/s", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            self.prev_positions = current_centroids
            
            # Control de acotamiento de memoria RAM en la lista de telemetría
            self.telemetry_data.append({
                "timestamp": current_time,
                "objects": detected_objects
            })
            if len(self.telemetry_data) > self.max_history_records:
                self.telemetry_data.pop(0)
            
            # NUEVO: Guardar evidencia fotográfica automática de la misión
            self.save_frame_snapshot(frame, detected_objects)
            
            return frame, detected_objects

    def save_to_json(self):
        """Vuelca de manera segura los datos acotados de telemetría."""
        with self.lock:
            try:
                with open(self.json_output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.telemetry_data, f, indent=4, ensure_ascii=False)
            except IOError as e:
                print(f"[Error de telemetría en disco]: {e}")
