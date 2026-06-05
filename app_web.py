from flask import Flask, render_template_string, request, jsonify
import requests
import os
import re
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# CONFIGURACIÓN: API KEY de Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spark IA - Tu Asistente de Conquista</title>
    <link rel="icon" href="https://fav.farm/⚡" />
    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
    <style>
        body { background: #121212; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 20px; }
        .container { max-width: 500px; margin: auto; }
        
        textarea { 
            width: 100%; 
            height: 140px; 
            background: rgba(30, 30, 30, 0.7); 
            color: #ffffff; 
            border: 2px solid #8A2BE2; 
            border-radius: 15px; 
            padding: 15px; 
            font-family: 'Segoe UI', sans-serif; 
            font-size: 14px;
            outline: none;
            box-shadow: 0 0 10px rgba(138, 43, 226, 0.2);
            transition: 0.3s ease;
            resize: none;
            box-sizing: border-box;
        }
        textarea:focus { border-color: #00D4FF; box-shadow: 0 0 20px rgba(0, 212, 255, 0.4); background: #1e1e1e; }
        
        .file-zone {
            border: 2px dashed #8A2BE2;
            border-radius: 15px;
            padding: 20px;
            background: rgba(30, 30, 30, 0.5);
            cursor: pointer;
            margin-bottom: 15px;
            transition: 0.3s;
        }
        .file-zone:hover { border-color: #00D4FF; background: rgba(0, 212, 255, 0.05); }
        .file-zone input { display: none; }
        .file-zone p { margin: 5px 0; font-size: 14px; color: #aaa; }
        .preview-img { max-height: 100px; display: none; margin: 10px auto; border-radius: 8px; border: 1px solid #8A2BE2; }

        /* CUADRÍCULA DE BOTONES EXACTA DE LA TARDE (2 Columnas por 3 Filas) */
        .grid-botones {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-top: 20px;
        }

        .btn-base {
            border: none; 
            padding: 15px 10px; 
            border-radius: 12px; 
            font-weight: bold; 
            font-size: 14px; 
            cursor: pointer; 
            transition: 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .btn-base:hover { transform: scale(1.02); }

        /* Paleta de colores exacta de tu diseño anterior */
        .btn-rom { background-color: #ee82ee; box-shadow: 0 0 15px rgba(238, 130, 238, 0.3); }
        .btn-rom:hover { box-shadow: 0 0 25px rgba(238, 130, 238, 0.7); }
        
        .btn-coq { background-color: #ed8002; box-shadow: 0 0 15px rgba(237, 128, 2, 0.3); }
        .btn-coq:hover { box-shadow: 0 0 25px rgba(237, 128, 2, 0.7); }
        
        .btn-pic { background-color: #E63946; box-shadow: 0 0 15px rgba(230, 57, 70, 0.3); }
        .btn-pic:hover { box-shadow: 0 0 25px rgba(230, 57, 70, 0.7); }
        
        .btn-prov { background-color: #a333ff; box-shadow: 0 0 15px rgba(163, 51, 255, 0.3); }
        .btn-prov:hover { box-shadow: 0 0 25px rgba(163, 51, 255, 0.7); }

        .btn-iniciar-modo { background-color: #00b4d8; box-shadow: 0 0 15px rgba(0, 180, 216, 0.3); }
        .btn-iniciar-modo:hover { box-shadow: 0 0 25px rgba(0, 180, 216, 0.7); }

        .btn-salvar { background-color: #00d4ff; box-shadow: 0 0 15px rgba(0, 212, 255, 0.3); }
        .btn-salvar:hover { box-shadow: 0 0 25px rgba(0, 212, 255, 0.7); }

        /* Botón Limpiar estilizado abajo de la cuadrícula */
        .btn-limpiar-container { margin-top: 15px; display: flex; justify-content: center; }
        .btn-limpiar { background: #1e1e1e; border: 1px solid #333; color: #888; padding: 6px 16px; border-radius: 20px; font-size: 12px; cursor: pointer; transition: 0.3s; }
        .btn-limpiar:hover { background: #333; color: white; }
        
        #res { background: #1e1e1e; padding: 15px; border-radius: 10px; text-align: left; white-space: pre-wrap; margin-top: 20px; border-left: 5px solid #03dac6; min-height: 50px; font-size: 15px; line-height: 1.5; }
        h2 { color: #bb86fc; margin-bottom: 5px; }
        .subtitle { color: #888; font-size: 14px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Spark IA</h2>
        <div class="subtitle">Asistente de Conquista v5.1</div>
        
        <div class="file-zone" onclick="document.getElementById('file-input').click()">
            <p>📸 <strong>Sube la captura de pantalla</strong></p>
            <p style="font-size: 12px;" id="upload-status">Haz clic aquí para seleccionar el screenshot del chat</p>
            <input type="file" id="file-input" accept="image/*" onchange="previewAndProcessImage(this)">
            <img id="img-preview" class="preview-img" src="" alt="Vista previa">
        </div>

        <p style="color: #666; margin: 10px 0; font-size: 12px; letter-spacing: 1px;">— TEXTO DEL CHAT O DETALLES DEL PERFIL —</p>
        <textarea id="chat" placeholder="Para responder un chat: aquí aparecerá el texto de tu captura.\\n\\nPara iniciar un chat: puedes dejarlo vacío o escribir algún gusto de ella..."></textarea>
        
        <div class="grid-botones">
            <button class="btn-base btn-rom" onclick="enviar('Romántico')">💖 ROMÁNTICO</button>
            <button class="btn-base btn-coq" onclick="enviar('Coqueto')">😏 COQUETO</button>
            <button class="btn-base btn-pic" onclick="enviar('Picante')">🔥 PICANTE</button>
            <button class="btn-base btn-prov" onclick="enviar('Provocativo')">😈 PROVOCATIVO</button>
            <button class="btn-base btn-iniciar-modo" onclick="enviar('Iniciar chat')">✨ INICIAR CHAT</button>
            <button class="btn-base btn-salvar" onclick="enviar('Salvar el momento')">🚨 SALVAR MOMENTO</button>
        </div>

        <div class="btn-limpiar-container">
            <button class="btn-limpiar" onclick="limpiar()">🖌️ Limpiar Todo</button>
        </div>

        <div id="res">✨ Las sugerencias personalizadas aparecerán aquí...</div>
    </div>

    <script>
        function previewAndProcessImage(input) {
            const preview = document.getElementById('img-preview');
            const status = document.getElementById('upload-status');
            
            if (input.files && input.files[0]) {
                status.innerText = "⏳ Decodificando chat... Por favor espera.";
                status.style.color = "#00D4FF";
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    
                    Tesseract.recognize(
                        e.target.result,
                        'spa', 
                        { logger: m => console.log(m) }
                    ).then(({ data: { text } }) => {
                        status.innerText = "✅ Conversación extraída correctamente.";
                        status.style.color = "#03dac6";
                        document.getElementById('chat').value = text; 
                    }).catch(err => {
                        status.innerText = "❌ Error al leer la imagen.";
                        status.style.color = "#E63946";
                    });
                }
                reader.readAsDataURL(input.files[0]);
            }
        }

        function limpiar() {
            document.getElementById('chat').value = "";
            document.getElementById('file-input').value = "";
            const preview = document.getElementById('img-preview');
            preview.src = "";
            preview.style.display = 'none';
            const status = document.getElementById('upload-status');
            status.innerText = "Haz clic aquí para seleccionar el screenshot del chat";
            status.style.color = "#aaa";
            document.getElementById('res').innerText = "✨ Las sugerencias aparecerán aquí...";
        }

        function enviar(modoEstratega) {
            const resDiv = document.getElementById('res');
            const chatTexto = document.getElementById('chat').value;
            
            resDiv.innerText = "⏳ Spark IA está analizando estratégicamente...";

            // Si es iniciar chat puro y está vacío, pedir contexto
            if (modoEstratega === 'Iniciar chat' && chatTexto.trim() === "") {
                alert("Por favor, escribe algunos gustos o detalles en el cuadro de texto para armar los abridores.");
                resDiv.innerText = "✨ Las sugerencias aparecerán aquí...";
                return;
            }

            // Si intenta usar un modo de respuesta pero no hay texto
            if (modoEstratega !== 'Iniciar chat' && chatTexto.trim() === "") {
                alert("Por favor, sube una captura de pantalla o escribe el mensaje que quieres responder.");
                resDiv.innerText = "✨ Las sugerencias aparecerán aquí...";
                return;
            }

            // Enviamos todo unificado al backend
            fetch('/generar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ data: chatTexto, modo: modoEstratega })
            })
            .then(response => response.json())
            .then(data => {
                resDiv.innerText = data.resultado;
            })
            .catch(error => {
                resDiv.innerText = "❌ Error en el servidor. Inténtalo de nuevo.";
            });
        }
    </script>
</body>
</html>
"""

def limpiar_basura_ocr(texto):
    lineas = texto.split('\n')
    lineas_limpias = []
    for linea in lineas:
        l = linea.strip()
        if not l:
            continue
        if re.search(r'(?i)(p\.?m\.?|a\.?m\.?|\d{2,4}\s*(pm|am)?)', l):
            if re.search(r'(?i)(talla|tala|tall|\d+)', l):
                continue
        l = re.sub(r'^[\s|:.\-]+', '', l).strip()
        if l:
            lineas_limpias.append(l)
    return "\n".join(lineas_limpias)

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ping')
def ping():
    return jsonify({"status": "despierto"})

@app.route('/generar', methods=['POST'])
def generar():
    data = request.json
    contenido = data.get('data')
    modo = data.get('modo')
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    if modo == 'Iniciar chat':
        system_prompt = (
            f"Eres un maestro del carisma y experto en crear mensajes rompehielos para apps de citas. "
            f"Tu misión es dar exactamente 3 opciones CORTAS e impactantes para iniciar la conversación basado en los detalles dados. "
            f"REGLA DE ORO: Cero formalismos, nada de clichés aburridos ni piropos genéricos de internet. "
            f"Formato estricto: Entrega exclusivamente las 3 opciones en una lista numerada (1, 2, 3), listas para copiar y mandar. Sin introducciones ni saludos."
        )
        user_prompt = f"Detalles del perfil o gustos de la persona: '{contenido}'. Fabrícame las 3 mejores opciones."
    else:
        texto_filtrado = limpiar_basura_ocr(contenido)
        
        if modo == 'Salvar el momento':
            enfoque_modo = "Urgente, ingenioso y diseñado para revivir una conversación muerta, responder a un visto o salir elegantemente de un momento incómodo sin perder el valor."
        else:
            enfoque_modo = f"Alineado estrictamente al tono {modo}."

        system_prompt = (
            f"Eres un estratega experto en carisma y citas rápidas. "
            f"Vas a recibir una conversación limpia del OCR. Sabes perfectamente que las líneas de arriba corresponden al contexto "
            f"y los mensajes finales son lo que la otra persona envió. "
            f"Tu tarea crucial es responder ÚNICAMENTE al último mensaje enviado por ella, usando el contexto anterior para que tenga sentido. "
            f"Genera exactamente 3 opciones de réplica cortas, fluidas, magnéticas y que suenen 100% humanas. "
            f"ENFOQUE DE RESPUESTA: {enfoque_modo} "
            f"Formato estricto: Devuelve exclusivamente las 3 opciones en una lista numerada (1, 2, 3). Sin introducciones ni explicaciones de ningún tipo."
        )
        user_prompt = f"Conversación procesada:\n{texto_filtrado}\n\nGenera 3 respuestas perfectas en base al último mensaje recibido."

    payload_final = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.82
    }

    try:
        r_final = requests.post(url, headers=headers, json=payload_final)
        res_final = r_final.json()
        resultado = res_final['choices'][0]['message']['content']
        return jsonify({"resultado": resultado})
    except Exception as e:
        return jsonify({"resultado": f"Error en el motor de conquista: {str(e)}"})

def mantener_despierto():
    try:
        requests.get("https://asistente-ia-conquista.onrender.com/ping")
    except Exception:
        pass

scheduler = BackgroundScheduler()
scheduler.add_job(func=mantener_despierto, trigger="interval", minutes=10)
scheduler.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
