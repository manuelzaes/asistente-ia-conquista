from flask import Flask, render_template_string, request, jsonify
import requests
import os
import re

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
        
        .tabs { display: flex; justify-content: space-around; margin-bottom: 20px; background: #1e1e1e; border-radius: 12px; padding: 5px; }
        .tab-btn { background: transparent; color: #888; border: none; padding: 10px 20px; font-weight: bold; cursor: pointer; transition: 0.3s; width: 50%; border-radius: 8px; }
        .tab-btn.active { background: #8A2BE2; color: white; box-shadow: 0 0 10px rgba(138, 43, 226, 0.5); }
        
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

        .btn-rom, .btn-coq, .btn-pic, .btn-prov {
            border: none; padding: 15px; border-radius: 12px; font-weight: bold; font-size: 16px; cursor: pointer; width: 100%; margin-bottom: 12px; transition: 0.3s ease;
        }
        .btn-rom { background-color: #ee82ee; color: white; box-shadow: 0 0 15px rgba(138, 43, 226, 0.4); }
        .btn-rom:hover { box-shadow: 0 0 25px rgba(138, 43, 226, 0.8); transform: scale(1.01); }
        .btn-coq { background-color: #ed8002; color: white; box-shadow: 0 0 15px rgba(237, 128, 2, 0.4); }
        .btn-coq:hover { box-shadow: 0 0 25px rgba(237, 128, 2, 0.8); transform: scale(1.01); }
        .btn-pic { background-color: #E63946; color: white; box-shadow: 0 0 15px rgba(230, 57, 70, 0.4); }
        .btn-pic:hover { box-shadow: 0 0 25px rgba(230, 57, 70, 0.8); transform: scale(1.01); }
        .btn-prov { background-color: #a333ff; color: white; box-shadow: 0 0 15px rgba(163, 51, 255, 0.4); }
        .btn-prov:hover { box-shadow: 0 0 25px rgba(163, 51, 255, 0.8); transform: scale(1.01); }
        
        .btn-clear { background: transparent; color: #888; border: 1px solid #444; padding: 10px; border-radius: 10px; cursor: pointer; width: 50%; margin: 10px auto; display: block; transition: 0.3s; }
        .btn-clear:hover { color: #fff; border-color: #fff; background-color: rgba(255, 255, 255, 0.1); }
        
        #res { background: #1e1e1e; padding: 15px; border-radius: 10px; text-align: left; white-space: pre-wrap; margin-top: 20px; border-left: 5px solid #03dac6; min-height: 50px; font-size: 15px; line-height: 1.5; }
        h2 { color: #bb86fc; margin-bottom: 5px; }
        .subtitle { color: #888; font-size: 14px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Spark IA</h2>
        <div class="subtitle">Asistente Avanzado de Conquista v3.8</div>
        
        <div class="tabs">
            <button class="tab-btn active" id="tab-responder" onclick="cambiarModo('responder')">💬 Responder Chat</button>
            <button class="tab-btn" id="tab-iniciar" onclick="cambiarModo('iniciar')">✨ Iniciar Chat</button>
        </div>
        
        <div id="section-responder">
            <div class="file-zone" onclick="document.getElementById('file-input').click()">
                <p>📸 <strong>Sube la captura de pantalla</strong></p>
                <p style="font-size: 12px;" id="upload-status">Haz clic aquí para seleccionar el screenshot del chat</p>
                <input type="file" id="file-input" accept="image/*" onchange="previewAndProcessImage(this)">
                <img id="img-preview" class="preview-img" src="" alt="Vista previa">
            </div>
            <p style="color: #666; margin: 10px 0;">— CONTEXTO DETECTADO —</p>
            <textarea id="chat" placeholder="Aquí aparecerá la conversación limpia de la captura..."></textarea>
        </div>
        
        <div id="section-iniciar" style="display: none;">
            <textarea id="intereses" placeholder="Ejemplo: Se llama Lucía, le encanta entrenar en el gym y ver anime. Parece alguien alegre..."></textarea>
        </div>
        
        <div style="margin-top: 20px;">
            <button class="btn-rom" onclick="enviar('Romántico')">💖 MODO ROMÁNTICO</button>
            <button class="btn-coq" onclick="enviar('Coqueto')">😏 MODO COQUETO</button>
            <button class="btn-pic" onclick="enviar('Picante')">🔥 MODO PICANTE</button>
            <button class="btn-prov" onclick="enviar('Provocativo')">😈 MODO PROVOCATIVO</button>
            <button class="btn-clear" onclick="limpiar()">🧹 Limpiar Todo</button>
        </div>

        <div id="res">✨ Las sugerencias personalizadas aparecerán aquí...</div>
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
            document.getElementById('intereses').value = "";
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
            resDiv.innerText = "⏳ Spark IA está analizando estratégicamente...";

            if (modoApp === 'responder') {
                const chatTexto = document.getElementById('chat').value;
                if (chatTexto.trim() !== "") {
                    ejecutarPeticion({ tipo: 'texto', data: chatTexto, modo: modoEstratega });
                } else {
                    alert("Por favor, sube una captura.");
                    resDiv.innerText = "✨ Las sugerencias aparecerán aquí...";
                }
            } else {
                const datosPerfil = document.getElementById('intereses').value;
                if (!datosPerfil.trim()) {
                    alert("Por favor, escribe algunos detalles del perfil.");
                    resDiv.innerText = "✨ Las sugerencias aparecerán aquí...";
                    return;
                }
                ejecutarPeticion({ tipo: 'iniciar', data: datosPerfil, modo: modoEstratega });
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
    """
    Filtro inteligente para quitar horas, palabras fantasma del OCR 
    y formatear correctamente los emisores.
    """
    lineas = texto.split('\n')
    lineas_limpias = []
    
    for linea in lineas:
        l = linea.strip()
        if not l:
            continue
            
        # 1. Quitar basuras comunes de horas del OCR como "515 p.m.", "Talla 5:15", "a.m.", etc.
        if re.search(r'(?i)(p\.?m\.?|a\.?m\.?|\d{2,4}\s*(pm|am)?)', l):
            if re.search(r'(?i)(talla|tala|tall|\d+)', l):
                continue
        
        # 2. Limpiar barras verticales residuales del OCR
        l = re.sub(r'^[\s|:.\-]+', '', l).strip()
        
        if l:
            lineas_limpias.append(l)
            
    return "\n".join(lineas_limpias)

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generar', methods=['POST'])
def generar():
    data = request.json
    tipo = data.get('tipo') 
    contenido = data.get('data')
    modo = data.get('modo')
    
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
            f"Formato estricto: Entrega exclusivamente las 3 opciones en una lista numerada (1, 2, 3), listas para copiar y mandar. Sin introducciones ni saludos."
        )
        user_prompt = f"Detalles del perfil o gustos de la chica: '{contenido}'. Fabrícame las 3 mejores opciones."
    else:
        texto_filtrado = limpiar_basura_ocr(contenido)
        
        system_prompt = (
            f"Eres un estratega experto en carisma y citas rápidas. "
            f"Vas a recibir una conversación limpia. Sabes perfectamente que las líneas que comiencen con o estén bajo la etiqueta 'Tú' corresponden al usuario, "
            f"y los mensajes siguientes son la respuesta directa que la otra persona (ella) envió. "
            f"Tu tarea crucial es responder ÚNICAMENTE al último mensaje enviado por ella, usando el contexto anterior para que tenga sentido. "
            f"Genera exactamente 3 opciones de réplica cortas, fluidas, magnéticas y que suenen 100% humanas. "
            f"ENFOQUE SEGÚN MODO SELECCIONADO ({modo}): "
            f"- Romántico: Atento, sutil, conectando de forma linda pero con alta seguridad. "
            f"- Coqueto: Divertido, ingenioso, con una pizca de picardía que la haga sonreír. "
            f"- Picante: Atrevido, directo, magnético, rompiendo el hielo con mucha clase y misterio. "
            f"- Provocativo: Un reto juguetón, usando un dilema divertido o psicología inversa para que busque tu aprobación. "
            f"Formato estricto: Devuelve exclusivamente las 3 opciones en una lista numerada (1, 2, 3). Sin introducciones ni explicaciones de ningún tipo."
        )
        user_prompt = f"Conversación procesada:\n{texto_filtrado}\n\nGenera 3 respuestas perfectas en base al último mensaje recibido en modo {modo}."

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
