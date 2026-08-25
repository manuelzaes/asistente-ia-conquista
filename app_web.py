import os
import re
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

def limpiar_respuesta(texto_raw, modo):
    texto = re.sub(r'<think>.*?</think>', '', texto_raw, flags=re.DOTALL)
    if '<think>' in texto:
        texto = texto.split('<think>')[0]
    if '</think>' in texto:
        texto = texto.split('</think>')[-1]

    lineas = [l.strip() for l in texto.split('\n') if l.strip()]
    lineas_filtradas = []
    
    palabras_basura = ["analiz", "pensam", "usuario", "solicitud", "espera", "thinking", "option"]
    
    for l in lineas:
        if not any(p in l.lower() for p in palabras_basura):
            linea_limpia = re.sub(r'\*\*', '', l)
            lineas_filtradas.append(linea_limpia)

    header = f"📌 Respuestas estilo {modo.upper()}:\n\n"
    if lineas_filtradas:
        return header + "\n\n".join(lineas_filtradas)
    return texto_raw

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
        <div class="subtitle">Asistente de Conquista v16.1</div>
        
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
            
            resDiv.innerHTML = '<span class="loading">🤔 Generando respuestas ' + modo.toLowerCase() + 's únicas...</span>';
            
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
                    resDiv.innerText = "❌ " + (data.error || "Error al procesar la solicitud."); 
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
    texto_manual = data.get('texto', '').strip()
    modo = data.get('modo', 'Coqueto')

    api_key = os.environ.get("GROQ_API_KEY", "").strip()

    if not api_key:
        return jsonify({'error': 'Falta configurar la GROQ_API_KEY en Render.'})

    guia_estilo = {
        "Iniciar Conversación": "Rompehielos original, ingenioso e impredecible para abrir conversación de forma fluida.",
        "Romántico": "Cálido, tierno, expresivo, seguro de sí mismo y muy detallista.",
        "Coqueto": "Divertido, juguetón, con humor fresco y picardía ligera.",
        "Picante": "Atrevido, audaz, coqueto y directo sin rodeos.",
        "Provocativo": "Desafiante, interesante y misterioso para obligar a responder.",
        "Salvar el Momento": "Ingenioso y ameno para desentrampar la conversación si se enfrió."
    }

    estilo_instruccion = guia_estilo.get(modo, "Atractivo y natural.")
    contexto_evaluado = texto_manual if texto_manual else "Hola, ¿cómo estás?"

    prompt_texto = (
        f"Contexto o mensaje recibido del chat: '{contexto_evaluado}'.\n"
        f"Genera exactamente 3 opciones de respuesta NUNCA antes vistas, totalmente improvisadas, variadas y originales en estilo {modo.upper()}.\n"
        f"Enfoque del tono: {estilo_instruccion}\n"
        f"REGLA OBLIGATORIA: Adapta las respuestas al mensaje o contexto exacto. Responde únicamente con las 3 opciones numeradas del 1 al 3 en español latino natural, sin introducción ni notas adicionales."
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Lista de modelos compatibles en orden de prioridad
    modelos = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.6-27b",
        "llama-3.3-70b-versatile"
    ]

    ultimo_error = ""

    for modelo in modelos:
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un experto en seducción, carisma y conversación que improvisa opciones dinámicas e inéditas cada vez que le piden una respuesta."},
                {"role": "user", "content": prompt_texto}
            ],
            "temperature": 0.95,
            "max_tokens": 400
        }

        try:
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=12)
            res_json = resp.json()

            if resp.status_code == 200 and "choices" in res_json:
                raw_text = res_json["choices"][0]["message"]["content"]
                texto_final = limpiar_respuesta(raw_text, modo)
                return jsonify({'respuesta': texto_final})
            elif "error" in res_json:
                ultimo_error = res_json["error"].get("message", "Error desconocido")
        except Exception as e:
            ultimo_error = str(e)

    return jsonify({'error': f"Groq API Error: {ultimo_error}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
