import os
import re
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Modelo de visión soportado oficialmente en Groq
MODELO_GROQ = "llama-3.2-11b-vision-preview"

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
        .upload-area { border: 2px dashed #888; border-radius: 15px; padding: 20px; cursor: pointer; background: #252525; margin-bottom: 20px; }
        #preview-img { max-width: 100%; max-height: 250px; border-radius: 10px; margin-top: 10px; display: none; }
        textarea { width: 90%; height: 70px; background: #2a2a2a; color: white; border: 1px solid #444; border-radius: 12px; padding: 12px; resize: none; margin-bottom: 20px; font-size: 14px;}
        .grid-botones { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
        .btn-base { border: none; padding: 15px; border-radius: 12px; font-weight: bold; cursor: pointer; color: white; text-transform: uppercase; font-size: 13px;}
        .btn-rom { background: linear-gradient(135deg, #ff69b4, #ff1493); }
        .btn-coq { background: linear-gradient(135deg, #ff9100, #ed8002); }
        .btn-pic { background: linear-gradient(135deg, #ff3d00, #dd2c00); }
        .btn-pro { background: linear-gradient(135deg, #a855f7, #7e22ce); }
        #res { background: #2a2a2a; padding: 18px; border-radius: 12px; text-align: left; white-space: pre-wrap; margin-top: 20px; border-left: 5px solid #00D4FF; min-height: 60px; font-size: 15px; }
        .loading { color: #888; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Spark IA</h2>
        <div class="subtitle">Asistente de Conquista v6.4</div>
        <div class="upload-area" onclick="document.getElementById('file-input').click();">
            <span id="upload-text">📸 Subir captura del chat</span>
            <input type="file" id="file-input" accept="image/*" onchange="cargarImagen(event)" style="display:none;">
            <img id="preview-img">
        </div>
        <textarea id="texto-adicional" placeholder="Contexto extra (opcional)..."></textarea>
        <div class="grid-botones">
            <button class="btn-base btn-rom" onclick="generarRespuesta('Romántico')">💖 Romántico</button>
            <button class="btn-base btn-coq" onclick="generarRespuesta('Coqueto')">😏 Coqueto</button>
            <button class="btn-base btn-pic" onclick="generarRespuesta('Picante')">🔥 Picante</button>
            <button class="btn-base btn-pro" onclick="generarRespuesta('Provocativo')">😈 Provocativo</button>
        </div>
        <div id="res">Sube una captura y elige un modo.</div>
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
        async function generarRespuesta(modo) {
            const resDiv = document.getElementById('res');
            const textoExtra = document.getElementById('texto-adicional').value;
            if (!imagenBase64 && !textoExtra.trim()) {
                resDiv.innerText = "⚠️ Sube una imagen o da contexto.";
                return;
            }
            resDiv.innerHTML = '<span class="loading">🤔 Analizando y generando respuestas...</span>';
            try {
                const response = await fetch('/procesar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ imagen: imagenBase64, texto_extra: textoExtra, modo: modo })
                });
                const data = await response.json();
                if (data.respuesta) { resDiv.innerHTML = data.respuesta; }
                else { resDiv.innerText = "❌ Error: " + (data.error || "Desconocido"); }
            } catch (err) { resDiv.innerText = "❌ Error de conexión."; }
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
    if not client:
        return jsonify({'error': 'GROQ_API_KEY no configurada.'}), 500
    
    data = request.json
    imagen_b64 = data.get('imagen')
    texto_extra = data.get('texto_extra', '')
    modo = data.get('modo', 'Coqueto')

    prompt = f"""
RESPONDE EXCLUSIVAMENTE EN ESPAÑOL.
Analiza la captura del chat adjunta y genera EXACTAMENTE 3 opciones de respuesta en estilo **{modo.upper()}**.

FORMATO DE SALIDA (ESTRICTO - SIN ANÁLISIS, SIN INTRODUCCIONES, SIN TEXTO EN INGLÉS):

1. "[Opcion de respuesta 1]"
📌 Por qué funciona: [Explicación de 1 sola línea corta]

2. "[Opcion de respuesta 2]"
📌 Por qué funciona: [Explicación de 1 sola línea corta]

3. "[Opcion de respuesta 3]"
📌 Por qué funciona: [Explicación de 1 sola línea corta]

Contexto opcional del usuario: "{texto_extra}".
"""

    # Construir mensaje multimodal
    content = [{"type": "text", "text": prompt}]
    if imagen_b64:
        content.append({"type": "image_url", "image_url": {"url": imagen_b64}})

    try:
        completion = client.chat.completions.create(
            model=MODELO_GROQ,
            messages=[{"role": "user", "content": content}],
            temperature=0.6,
            max_tokens=500
        )
        respuesta_texto = completion.choices[0].message.content
        
        # Filtro en el servidor para eliminar cualquier prefijo técnico si el modelo lo genera
        if "1." in respuesta_texto:
            respuesta_texto = "1." + respuesta_texto.split("1.", 1)[1]

        return jsonify({'respuesta': respuesta_texto})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
