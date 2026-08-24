import os
import re
import random
import threading
import time
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

def keep_alive():
    while True:
        time.sleep(600)
        try:
            requests.get("https://asistente-ia-conquista.onrender.com/")
        except Exception:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

def procesar_respuesta_ia(texto_raw, modo):
    """
    Limpia etiquetas de pensamiento interno y añade encabezado formateado.
    """
    texto = re.sub(r'<think>.*?</think>', '', texto_raw, flags=re.DOTALL)
    if '<think>' in texto:
        texto = texto.split('<think>')[0]
    if '</think>' in texto:
        texto = texto.split('</think>')[-1]

    lineas = texto.split('\n')
    lineas_filtradas = []
    
    palabras_basura = [
        "analiz", "pensam", "usuario", "solicitud", "espera", "releyendo",
        "thinking", "context", "strategy", "option 1", "option 2", "here is"
    ]
    
    for l in lineas:
        linea_str = l.strip()
        if not linea_str:
            continue
        if any(p in linea_str.lower() for p in palabras_basura):
            continue
        
        linea_limpia = re.sub(r'\*\*', '', linea_str)
        lineas_filtradas.append(linea_limpia)

    header = f"📌 Respuestas estilo {modo.upper()}:\n\n"

    if lineas_filtradas:
        return header + "\n\n".join(lineas_filtradas)
    
    return header + "1. ¿Cómo va tu día por allá?\n\n2. Qué bueno saber de ti, avísame si te liberas luego.\n\n3. ¡Muchos éxitos en todo hoy!"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spark IA - Tu Asistente de Conquista</title>
    <style>
        body { background-color: #121212; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 20px; margin: 0; }
        .container { max-width: 500px; margin: auto; background: #1e1e1e; padding: 25px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); margin-top: 20px; }
        h2 { color: #bb86fc; margin-bottom: 5px; }
        .subtitle { color: #888; font-size: 14px; margin-bottom: 20px; }
        .upload-area { border: 2px dashed #888; border-radius: 15px; padding: 20px; cursor: pointer; background: #252525; margin-bottom: 15px; }
        #preview-img { max-width: 100%; max-height: 200px; border-radius: 10px; margin-top: 10px; display: none; }
        textarea { width: 90%; height: 70px; background: #2a2a2a; color: white; border: 1px solid #444; border-radius: 12px; padding: 12px; resize: none; margin-bottom: 15px; font-size: 14px;}
        
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
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Spark IA</h2>
        <div class="subtitle">Asistente de Conquista v8.2</div>
        
        <div class="upload-area" onclick="document.getElementById('file-input').click();">
            <span id="upload-text">📸 Subir captura del chat</span>
            <input type="file" id="file-input" accept="image/*" onchange="cargarImagen(event)" style="display:none;">
            <img id="preview-img">
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

        function cargarImagen(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagenBase64 = e.target.result;
                    document.getElementById('preview-img').src = imagenBase64;
                    document.getElementById('preview-img').style.display = 'block';
                    document.getElementById('upload-text').style.display = 'none';
                };
                reader.readAsDataURL(file);
            }
        }

        function limpiarTodo() {
            imagenBase64 = null;
            document.getElementById('file-input').value = "";
            document.getElementById('preview-img').style.display = 'none';
            document.getElementById('upload-text').style.display = 'block';
            document.getElementById('texto-adicional').value = "";
            document.getElementById('res').innerText = "Sube una captura o escribe contexto y elige un estilo.";
        }

        async function generarRespuesta(modo) {
            const resDiv = document.getElementById('res');
            const textoManual = document.getElementById('texto-adicional').value;
            
            if (!imagenBase64 && !textoManual && modo !== 'Iniciar Conversación') {
                resDiv.innerText = "⚠️ Escribe un mensaje o sube una imagen para empezar.";
                return;
            }
            
            resDiv.innerHTML = '<span class="loading">🤔 Generando respuestas ' + modo.toLowerCase() + 's...</span>';
            
            try {
                const response = await fetch('/procesar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        imagen: imagenBase64, 
                        texto: textoManual, 
                        modo: modo 
                    })
                });
                const data = await response.json();
                if (data.respuesta) { 
                    resDiv.innerText = data.respuesta; 
                } else { 
                    resDiv.innerText = "❌ Error: " + (data.error || "No se pudo procesar"); 
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
    texto_manual = data.get('texto', '')
    modo = data.get('modo', 'Coqueto')

    key_actual = os.environ.get("GROQ_API_KEY", "").strip()
    if not key_actual:
        return jsonify({'error': 'Falta la variable GROQ_API_KEY en Render.'}), 500

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key_actual}"
    }

    semilla_variacion = random.randint(1000, 9999)

    prompt_estricto = (
        f"[Variación #{semilla_variacion}] "
        f"Genera 3 respuestas breves, naturales y creativas en Español Latino. "
        f"ESTILO REQUERIDO: {modo.upper()}. "
        f"Contexto o texto del chat: '{texto_manual}'. "
        f"Responde únicamente con 3 opciones listas para enviar, una por línea numerada del 1 al 3."
    )

    # Modelos oficiales activos en la infraestructura de Groq
    modelos_a_probar = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "qwen/qwen3.6-27b",
        "llama-3.1-8b-instant"
    ]

    for mod in modelos_a_probar:
        body = {
            "model": mod,
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un asistente de conquista rápida. Entregas exactamente 3 respuestas cortas numeradas en español latino."
                },
                {
                    "role": "user",
                    "content": prompt_estricto
                }
            ],
            "temperature": 0.85,
            "max_tokens": 200
        }

        try:
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body, timeout=20)
            res_json = resp.json()

            if resp.status_code == 200 and "choices" in res_json:
                raw_text = res_json["choices"][0]["message"]["content"]
                texto_final = procesar_respuesta_ia(raw_text, modo)
                return jsonify({'respuesta': texto_final})
        except Exception:
            continue

    return jsonify({'error': 'No se pudo conectar a los servidores de IA en este momento. Revisa la clave API en Render o reintenta.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
