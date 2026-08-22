import os
import threading
import time
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Se obtiene la clave de forma segura desde las variables de Render
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

# Script Keep-Alive para evitar que Render se dormite
def keep_alive():
    while True:
        time.sleep(600)
        try:
            requests.get("https://asistente-ia-conquista.onrender.com/")
        except Exception:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

def obtener_modelo_activo(key):
    """
    Consulta dinámicamente a Groq para ver qué modelos están disponibles
    para esta API Key en particular.
    """
    try:
        resp = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            modelos_disponibles = [m.get("id") for m in data.get("data", []) if m.get("id")]
            
            # Orden de preferencia si están disponibles
            preferencias = [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "llama3-70b-8192",
                "llama3-8b-8192",
                "mixtral-8x7b-32768"
            ]
            
            for pref in preferencias:
                if pref in modelos_disponibles:
                    return pref
            
            # Si no coincide con las preferencias, usar el primer modelo disponible que no sea whisper
            for m_id in modelos_disponibles:
                if "whisper" not in m_id.lower() and "guard" not in m_id.lower():
                    return m_id
    except Exception as e:
        print(f"Error consultando modelos: {e}")
    
    # Fallback por defecto si no responde la lista
    return "llama-3.1-8b-instant"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spark IA - Tu Asistente de Conquista</title>
    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
    <style>
        body { background-color: #121212; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 20px; margin: 0; }
        .container { max-width: 500px; margin: auto; background: #1e1e1e; padding: 25px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); margin-top: 20px; }
        h2 { color: #bb86fc; margin-bottom: 5px; }
        .subtitle { color: #888; font-size: 14px; margin-bottom: 20px; }
        .upload-area { border: 2px dashed #888; border-radius: 15px; padding: 20px; cursor: pointer; background: #252525; margin-bottom: 15px; }
        #preview-img { max-width: 100%; max-height: 250px; border-radius: 10px; margin-top: 10px; display: none; }
        textarea { width: 90%; height: 60px; background: #2a2a2a; color: white; border: 1px solid #444; border-radius: 12px; padding: 12px; resize: none; margin-bottom: 15px; font-size: 14px;}
        
        .grid-botones { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 15px; }
        .btn-base { border: none; padding: 12px; border-radius: 12px; font-weight: bold; cursor: pointer; color: white; text-transform: uppercase; font-size: 12px;}
        .btn-ini { background: linear-gradient(135deg, #00c6ff, #0072ff); grid-column: span 2; }
        .btn-rom { background: linear-gradient(135deg, #ff69b4, #ff1493); }
        .btn-coq { background: linear-gradient(135deg, #ff9100, #ed8002); }
        .btn-pic { background: linear-gradient(135deg, #ff3d00, #dd2c00); }
        .btn-pro { background: linear-gradient(135deg, #a855f7, #7e22ce); }
        .btn-salv { background: linear-gradient(135deg, #10b981, #059669); grid-column: span 2; }
        .btn-limp { background: #444; color: #ccc; margin-top: 10px; width: 100%; padding: 10px; border-radius: 10px; border: none; cursor: pointer; font-size: 12px; }
        
        #res { background: #2a2a2a; padding: 18px; border-radius: 12px; text-align: left; white-space: pre-wrap; margin-top: 15px; border-left: 5px solid #00D4FF; min-height: 50px; font-size: 14px; line-height: 1.5; }
        .loading { color: #888; font-style: italic; }
        #status-ocr { font-size: 12px; color: #00c6ff; margin-top: 5px; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Spark IA</h2>
        <div class="subtitle">Asistente de Conquista v5.1</div>
        
        <div class="upload-area" onclick="document.getElementById('file-input').click();">
            <span id="upload-text">📸 Subir captura del chat</span>
            <input type="file" id="file-input" accept="image/*" onchange="cargarImagen(event)" style="display:none;">
            <img id="preview-img">
            <div id="status-ocr">🔍 Leyendo imagen...</div>
        </div>
        
        <textarea id="texto-adicional" placeholder="Escribe aquí lo que dijo o el contexto extra..."></textarea>
        
        <div class="grid-botones">
            <button class="btn-base btn-ini" onclick="generarRespuesta('Iniciar Conversación')">🚀 INICIAR CONVERSACIÓN</button>
            <button class="btn-base btn-rom" onclick="generarRespuesta('Romántico')">💖 ROMÁNTICO</button>
            <button class="btn-base btn-coq" onclick="generarRespuesta('Coqueto')">😏 COQUETO</button>
            <button class="btn-base btn-pic" onclick="generarRespuesta('Picante')">🔥 PICANTE</button>
            <button class="btn-base btn-pro" onclick="generarRespuesta('Provocativo')">😈 PROVOCATIVO</button>
            <button class="btn-base btn-salv" onclick="generarRespuesta('Salvar el Momento')">🛟 SALVAR EL MOMENTO</button>
        </div>
        
        <button class="btn-limp" onclick="limpiarTodo()">🧹 Limpiar Todo</button>
        
        <div id="res">Sube una captura o escribe contexto y elige un estilo.</div>
    </div>

    <script>
        let imagenBase64 = null;
        let textoExtraidoOCR = "";

        async function cargarImagen(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = async function(e) {
                    imagenBase64 = e.target.result;
                    document.getElementById('preview-img').src = imagenBase64;
                    document.getElementById('preview-img').style.display = 'block';
                    document.getElementById('upload-text').style.display = 'none';
                    
                    const status = document.getElementById('status-ocr');
                    status.style.display = 'block';
                    status.innerText = "🔍 Procesando texto...";
                    
                    try {
                        const result = await Tesseract.recognize(imagenBase64, 'spa');
                        textoExtraidoOCR = result.data.text.trim();
                        status.innerText = "✅ Captura leída correctamente";
                    } catch (err) {
                        status.innerText = "⚠️ Ingrese el contexto abajo.";
                    }
                };
                reader.readAsDataURL(file);
            }
        }

        function limpiarTodo() {
            imagenBase64 = null;
            textoExtraidoOCR = "";
            document.getElementById('file-input').value = "";
            document.getElementById('preview-img').style.display = 'none';
            document.getElementById('upload-text').style.display = 'block';
            document.getElementById('status-ocr').style.display = 'none';
            document.getElementById('texto-adicional').value = "";
            document.getElementById('res').innerText = "Sube una captura o escribe contexto y elige un estilo.";
        }

        async function generarRespuesta(modo) {
            const resDiv = document.getElementById('res');
            const textoManual = document.getElementById('texto-adicional').value;
            const contextoFinal = (textoExtraidoOCR + "\\n" + textoManual).trim();
            
            if (!contextoFinal && modo !== 'Iniciar Conversación') {
                resDiv.innerText = "⚠️ Suba una captura o escriba el mensaje en el cuadro de texto.";
                return;
            }
            
            resDiv.innerHTML = '<span class="loading">🤔 Generando respuestas...</span>';
            
            try {
                const response = await fetch('/procesar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ contexto: contextoFinal, modo: modo })
                });
                const data = await response.json();
                if (data.respuesta) { 
                    resDiv.innerText = data.respuesta; 
                } else { 
                    resDiv.innerText = "❌ Error: " + (data.error || "Desconocido"); 
                }
            } catch (err) { 
                resDiv.innerText = "❌ Error de conexión con el servidor."; 
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/procesar', methods=['POST'])
def procesar():
    data = request.json or {}
    contexto = data.get('contexto', '')
    modo = data.get('modo', 'Coqueto')

    key_actual = os.environ.get("GROQ_API_KEY", "").strip()

    if not key_actual:
        return jsonify({'error': 'La variable GROQ_API_KEY no se encontró en Render. Revisa la sección Environment.'}), 500

    # Detección automática del modelo activo en la cuenta de Groq
    modelo_a_usar = obtener_modelo_activo(key_actual)

    prompt = f"""
Escribe EXCLUSIVAMENTE en español latino. Eres un experto en seducción y citas.

Genera ÚNICAMENTE 3 opciones de respuesta cortas y directas en tono **{modo.upper()}**.

Formato estricto:
1. "Opción 1"
2. "Opción 2"
3. "Opción 3"

REGLAS:
- Cero intros, cero saludos, cero explicaciones.
- Empieza directamente con "1.".
- Contexto brindado: "{contexto}"
"""

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key_actual}"
            },
            json={
                "model": modelo_a_usar,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 250
            },
            timeout=15
        )
        res_json = resp.json()
        if resp.status_code == 200 and "choices" in res_json:
            return jsonify({'respuesta': res_json["choices"][0]["message"]["content"].strip()})
        else:
            det = res_json.get("error", {}).get("message", resp.text)
            return jsonify({'error': f"Groq rechazó la solicitud (Modelo usado: {modelo_a_usar}). Detalle: {det}"}), 400
    except Exception as e:
        return jsonify({'error': f"Error en el servidor: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
