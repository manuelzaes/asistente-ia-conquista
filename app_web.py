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
            box-shadow: 0 0 15px rgba(138, 43, 226, 0.25);
            transition: 0.3s ease;
            resize: none;
            box-sizing: border-box;
        }
        textarea:focus { border-color: #00D4FF; box-shadow: 0 0 25px rgba(0, 212, 255, 0.45); background: #1e1e1e; }
        
        .file-zone {
            border: 2px dashed #8A2BE2;
            border-radius: 15px;
            padding: 20px;
            background: rgba(30, 30, 30, 0.5);
            cursor: pointer;
            margin-bottom: 15px;
            transition: 0.3s;
        }
        .file-zone:hover { border-color: #00D4FF; background: rgba(0, 212, 255, 0.05); box-shadow: 0 0 15px rgba(0, 212, 255, 0.2); }
        .file-zone input { display: none; }
        .file-zone p { margin: 5px 0; font-size: 14px; color: #aaa; }
        .preview-img { max-height: 100px; display: none; margin: 10px auto; border-radius: 8px; border: 1px solid #8A2BE2; }

        /* CUADRÍCULA DE BOTONES CON BRILLO AVANZADO */
        .grid-botones {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 14px;
            margin-top: 20px;
        }

        .btn-base {
            border: 1px solid rgba(255, 255, 255, 0.1); 
            padding: 16px 10px; 
            border-radius: 14px; 
            font-weight: bold; 
            font-size: 14px; 
            cursor: pointer; 
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .btn-base:hover { transform: translateY(-2px); }

        /* Paleta con Brillo Neon */
        .btn-rom { 
            background: linear-gradient(135deg, #ff71ce, #ee82ee); 
            box-shadow: 0 4px 15px rgba(238, 130, 238, 0.4), inset 0 0 10px rgba(255, 255, 255, 0.2); 
        }
        .btn-rom:hover { box-shadow: 0 6px 25px rgba(238, 130, 238, 0.8); }
        
        .btn-coq { 
            background: linear-gradient(135deg, #ff9100, #ed8002); 
            box-shadow: 0 4px 15px rgba(237, 128, 2, 0.4), inset 0 0 10px rgba(255, 255, 255, 0.2); 
        }
        .btn-coq:hover { box-shadow: 0 6px 25px rgba(237, 128, 2, 0.8); }
        
        .btn-pic { 
            background: linear-gradient(135deg, #ff4d5a, #E63946); 
            box-shadow: 0 4px 15px rgba(230, 57, 70, 0.4), inset 0 0 10px rgba(255, 255, 255, 0.2); 
        }
        .btn-pic:hover { box-shadow: 0 6px 25px rgba(230, 57, 70, 0.8); }
        
        .btn-prov { 
            background: linear-gradient(135deg, #b85cff, #a333ff); 
            box-shadow: 0 4px 15px rgba(163, 51, 255, 0.4), inset 0 0 10px rgba(255, 255, 255, 0.2); 
        }
        .btn-prov:hover { box-shadow: 0 6px 25px rgba(163, 51, 255, 0.8); }

        .btn-iniciar-modo { 
            background: linear-gradient(135deg, #00f5ff, #00b4d8); 
            box-shadow: 0 4px 15px rgba(0, 180, 216, 0.4), inset 0 0 10px rgba(255, 255, 255, 0.2); 
        }
        .btn-iniciar-modo:hover { box-shadow: 0 6px 25px rgba(0, 180, 216, 0.8); }

        .btn-salvar { 
            background: linear-gradient(135deg, #00fcfd, #00d4ff); 
            box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4), inset 0 0 10px rgba(255, 255, 255, 0.2); 
        }
        .btn-salvar:hover { box-shadow: 0 6px 25px rgba(0, 212, 255, 0.8); }

        /* Botón Limpiar Estilizado */
        .btn-limpiar-container { margin-top: 18px; display: flex; justify-content: center; }
        .btn-limpiar { background: #1a1a1a; border: 1px solid #333; color: #777; padding: 7px 20px; border-radius: 20px; font-size: 11px; font-weight: bold; letter-spacing: 0.5px; cursor: pointer; transition: 0.3s; }
        .btn-limpiar:hover { background: #2a2a2a; color: #fff; border-color: #666; box-shadow: 0 0 10px rgba(255,255,255,0.05); }
        
        #res { 
            background: #1e1e1e; 
            padding: 18px; 
            border-radius: 12px; 
            text-align: left; 
            white-space: pre-wrap; 
            margin-top: 22px; 
            border-left: 5px solid #00D4FF; 
            min-height: 50px; 
            font-size: 15px; 
            line-height: 1.6; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transition: background 0.3s ease;
        }
        h2 { color: #bb86fc; margin-bottom: 5px; font-size: 26px; font-weight: 800; letter-spacing: 0.5px; }
        .subtitle { color: #888; font-size: 13px; margin-bottom: 22px; font-weight: 500; }

        /* ========================================================
           NUEVOS ESTILOS INTERNOS: EFECTO SKELETON CELESTE/TURQUESA
           ======================================================== */
        @keyframes skeleton-glow {
            0% { background-position: 100% 0; }
            100% { background-position: -100% 0; }
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
        <div class="subtitle">Asistente de Conquista v5.5</div>
        
        <div class="file-zone" onclick="document.getElementById('file-input').click()">
            <p>📸 <strong>Sube la captura de pantalla</strong></p>
            <p style="font-size: 12px;" id="upload-status">Haz clic aquí para seleccionar el screenshot del chat</p>
            <input type="file" id="file-input" accept="image/*" onchange="previewAndProcessImage(this)">
            <img id="img-preview" class="preview-img" src="" alt="Vista previa">
        </div>

        <p style="color: #555; margin: 12px 0; font-size: 11px; font-weight: bold; letter-spacing: 1.2px;">— TEXTO DEL CHAT O DETALLES DEL PERFIL —</p>
        <textarea id="chat" placeholder="Para responder un chat: aquí aparecerá el texto de tu captura.\\n\\nPara iniciar un chat: puedes dejarlo vacío o escribir algún gusto de ella..."></textarea>
        
        <div class="grid-botones">
            <button class="btn-base btn-rom" onclick="enviar('Romántico')">💖 Romántico</button>
            <button class="btn-base btn-coq" onclick="enviar('Coqueto')">😏 Coqueto</button>
            <button class="btn-base btn-pic" onclick="enviar('Picante')">🔥 Picante</button>
            <button class="btn-base btn-prov" onclick="enviar('Provocativo')">😈 Provocativo</button>
            <button class="btn-base btn-iniciar-modo" onclick="enviar('Iniciar chat')">✨ Iniciar Chat</button>
            <button class="btn-base btn-salvar" onclick="enviar('Salvar el momento')">🚨 Salvar Momento</button>
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
            
            // CORRECCIÓN VISUAL: Activamos el barrido degradado turquesa
            resDiv.classList.add('skeleton-loading');
            resDiv.innerText = "Cargando..."; 

            if (modoEstratega !== 'Iniciar chat' && chatTexto.trim() === "") {
                alert("Por favor, sube una captura de pantalla o escribe el mensaje que quieres responder.");
                resDiv.classList.remove('skeleton-loading');
                resDiv.innerText = "✨ Las sugerencias aparecerán aquí...";
                return;
            }

            fetch('/generar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ data: chatTexto, modo: modoEstratega })
            })
            .then(response => response.json())
            .then(data => {
                // Quitamos el efecto y soltamos las respuestas limpias
                resDiv.classList.remove('skeleton-loading');
                resDiv.innerText = data.resultado;
            })
            .catch(error => {
                resDiv.classList.remove('skeleton-loading');
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

    cabecera_titulo = f"✨ OPCIONES MODO {modo.upper()}:\n\n"

    if modo == 'Iniciar chat':
        contexto_usuario = contenido.strip() if contenido else "intereses variados, divertida, casual y espontánea"
        system_prompt = (
            f"Eres un maestro del carisma y experto en crear mensajes rompehielos para apps de citas. "
            f"Tu misión es dar exactamente 3 opciones CORTAS, ingeniosas e impactantes para abrir el chat. "
            f"REGLA DE ORO: Cero formalismos, nada de clichés aburridos ni frases trilladas de internet. "
            f"Formato estricto: Entrega exclusivamente las 3 opciones en una lista numerada (1, 2, 3), listas para copiar y mandar. Sin introducciones ni saludos."
        )
        user_prompt = f"Detalles sugeridos para armar los abridores: '{contexto_usuario}'. Fabrícame las 3 mejores opciones."
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
            f"Genera exactamente 3 opciones de réplica cortas, fluidas, magnéticas y que suonen 100% humanas. "
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
        resultado_ia = res_final['choices'][0]['message']['content']
        
        resultado_combinado = cabecera_titulo + resultado_ia
        return jsonify({"resultado": resultado_combinado})
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
