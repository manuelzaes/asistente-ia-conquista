import os
import base64
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = Flask(__name__)

# Configuración del cliente Groq con la API KEY del entorno
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spark IA - Tu Asistente de Conquista</title>
    <style>
        body { 
            background-color: #121212; 
            color: white; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            text-align: center; 
            padding: 20px; 
            margin: 0;
        }
        .container { 
            max-width: 500px; 
            margin: auto; 
            background: #1e1e1e; 
            padding: 25px; 
            border-radius: 20px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            margin-top: 20px;
        }
        h2 { color: #bb86fc; margin-bottom: 5px; }
        .subtitle { color: #888; font-size: 14px; margin-bottom: 20px; }
        
        .upload-area {
            border: 2px dashed #888;
            border-radius: 15px;
            padding: 20px;
            cursor: pointer;
            transition: 0.3s;
            margin-bottom: 20px;
            background: #252525;
        }
        .upload-area:hover { border-color: #bb86fc; background: #2d2d2d; }
        #file-input { display: none; }
        #preview-img { max-width: 100%; max-height: 250px; border-radius: 10px; margin-top: 10px; display: none; }

        textarea { 
            width: 90%; 
            height: 70px; 
            background: #2a2a2a; 
            color: white; 
            border: 1px solid #444; 
            border-radius: 12px; 
            padding: 12px; 
            font-size: 14px; 
            resize: none;
            margin-bottom: 20px;
        }

        .grid-botones {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }

        .btn-base {
            border: none; 
            padding: 15px; 
            border-radius: 12px; 
            font-weight: bold; 
            font-size: 14px; 
            cursor: pointer; 
            transition: transform 0.2s, box-shadow 0.2s;
            color: white;
            text-transform: uppercase;
        }
        .btn-base:hover { transform: translateY(-2px); }

        .btn-rom { background: linear-gradient(135deg, #ff69b4, #ff1493); box-shadow: 0 4px 10px rgba(255, 105, 180, 0.3); }
        .btn-coq { background: linear-gradient(135deg, #ff9100, #ed8002); box-shadow: 0 4px 10px rgba(237, 128, 2, 0.3); }
        .btn-pic { background: linear-gradient(135deg, #ff3d00, #dd2c00); box-shadow: 0 4px 10px rgba(255, 61, 0, 0.3); }
        .btn-pro { background: linear-gradient(135deg, #a855f7, #7e22ce); box-shadow: 0 4px 10px rgba(168, 85, 247, 0.3); }

        /* EFECTO BARRIDO DEGRADADO TURQUESA DE CARGA */
        @keyframes skeleton-glow {
            0% { background-position: 100% 0; }
            100% { background-position: -100% 0; }
        }

        #res { 
            background: #2a2a2a; 
            padding: 18px; 
            border-radius: 12px; 
            text-align: left; 
            white-space: pre-wrap; 
            margin-top: 20px; 
            border-left: 5px solid #00D4FF;
            min-height: 80px; 
            font-size: 15px; 
            line-height: 1.5;
            transition: all 0.3s ease;
        }

        .skeleton-loading {
            background: linear-gradient(90deg, #1e1e1e 25%, #003647 50%, #1e1e1e 75%) !important;
            background-size: 200% 100% !important;
            animation: skeleton-glow 1.4s infinite linear !important;
            color: transparent !important;
            user-select: none;
            pointer-events: none;
        }
    </style>
</head>
<body>

    <div class="container">
        <h2>🤖 Spark IA</h2>
        <div class="subtitle">Asistente de Conquista v6.0 (Visión Directa)</div>

        <div class="upload-area" onclick="document.getElementById('file-input').click();">
            <span id="upload-text">📸 Subir captura de pantalla del chat</span>
            <input type="file" id="file-input" accept="image/*" onchange="cargarImagen(event)">
            <img id="preview-img" alt="Vista previa">
        </div>

        <textarea id="texto-adicional" placeholder="Detalle extra (Opcional). Ej: Se llama Valeria, o contexto especial..."></textarea>

        <div class="grid-botones">
            <button class="btn-base btn-rom" onclick="generarRespuesta('Romántico')">💖 Romántico</button>
            <button class="btn-base btn-coq" onclick="generarRespuesta('Coqueto')">😏 Coqueto</button>
            <button class="btn-base btn-pic" onclick="generarRespuesta('Picante')">🔥 Picante</button>
            <button class="btn-base btn-pro" onclick="generarRespuesta('Provocativo')">😈 Provocativo</button>
        </div>

        <div id="res">Sube una captura de pantalla del chat y presiona un botón para analizar la conversación en vivo.</div>
    </div>

    <script>
        let imagenBase64 = null;

        function cargarImagen(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagenBase64 = e.target.result;
                    const preview = document.getElementById('preview-img');
                    preview.src = imagenBase64;
                    preview.style.display = 'block';
                    document.getElementById('upload-text').innerHTML = '✅ Imagen lista para analizar';
                };
                reader.readAsDataURL(file);
            }
        }

        async function generarRespuesta(modo) {
            const resDiv = document.getElementById('res');
            const textoExtra = document.getElementById('texto-adicional').value;

            if (!imagenBase64 && !textoExtra.trim()) {
                resDiv.innerText = "⚠️ Por favor sube una imagen del chat o escribe un contexto.";
                return;
            }

            // Iniciar efecto de carga turquesa
            resDiv.classList.add('skeleton-loading');
            resDiv.innerText = "Analizando chat con visión directa...";

            try {
                const response = await fetch('/procesar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        imagen: imagenBase64, 
                        texto_extra: textoExtra, 
                        modo: modo 
                    })
                });

                const data = await response.json();
                resDiv.classList.remove('skeleton-loading');

                if (data.respuesta) {
                    resDiv.innerHTML = data.respuesta;
                } else {
                    resDiv.innerText = "❌ Error: " + (data.error || "No se pudo procesar.");
                }
            } catch (err) {
                resDiv.classList.remove('skeleton-loading');
                resDiv.innerText = "❌ Error de conexión al servidor.";
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
    if not client:
        return jsonify({'error': 'GROQ_API_KEY no configurada en las variables de entorno.'}), 500

    data = request.json
    imagen_b64 = data.get('imagen')
    texto_extra = data.get('texto_extra', '')
    modo = data.get('modo', 'Coqueto')

    prompt_sistema = f"""
Eres un experto estratega en seducción, citas y habilidades sociales.
Tu tarea es analizar la captura de pantalla de un chat de WhatsApp/Instagram/Tinder recibida y generar 3 opciones de respuesta en modo: **{modo}**.

INSTRUCCIONES CLAVE:
1. Mira detalladamente la imagen: identifica quién envió el último mensaje, la vibra de la conversación, el tono y los emojis presentes.
2. Si hay un texto de contexto extra suministrado por el usuario, tómalo en cuenta: "{texto_extra}".
3. Genera 3 opciones de respuesta breves, naturales, fluidas y muy efectivas.
4. Usa emojis de forma sutil que encajen con el modo {modo}.
5. Presenta la respuesta numerada del 1 al 3 directamente sin intros aburridas.
"""

    messages = []
    
    if imagen_b64:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_sistema},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": imagen_b64
                    }
                }
            ]
        })
    else:
        messages.append({
            "role": "user",
            "content": f"{prompt_sistema}\nContexto: {texto_extra}"
        })

    try:
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        respuesta_texto = completion.choices[0].message.content
        return jsonify({'respuesta': respuesta_texto})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
