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
    
    palabras_basura = ["analiz", "pensam", "usuario", "solicitud", "espera", "thinking", "option", "here is"]
    
    for l in lineas:
        if not any(p in l.lower() for p in palabras_basura):
            linea_limpia = re.sub(r'\*\*', '', l)
            lineas_filtradas.append(linea_limpia)

    header = f"📌 Respuestas estilo {modo.upper()}:\n\n"
    if lineas_filtradas:
        return header + "\n\n".join(lineas_filtradas)
    return texto_raw

def limpiar_basura_ocr(texto):
    texto = re.sub(r'\b\d{1,2}:\d{2}\s*(?:p\.?\s*m\.?|a\.?\s*m\.?)?\b', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\b(visto|leído|enviado|online|en línea|whatsapp|hoy|ayer)\b', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\b\d+\b', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spark IA - Tu Asistente de Conquista</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚡</text></svg>">
    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
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
        <div class="subtitle">Asistente de Conquista v20.0</div>
        
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
        let textoExtraidoOCR = "";

        async function cargarImagen(event) {
            const file = event.target.files[0];
            if (file) {
                const resDiv = document.getElementById('res');
                resDiv.innerHTML = '<span class="loading">🔍 Leyendo texto de la captura...</span>';
                
                const reader = new FileReader();
                reader.onload = async function(e) {
                    imagenBase64 = e.target.result;
                    document.getElementById('preview-img').src = imagenBase64;
                    document.getElementById('preview-img').style.display = 'block';
                    document.getElementById('upload-text').style.display = 'none';

                    try {
                        const result = await Tesseract.recognize(imagenBase64, 'spa');
                        textoExtraidoOCR = result.data.text;
                        resDiv.innerText = "✅ Captura procesada con éxito. Ahora elige una opción abajo.";
                    } catch (err) {
                        textoExtraidoOCR = "";
                        resDiv.innerText = "📸 Captura lista. Elige una opción abajo.";
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
            document.getElementById('texto-adicional').value = "";
            document.getElementById('res').innerText = "Sube una captura o escribe contexto y elige un estilo.";
        }

        async function generarRespuesta(modo) {
            const resDiv = document.getElementById('res');
            const textoManual = document.getElementById('texto-adicional').value;
            
            let contextoFinal = (textoExtraidoOCR + " " + textoManual).trim();

            resDiv.innerHTML = '<span class="loading">🤔 Generando respuestas ' + modo.toLowerCase() + 's adaptadas...</span>';
            
            try {
                const response = await fetch('/procesar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        texto: contextoFinal, 
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
    texto_raw_contexto = data.get('texto', '').strip()
    modo = data.get('modo', 'Coqueto')

    api_key = os.environ.get("GROQ_API_KEY", "").strip()

    if not api_key:
        return jsonify({'error': 'Falta configurar la GROQ_API_KEY en Render.'})

    texto_contexto = limpiar_basura_ocr(texto_raw_contexto)

    guia_estilo = {
        "Iniciar Conversación": "Rompehielos original e ingenioso para abrir conversación.",
        "Romántico": "Cálido, tierno, cariñoso y expresivo.",
        "Coqueto": "Divertido, juguetón y con picardía ligera.",
        "Picante": "Atrevido, audaz y directo.",
        "Provocativo": "Desafiante y misterioso para generar interés.",
        "Salvar el Momento": "Ingenioso y ameno para reactivar la charla si se volvió fría o seca."
    }

    estilo_instruccion = guia_estilo.get(modo, "Atractivo y natural.")
    contexto_evaluado = texto_contexto if texto_contexto else "La otra persona acaba de responder."

    prompt_texto = (
        f"HISTORIAL / CONTEXTO EXTRAÍDO DEL CHAT:\n\"{contexto_evaluado}\"\n\n"
        f"INSTRUCCIÓN CLAVE DE ENFOQUE:\n"
        f"1. Identifica el ÚLTIMO MENSAJE o la ÚLTIMA PALABRA que la OTRA PERSONA te envió en ese historial.\n"
        f"2. Tu respuesta DEBE RESPONDER DIRECTAMENTE a esa última intervención de la otra persona. Usa el resto del chat únicamente como contexto ambiental.\n"
        f"3. Si ella dijo algo como 'depende del momento' o se rió, responde directamente a ese 'depende' o a su risa, no repitas lo que tú dijiste antes.\n\n"
        f"ESTILO REQUERIDO: {modo.upper()} ({estilo_instruccion})\n\n"
        f"REGLAS OBLIGATORIAS:\n"
        f"- NO saludes (no digas 'Hola', 'Buenas', etc.) salvo en 'Iniciar Conversación'.\n"
        f"- NUNCA menciones horarios (como 6:15 p.m.), ni números sueltos del OCR.\n"
        f"- Genera exactamente 3 opciones de respuesta numeradas del 1 al 3.\n"
        f"- Escribe en español latino natural, sin introducciones ni metatexto."
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    modelos = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.6-27b"
    ]

    ultimo_error = ""

    for modelo in modelos:
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Eres un experto en dinámicas de conversación y seducción. Tu especialidad es responder con agilidad al ÚLTIMO mensaje enviado por la otra persona en la conversación."},
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
                ultimo_error = res_json["error"].get("message", "Error en Groq API")
        except Exception as e:
            ultimo_error = str(e)

    return jsonify({'error': f"Groq API Error: {ultimo_error}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
