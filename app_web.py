from flask import Flask, render_template_string, request, jsonify
import requests
import os

app = Flask(__name__)

# 1. CONFIGURACIÓN: API KEY de Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spark IA - Tu Asistente de Conquista</title>
    <link rel="icon" href="https://fav.farm/⚡" />
    <!-- Cargamos el lector de imágenes ultra rápido directamente en el navegador -->
    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
    <style>
        body { background: #121212; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 20px; }
        .container { max-width: 500px; margin: auto; }
        
        /* Pestañas de Navegación */
        .tabs { display: flex; justify-content: space-around; margin-bottom: 20px; background: #1e1e1e; border-radius: 12px; padding: 5px; }
        .tab-btn { background: transparent; color: #888; border: none; padding: 10px 20px; font-weight: bold; cursor: pointer; transition: 0.3s; width: 50%; border-radius: 8px; }
        .tab-btn.active { background: #8A2BE2; color: white; box-shadow: 0 0 10px rgba(138, 43, 226, 0.5); }
        
        /* Contenedores de Entrada */
        textarea { 
            width: 100%; 
            height: 120px; 
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
        
        /* Zona de carga de archivos / Capturas */
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

        /* Botones de Estilo */
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
        <div class="subtitle">Asistente Avanzado de Conquista v3.5</div>
        
        <!-- Pestañas -->
        <div class="tabs">
            <button class="tab-btn active" id="tab-responder" onclick="cambiarModo('responder')">💬 Responder Chat</button>
            <button class="tab-btn" id="tab-iniciar" onclick="cambiarModo('iniciar')">✨ Iniciar Chat</button>
        </div>
        
        <!-- Sección Opciones para Responder Chat (Texto o Imagen) -->
        <div id="section-responder">
            <div class="file-zone" onclick="document.getElementById('file-input').click()">
                <p>📸 <strong>Sube la captura de pantalla</strong></p>
                <p style="font-size: 12px;" id="upload-status">Haz clic aquí para seleccionar el screenshot del chat</p>
                <input type="file" id="file-input" accept="image/*" onchange="previewAndProcessImage(this)">
                <img id="img-preview" class="preview-img" src="" alt="Vista previa">
            </div>
            <p style="color: #666; margin: 10px 0;">— O TAMBIÉN PUEDES PEGAR EL TEXTO —</p>
            <textarea id="chat" placeholder="Escribe o pega el texto del chat aquí si no tienes captura..."></textarea>
        </div>
        
        <!-- Sección Opciones para Iniciar Chat desde cero -->
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
                status.innerText = "⏳ Leyendo captura... Por favor espera.";
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
                        status.innerText = "✅ ¡Captura leída! Pulsa un modo abajo.";
                        status.style.color = "#03dac6";
                        document.getElementById('chat').value = text; 
                    }).catch(err => {
                        status.innerText = "❌ Error al leer la imagen. Intenta escribir abajo.";
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
                    alert("Por favor, sube una captura o escribe el texto del chat.");
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
            f"Eres un maestro del carisma y experto en crear 'abrelatas' o mensajes rompehielos para apps de citas (como Liggo o Flechazo). "
            f"Tu misión es dar exactamente 3 opciones CORTAS e impactantes para iniciar la conversación basado en la descripción dada. "
            f"REGLA DE ORO: Cero formalismos, nada de clichés aburridos ni piropos genéricos de internet. "
            f"Alinea las 3 opciones de forma creativa con el tono: {modo}. "
            f"- Romántico: Atento, sutil, enfocado en conectar de forma linda pero con alta seguridad. "
            f"- Coqueto: Divertido, ingenioso, con una pizca de picardía que la haga sonreír. "
            f"- Picante: Atrevido, directo, magnético, rompiendo el hielo con mucha clase y misterio. "
            f"- Provocativo: Un reto juguetón, usando psicología inversa o un dilema divertido para que sienta ganas de responderte. "
            f"Formato estricto: Entrega exclusivamente las 3 opciones en una lista numerada (1, 2, 3), listas para copiar y mandar. Sin introducciones ni saludos."
        )
        user_prompt = f"Detalles del perfil o gustos de la chica: '{contenido}'. Fabrícame las 3 mejores opciones."
    else:
        # AQUÍ ESTÁ EL CAMBIO CLAVE: Entrenamos al modelo para que ordene el desastre del OCR
        system_prompt = (
            f"Eres un experto en carisma, seducción moderna y dinámicas de chat en apps de citas (como Liggo o Flechazo). "
            f"INSTRUCCIÓN DE FILTRADO OCR: El texto del chat que vas a recibir proviene de un lector óptico de imágenes, por lo que estará desordenado, mezclado con horas (p.m./a.m.) o marcas como 'Tú'. "
            f"Tu primer paso es analizar ese desorden de forma lógica, identificar cuál es el hilo real de la conversación y aislar el último mensaje que envió la otra persona (ella) para responderle directamente. "
            f"Tu misión es dar exactamente 3 opciones de respuestas cortas, fluidas, ingeniosas y que suenen 100% naturales, ideales para mensajería móvil. "
            f"REGLA DE ORO: Evita sonar artificial, robótico o formal. Prohibido ser arrogante, intenso o pesado. "
            f"Mantén siempre una vibra de alta confianza y tensión divertida. "
            f"ESTILOS DE RESPUESTA SEGÚN EL MODO SELECCIONADO ({modo}): "
            f"- Romántico: Dulce, tierno y detallista, pero moderno. Hazla sentir especial sin sonar necesitado. "
            f"- Coqueto: Pícaro, divertido y seguro. Usa cumplidos inesperados o réplicas ingeniosas que la hagan reír. "
            f"- Picante: Atrevido, magnético y directo. Genera tensión con mucha clase, elegancia y alta seguridad. "
            f"- Provocativo: Un reto juguetón. Aplica el 'tira y afloja'. Sé ese villano encantador que pone un desafío inteligente para que ella busque ganar tu atención. "
            f"Formato estricto: Entrega exclusivamente las 3 opciones en una lista numerada (1, 2, 3). No agregues introducciones, comentarios, ni textos extras antes o después."
        )
        user_prompt = f"Texto bruto del chat (OCR):\n{contenido}\n\nAnaliza la estructura, descubre qué me está diciendo ella al final y genérame las 3 mejores opciones en modo {modo}."

    # ENVIAMOS AL CEREBRO Llama 3.3 70B
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
