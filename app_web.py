from flask import Flask, render_template_string, request, jsonify
import requests
import os

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
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #121212; color: white; font-family: 'Segoe UI', sans-serif; padding: 20px; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 500px; background: #1a1a1a; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        
        h2 { color: #bb86fc; text-align: center; margin-bottom: 5px; font-size: 24px; }
        .subtitle { color: #888; font-size: 13px; text-align: center; margin-bottom: 20px; }
        
        /* DISEÑO VERTICAL ORIGINAL EXCLUSIVO */
        .file-zone {
            border: 2px dashed #8A2BE2;
            border-radius: 15px;
            padding: 20px;
            background: rgba(30, 30, 30, 0.5);
            cursor: pointer;
            text-align: center;
            margin-bottom: 15px;
            transition: 0.3s;
        }
        .file-zone:hover { border-color: #00D4FF; background: rgba(0, 212, 255, 0.05); }
        .file-zone input { display: none; }
        .file-zone p { margin: 5px 0; font-size: 14px; color: #aaa; }
        .preview-img { max-height: 90px; display: none; margin: 10px auto; border-radius: 8px; border: 1px solid #8A2BE2; }

        .section-divider { color: #555; font-size: 11px; margin: 10px 0; text-align: center; letter-spacing: 1px; }

        textarea { 
            width: 100%; 
            height: 130px; 
            background: rgba(30, 30, 30, 0.6); 
            color: #ffffff; 
            border: 2px solid #8A2BE2; 
            border-radius: 15px; 
            padding: 12px; 
            font-family: 'Segoe UI', sans-serif; 
            font-size: 13px;
            outline: none;
            box-shadow: 0 0 10px rgba(138, 43, 226, 0.1);
            transition: 0.3s ease;
            resize: none;
            margin-bottom: 15px;
        }
        textarea:focus { border-color: #00D4FF; box-shadow: 0 0 15px rgba(0, 212, 255, 0.3); }
        
        /* MATRIZ DE BOTONES SIMÉTRICA 2X3 */
        .buttons-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 15px;
        }
        
        /* Todos los botones miden exactamente lo mismo */
        .grid-btn {
            border: none; 
            height: 50px; 
            border-radius: 12px; 
            font-weight: bold; 
            font-size: 13px; 
            cursor: pointer; 
            transition: 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            color: white;
            width: 100%;
        }
        .grid-btn:hover { transform: translateY(-2px); }
        
        .btn-rom { background-color: #ee82ee; }
        .btn-rom:hover { box-shadow: 0 5px 12px rgba(238, 130, 238, 0.4); }
        
        .btn-coq { background-color: #ed8002; }
        .btn-coq:hover { box-shadow: 0 5px 12px rgba(237, 128, 2, 0.4); }
        
        .btn-pic { background-color: #E63946; }
        .btn-pic:hover { box-shadow: 0 5px 12px rgba(230, 57, 70, 0.4); }
        
        .btn-prov { background-color: #a333ff; }
        .btn-prov:hover { box-shadow: 0 5px 12px rgba(163, 51, 255, 0.4); }
        
        .btn-init { background-color: #00b4d8; }
        .btn-init:hover { box-shadow: 0 5px 12px rgba(0, 180, 216, 0.4); }
        
        .btn-save { background-color: #00e5ff; color: #121212; }
        .btn-save:hover { box-shadow: 0 5px 12px rgba(0, 229, 255, 0.4); }
        
        .btn-clear { background: transparent; color: #555; border: 1px solid #333; padding: 6px; border-radius: 8px; cursor: pointer; width: 110px; margin: 0 auto 15px auto; display: block; transition: 0.3s; font-size: 11px; }
        .btn-clear:hover { color: #fff; border-color: #666; }
        
        #res { background: #222; padding: 15px; border-radius: 15px; text-align: left; white-space: pre-wrap; border-left: 5px solid #00D4FF; min-height: 60px; font-size: 14px; line-height: 1.5; box-shadow: inset 0 2px 10px rgba(0,0,0,0.3); }
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Spark IA</h2>
        <div class="subtitle">Asistente de Conquista v5.1</div>
        
        <div class="file-zone" onclick="document.getElementById('file-input').click()">
            <p>📸 <strong>Sube la captura de pantalla</strong></p>
            <p style="font-size: 12px; color: #777;" id="upload-status">Haz clic aquí para seleccionar el screenshot del chat</p>
            <input type="file" id="file-input" accept="image/*" onchange="previewAndProcessImage(this)">
            <img id="img-preview" class="preview-img" src="" alt="Vista previa">
        </div>
        
        <div class="section-divider">— TEXTO DEL CHAT O DETALLES DEL PERFIL —</div>
        
        <textarea id="chat-input" placeholder="Para responder un chat: aquí aparecerá el texto de tu captura.\\n\\nPara iniciar un chat: puedes dejarlo vacío o escribir algún gusto de ella..."></textarea>
        
        <div class="buttons-grid">
            <button class="grid-btn btn-rom" onclick="enviar('Romántico')">💖 ROMÁNTICO</button>
            <button class="grid-btn btn-coq" onclick="enviar('Coqueto')">😏 COQUETO</button>
            <button class="grid-btn btn-pic" onclick="enviar('Picante')">🔥 PICANTE</button>
            <button class="grid-btn btn-prov" onclick="enviar('Provocativo')">😈 PROVOCATIVO</button>
            <button class="grid-btn btn-init" onclick="enviar('Iniciar Chat')">✨ INICIAR CHAT</button>
            <button class="grid-btn btn-save" onclick="enviar('Salvar el Momento')">🚨 SALVAR MOMENTO</button>
        </div>
        
        <button class="btn-clear" onclick="limpiar()">🧹 Limpiar Todo</button>

        <div id="res">✨ Selecciona una opción estratégica para ver las sugerencias de la IA...</div>
    </div>

    <script>
        function limpiarTextoFront(textoBruto) {
            let lineas = textoBruto.split('\\n');
            let lineasFiltradas = [];
            lineas.forEach(linea => {
                let l = linea.trim();
                if (!l) return;
                if (/(p\\.?m\\.?|a\\.?m\\.?|\\d{2,4})/i.test(l)) {
                    if (/(talla|tala|tall|\\d+)/i.test(l)) return;
                }
                l = l.replace(/^[\\s|:\\.\\-]+/, '').trim();
                if (l) lineasFiltradas.push(l);
            });
            return lineasFiltradas.join('\\n');
        }

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
                    
                    Tesseract.recognize(e.target.result, 'spa')
                    .then(({ data: { text } }) => {
                        status.innerText = "✅ Conversación extraída correctamente.";
                        status.style.color = "#03dac6";
                        document.getElementById('chat-input').value = limpiarTextoFront(text); 
                    }).catch(err => {
                        status.innerText = "❌ Error al leer la imagen.";
                        status.style.color = "#E63946";
                    });
                }
                reader.readAsDataURL(input.files[0]);
            }
        }

        function limpiar() {
            document.getElementById('chat-input').value = "";
            document.getElementById('file-input').value = "";
            const preview = document.getElementById('img-preview');
            preview.src = "";
            preview.style.display = 'none';
            const status = document.getElementById('upload-status');
            status.innerText = "Haz clic aquí para seleccionar el screenshot del chat";
            status.style.color = "#aaa";
            document.getElementById('res').innerText = "✨ Selecciona una opción estratégica para ver las sugerencias de la IA...";
        }

        function enviar(modoEstratega) {
            const resDiv = document.getElementById('res');
            const entradaTexto = document.getElementById('chat-input').value.trim();

            // CORRECCIÓN: Si es para iniciar chat, PERMITIR que la caja esté vacía
            if (entradaTexto === "" && modoEstratega !== 'Iniciar Chat') {
                alert("Por favor, introduce texto o sube una captura primero para responder.");
                return;
            }

            resDiv.innerText = "⏳ Spark IA está analizando estratégicamente...";
            ejecutarPeticion({ data: entradaTexto, mode: modoEstratega });
        }

        function ejecutarPeticion(payload) {
            const resDiv = document.getElementById('res');
            fetch('/generar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => { resDiv.innerText = data.resultado; })
            .catch(error => { resDiv.innerText = "❌ Error en el servidor al conectar con la IA."; });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generar', methods=['POST'])
def generar():
    data = request.json
    contenido = data.get('data', '').strip()
    modo = data.get('mode')
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    if modo == 'Iniciar Chat':
        # Cambiamos el prompt del sistema para que maneje de forma maestra el caso en blanco
        system_prompt = (
            "Eres un maestro supremo del carisma y experto en crear mensajes rompehielos letales para apps de citas. "
            "Tu misión es dar exactamente 3 opciones CORTAS, magnéticas e intrigantes para iniciar una conversación desde cero. "
            "REGLA DE ORO: Cero formalismos aburridos, cero saludos clichés como 'Hola cómo estás'. Deben ser abridores que generen curiosidad inmediata. "
            "Si el usuario te da detalles del perfil, úsalos con ingenio. Si el campo viene vacío, genera 3 abridores universales ganadores, divertidos y audaces. "
            "Formato estricto: Entrega exclusivamente las 3 opciones en una lista numerada (1, 2, 3). Sin introducciones ni saludos de tu parte."
        )
        user_prompt = f"Detalles provistos por el usuario: '{contenido if contenido else 'Ninguno, dame 3 abridores espectaculares desde cero'}'."
    else:
        system_prompt = (
            f"Eres un estratega experto en carisma y citas rápidas. "
            f"Vas a recibir una conversación de chat. Sabes perfectamente que la primera línea 'Tú' corresponde al usuario, "
            f"y los mensajes siguientes son la respuesta directa de la otra persona (ella). "
            f"Tu tarea crucial es responder ÚNICAMENTE al último mensaje enviado por ella, usando el contexto anterior para que tenga sentido. "
            f"Generas exactamente 3 opciones de réplica cortas, fluidas, magnéticas y auténticas. "
            f"ENFOQUE SEGÚN MODO SELECCIONADO ({modo}): "
            f"- Romántico: Atento, sutil, conectando lindo con alta seguridad. "
            f"- Coqueto: Divertido, ingenioso, pícaro, haciéndola sonreír. "
            f"- Picante: Atrevido, directo, magnético, con clase y misterio. "
            f"- Provocativo: Un reto juguetón, usando psicología inversa. "
            f"- Salvar el Momento: Un salvavidas de emergencia. Si ella fue cortante o dejó de responder, genera respuestas ingeniosas con humor o giros audaces para revivir el chat. "
            f"Formato estricto: Devuelve exclusivamente las 3 opciones en una lista numerada (1, 2, 3). Sin introducciones ni explicaciones."
        )
        user_prompt = f"Conversación:\n{contenido}\n\nGenera 3 respuestas perfectas en modo {modo}."

    payload_final = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.85
    }

    try:
        r_final = requests.post(url, headers=headers, json=payload_final)
        res_final = r_final.json()
        
        if 'choices' in res_final and len(res_final['choices']) > 0:
            resultado = res_final['choices'][0]['message']['content']
        else:
            resultado = f"Error en la respuesta de la API. Detalles: {res_final}"
            
        return jsonify({"resultado": resultado})
    except Exception as e:
        return jsonify({"resultado": f"Error en el motor de la IA: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
