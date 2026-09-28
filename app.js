document.addEventListener('DOMContentLoaded', () => {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const launchBtn = document.getElementById('launch-btn');
    const webcamLaunchBtn = document.getElementById('webcam-launch-btn');
    const outputCanvas = document.getElementById('output-canvas');
    const jsonOutput = document.getElementById('json-output');
    const placeholderText = document.getElementById('placeholder-text');
    const countdownBanner = document.getElementById('countdown-banner');
    const countdownText = document.getElementById('countdown-text');
    const webcamVideo = document.getElementById('webcam-video');

    let isTrackingActive = false;

    // --- Manejo de Carga de Imágenes Estáticas ---
    uploadZone.addEventListener('click', () => fileInput.click());
    launchBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    fileInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        if (!file.type.startsWith('image/')) {
            jsonOutput.textContent = "// Error: El archivo seleccionado no es una imagen válida.";
            return;
        }

        stopActiveStreams();
        launchBtn.innerHTML = '<span class="icon">⏳</span><span class="text">Procesando Telemetría...</span>';
        jsonOutput.textContent = "// Analizando frame y calculando métricas físicas...";

        const formData = new FormData();
        formData.append('file', file);
        await sendToServer(formData);
        launchBtn.innerHTML = '<span class="icon">📁</span><span class="text">Cargar Imagen de Escaneo</span>';
    });

    // --- Secuencia de Lanzamiento con Webcam y Cuenta Regresiva (20s) ---
    webcamLaunchBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        stopActiveStreams();

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
            webcamVideo.srcObject = stream;
            await webcamVideo.play();

            // Activar banner de cuenta regresiva
            countdownBanner.style.display = 'flex';
            let timeLeft = 20;

            const countdownInterval = setInterval(async () => {
                if (timeLeft > 0) {
                    countdownText.textContent = `🚨 FASE DE ASCENSO: Saliendo de la atmósfera... T-${timeLeft}s restantes para análisis espacial.`;
                    timeLeft--;
                    
                    // Capturar y procesar frames durante la cuenta regresiva para mostrar entorno en tiempo real
                    await captureAndProcessWebcamFrame();
                } else {
                    clearInterval(countdownInterval);
                    countdownText.textContent = `🚀 ¡ÓRBITA ALCANZADA! Telemetría espacial en vivo activada. Analizando entorno...`;
                    isTrackingActive = true;
                    startContinuousTracking();
                }
            }, 1000);

        } catch (error) {
            jsonOutput.textContent = `// Error crítico de hardware/permisos de cámara: ${error.message}`;
            countdownBanner.style.display = 'none';
        }
    });

    async function captureAndProcessWebcamFrame() {
        if (webcamVideo.videoWidth === 0) return;

        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = webcamVideo.videoWidth;
        tempCanvas.height = webcamVideo.videoHeight;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.drawImage(webcamVideo, 0, 0, tempCanvas.width, tempCanvas.height);

        tempCanvas.toBlob(async (blob) => {
            if (!blob) return;
            const formData = new FormData();
            formData.append('file', blob, 'webcam_frame.jpg');
            await sendToServer(formData);
        }, 'image/jpeg', 0.85);
    }

    function startContinuousTracking() {
        const trackingLoop = setInterval(async () => {
            if (!isTrackingActive || !webcamVideo.srcObject) {
                clearInterval(trackingLoop);
                return;
            }
            await captureAndProcessWebcamFrame();
        }, 1000); // Envía un frame cada segundo para telemetría continua
    }

    function stopActiveStreams() {
        isTrackingActive = false;
        countdownBanner.style.display = 'none';
        if (webcamVideo.srcObject) {
            let tracks = webcamVideo.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            webcamVideo.srcObject = null;
        }
    }

    async function sendToServer(formData) {
        try {
            const response = await fetch('/process_image', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.success) {
                const img = new Image();
                img.onload = () => {
                    outputCanvas.style.display = 'block';
                    placeholderText.style.display = 'none';
                    outputCanvas.width = img.width;
                    outputCanvas.height = img.height;
                    const ctx = outputCanvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                };
                img.src = data.image;
                jsonOutput.textContent = JSON.stringify(data.metrics, null, 2);
            } else {
                jsonOutput.textContent = `// Error del Servidor Misión: ${data.error}`;
            }
        } catch (error) {
            jsonOutput.textContent = `// Error de enlace de red: ${error.message}`;
        }
    }

});
