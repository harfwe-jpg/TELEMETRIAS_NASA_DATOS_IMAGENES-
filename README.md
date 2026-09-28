# 🚀 NASA Object Tracker & Telemetry System

## 📌 Descripción General
El **NASA Object Tracker & Telemetry System** es una solución híbrida de alto rendimiento diseñada para el análisis físico en tiempo real. Este sistema combina la potencia de la visión artificial en Python con una interfaz web universalmente accesible. Sus capacidades centrales incluyen:
- Cálculo preciso de áreas en centímetros y metros cuadrados.
- Estimación de velocidad instantánea (m/s) basada en desplazamiento de centroides.
- Mapeo de trayectorias y asignación de identificadores únicos por objeto.
- Registro estructurado y persistente de toda la telemetría en formato JSON.

## 🏗️ Arquitectura Técnica
- **Backend (Python/Flask)**: Estándar aeroespacial por su robustez, ecosistema científico (OpenCV, NumPy) y facilidad para integrar algoritmos de procesamiento de imágenes de grado profesional.
- **Motor de Visión (`tracker_engine.py`)**: Implementa umbralización adaptativa, detección de contornos, filtrado de ruido y un algoritmo de seguimiento por proximidad euclidiana para mantener la identidad de los objetos entre fotogramas.
- **Frontend (HTML5/CSS3/JS)**: Interfaz minimalista, oscura y de alto contraste, diseñada bajo principios de accesibilidad universal (WCAG). Permite que cualquier usuario, desde un niño en un programa educativo hasta un adulto mayor o un ingeniero de vuelo, interactúe con el sistema sin curva de aprendizaje.

## 🛠️ Instrucciones de Instalación y Ejecución

Siga estos pasos para desplegar el sistema en su estación de trabajo:

1. **Instalar Python**: Asegúrese de tener Python 3.8 o superior instalado en su sistema.
2. **Clonar el repositorio**: 
   ```bash
   git clone <url-del-repositorio>
   cd nasa_object_tracker

