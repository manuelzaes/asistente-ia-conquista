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
        .container { width: 100%; max-width: 650px; background: #1a1a1a; padding: 20px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        
        h2 { color: #bb86fc; text-align: center; margin-bottom: 5px; font-size: 24px; }
        .subtitle { color: #888; font-size: 13px; text-align: center; margin-bottom: 20px; }
        
        /* Pestañas de Navigation */
        .tabs { display: flex; justify-content: space-around; margin-bottom: 15px; background: #262626; border-radius: 12px; padding: 4px; }
        .tab-btn { background: transparent; color: #888; border: none; padding: 8px 15px; font-weight: bold; cursor: pointer; transition: 0.3s; width: 50%; border-radius: 8px; font-size: 14px; }
        .tab-btn.active { background: #8A2BE2; color: white; box-shadow: 0 0 10px rgba(138, 43, 226, 0.5); }
        
        /* DISEÑO EN HORIZONTAL */
        .grid-inputs {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }
        .input-box {
            flex: 1;
            min-width: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        /* Zona de Carga */
        .file-zone {
            border: 2px dashed #8A2BE2;
            border-radius: 15px;
            padding: 15px;
            background: rgba(30, 30, 30, 0.6);
            cursor: pointer;
            text-align: center;
            height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: 0.3s;
        }
        .file-zone:hover { border-color: #00D4FF; background: rgba(0, 212, 255, 0.05); }
        .file-zone input { display: none; }
        .file-zone p { margin: 2px 0; font-size: 13px; color: #aaa; }
        .preview-img { max-height: 50px; display: none; margin-top: 5px; border-radius: 6px; border: 1px solid #8A2BE2; }

        /* Cuadro de texto */
        textarea { 
            width: 100%; 
            height: 140px; 
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
        }
        textarea:focus { border-color: #00D4FF; box-shadow: 0 0 15px rgba(0, 212, 255, 0.3); }
        
        /* REJILLA MATRIZ 2X2 */
        .buttons-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .btn-rom, .btn-coq, .btn-pic, .btn-prov {
            border: none; 
            padding: 12px; 
            border-radius: 12px; 
            font-weight: bold; 
            font-size: 14px; 
            cursor: pointer; 
            transition: 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .btn-rom { background-color: #ee82ee; color: white; }
        .btn-rom:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(138, 43, 226, 0.5); }
        
        .btn-coq { background-color: #ed8002; color: white; }
        .btn-coq:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(237, 128, 2, 0.5); }
        
        .btn-pic { background-color: #E63946; color: white; }
        .btn-pic:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(230, 57, 70, 0.5); }
        
        .btn-prov { background-color: #a333ff; color: white; }
        .btn-prov:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(163, 51, 255, 0.5); }
        
        .btn-clear { background: transparent; color: #666; border: 1px solid #333; padding: 6px; border-radius: 8px; cursor: pointer; width: 120px; margin: 0 auto 15px auto; display: block; transition: 0.3s; font-size: 12px; }
        .btn-clear:hover { color: #fff; border-color: #aaa; }
        
        #res { background: #222; padding: 15px; border-radius: 15px; text-align: left; white-space: pre-wrap; border-left: 5px solid #00D4FF; min-height: 60px; font-size: 14px; line-height: 1.5; box-shadow: inset 0 2px 10px rgba(0,0,0,0.3); }

        @media (max-width: 480px) {
            .grid-inputs { flex-direction: column; gap: 10px; }
            .file-zone, textarea { height: 120px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Spark IA</h2>
        <div class="subtitle">Asistente de Conquista Compacto v4.0</div>
        
        <div class="tabs">
            <button class="tab-btn active" id="tab-responder" onclick="cambiarModo('responder')">💬 Responder Chat</button>
            <button class="tab-btn" id="tab-iniciar" onclick="cambiarModo('iniciar')">✨ Iniciar Chat</button>
        </div>
        
        <div id="section-responder">
            <div class="grid-inputs">
                <div class="input-box">
                    <div class="file-zone" onclick="document.getElementById('file-input').click()">
                        <p>📸 <strong>Captura</strong></p>
                        <p style="font-size: 11px; color: #777;" id="upload-status">Sube el screenshot aquí</p>
                        <input type="file" id="file-input" accept="image/*" onchange="previewAndProcessImage(this)">
                        <img id="img-preview" class="preview-img" src="" alt="Vista previa">
                    </div>
                </div>
                <div class="input-box">
                    <textarea id="chat" placeholder="Texto detectado o pégalo de forma manual..."></textarea>
                </div>
            </div>
        </div>
        
        <div id="section-iniciar" style="display: none; margin-bottom: 15px;">
            <textarea id="intereses" placeholder="Ejemplo: Se llama Lucía, le gusta ir al gym y el anime. Pídele salir de forma divertida..."></textarea>
        </div>
        
        <div class="buttons-container">
            <button class="btn-rom" onclick="enviar('Romántico')">💖 ROMÁNTICO</button>
            <button class="btn-coq" onclick="enviar('Coqueto')">😏 COQUETO</button>
            <button class="btn-pic" onclick="enviar('Picante')">🔥 PICANTE</button>
            <button class="btn-prov" onclick="enviar('Provocativo')">😈 PROVOCATIVO</button>
        </div>
        
        <button class="btn-clear" onclick="limpiar()">🧹 Limpiar Todo</button>

        <div id="res">✨ Las sugerencias estratégicas aparecerán aquí directamente...</div>
    </div>

    <script>
        let modoApp = 'responder';

        function cambiarModo(modo) {
            modoApp = modo;
            document.getElementById('tab-responder').classList.toggle('active', modo === 'responder');
            document.getElementById('tab-iniciar').classList.toggle('active', modo === 'iniciar');
            document.getElementById('section-responder').style.display = modo === 'responder' ? 'block' : 'none';
            document.getElementById('section-iniciar').style.display = modo === 'iniciar' ? 'block' : 'none';
        }

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
                status.innerText = "⏳ Leyendo...";
                status.style.color = "#00D4FF";
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    
                    Tesseract.recognize(e.target.result, 'spa')
                    .then(({ data: { text } }) => {
                        status.innerText = "✅ ¡Listo!";
                        status.style.color = "#03dac6";
                        document.getElementById('chat').value = limpiarTextoFront(text); 
                    }).catch(err => {
                        status.innerText = "❌ Error";
                        status.style.color = "#E63946";
                    });
                }
                reader.readAsDataURL(input.files[0]);
            }
        }

        function limpiar() {
            document.getElementById('chat').value = "";
            document.getElementById('intereses').value = "";
            document.getElementById('file-input').value = "";
            const preview = document.getElementById('img-preview');
            preview.src = "";
            preview.style.display = 'none';
            const status = document.getElementById('upload-status');
            status.innerText = "Sube el screenshot aquí";
            status.style.color = "#aaa";
            document.getElementById('res').innerText = "✨ Las sugerencias estratégicas aparecerán aquí directamente...";
        }

        function enviar(modoEstratega) {
            const resDiv = document.getElementById('res');
            resDiv.innerText = "⏳ Spark IA está analizando estratégicamente...";

            if (modoApp === 'responder') {
                const chatTexto = document.getElementById('chat').value;
                if (chatTexto.trim() !== "") {
                    ejecutarPeticion({ tipo: 'texto', data: chatTexto, mode: modoEstratega });
                } else {
                    alert("Por favor, sube una captura.");
                    resDiv.innerText = "✨ Las sugerencias estratégicas aparecerán aquí directamente...";
                }
            } else {
                const datosPerfil = document.getElementById('intereses').value;
                if (!datosPerfil.trim()) {
                    alert("Por favor, escribe algunos detalles del perfil.");
                    resDiv.innerText = "✨ Las sugerencias estratégicas aparecerán aquí directamente...";
                    return;
                }
                ejecutarPeticion({ tipo: 'iniciar', data: datosPerfil, mode: modoEstratega });
            }
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
            .catch(error => { resDiv.innerText = "❌ Error en el servidor."; });
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
    tipo = data.get('tipo') 
    contenido = data.get('data')
    modo = data.get('mode')
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    if tipo == 'iniciar':
        system_prompt = (
            f"Eres un maestro del carisma y experto en crear mensajes rompehielos para apps de citas. "
            f"Tu misión es dar exactamente 3 opciones CORTAS e impactantes para iniciar la conversación basado en la descripción dada. "
            f"REGLA DE ORO: Cero formalismos, nada de clichés aburridos ni piropos genéricos de internet. "
            f"Alinea las 3 opciones de forma creativa con el tono: {modo}. "
            f"Formato estricto: Entrega exclusivamente las 3 opciones en una lista numerada (1, 2, 3). Sin introducciones ni saludos."
        )
        user_prompt = f"Detalles del perfil: '{contenido}'."
    else:
        system_prompt = (
            f"Eres un estratega experto en carisma y citas rápidas. "
            f"Vas a recibir una conversación de chat. Sabes perfectamente que la primera línea 'Tú' corresponde al usuario, "
            f"y los mensajes siguientes son la respuesta directa de la otra persona (ella). "
            f"Tu tarea crucial es responder ÚNICAMENTE al último mensaje enviado por ella, usando el contexto anterior para que tenga sentido. "
            f"Genera exactamente 3 opciones de réplica cortas, fluidas, magnéticas y auténticas. "
            f"ENFOQUE SEGÚN MODO SELECCIONADO ({modo}): "
            f"- Romántico: Atento, sutil, conectando lindo con alta seguridad. "
            f"- Coqueto: Divertido, ingenioso, pícaro, haciéndola sonreír. "
            f"- Picante: Atrevido, directo, magnético, con clase y misterio. "
            f"- Provocativo: Un reto juguetón, usando psicología inversa. "
            f"Formato estricto: Devuelve exclusivamente las 3 opciones en una lista numerada (1, 2, 3). Sin introducciones ni explicaciones."
        )
        user_prompt = f"Conversación:\n{contenido}\n\nGenera 3 respuestas perfectas en modo {modo}."

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
        return jsonify({"resultado": f"Error en el motor: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
