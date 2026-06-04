from flask import Flask, render_template_string, request, jsonify
import requests
import os
import base64

app = Flask(__name__)

# 1. CONFIGURACIÓN: Pega tu API KEY de Groq aquí o configúrala en Render
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spark IA - Tu Asistente de Conquista</title>
    <link rel="icon" href="https://fav.farm/⚡" />
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
        <div class="subtitle">Asistente Avanzado de Conquista v3.0</div>
        
        <div class="tabs">
            <button class="tab-btn active" id="tab-responder" onclick="cambiarModo('responder')">💬 Responder Chat</button>
            <button class="tab-btn" id="tab-iniciar" onclick="cambiarModo('iniciar')">✨ Iniciar Chat</button>
        </div>
        
        <div id="section-responder">
            <div class="file-zone" onclick="document.getElementById('file-input').click()">
                <p>📸 <strong>Sube la captura de pantalla</strong></p>
                <p style="font-size: 12px;">Haz clic aquí para seleccionar el screenshot del chat</p>
                <input type="file" id="file-input" accept="image/*" onchange="previewImage(this)">
                <img id="img-preview" class="preview-img" src="" alt="Vista previa">
            </div>
            <p style="color: #666; margin: 10px 0;">— O TAMBIÉN PUEDES PEGAR EL TEXTO —</p>
            <textarea id="chat" placeholder="Escribe o pega el texto del chat aquí si no tienes captura..."></textarea>
        </div>
        
        <div id="section-iniciar" style="display: none;">
            <textarea id="intereses" placeholder="Ejemplo: Se llama Lucía, le encanta entrenar en el gym, ve anime (Naruto) y tiene fotos viajando. Parece alguien alegre y extrovertida..."></textarea>
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

        function previewImage(input) {
            const preview = document.getElementById('img-preview');
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
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
            document.getElementById('res').innerText = "✨ Las sugerencias aparecerán aquí...";
        }

        function enviar(modoEstratega) {
            const resDiv = document.getElementById('res');
            const fileInput = document.getElementById('file-input');
            
            resDiv.innerText = "⏳ Spark IA está analizando estratégicamente...";

            if (modoApp === 'responder') {
                const chatTexto = document.getElementById('chat').value;
                
                // Si hay una foto cargada, se procesa de forma prioritaria
                if (fileInput.files && fileInput.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const base64Image = e.target.result.split(',')[1];
                        ejecutarPeticion({ tipo: 'imagen', data: base64Image, modo: modoEstratega });
                    };
                    reader.readAsDataURL(fileInput.files[0]);
                } else if (chatTexto.trim() !== "") {
                    // Si no hay foto pero sí texto escrito
                    ejecutarPeticion({ tipo: 'texto', data: chatTexto, modo: modoEstratega });
                } else {
                    alert("Por favor, sube una captura de pantalla o pega el texto del chat.");
                    resDiv.innerText = "✨ Las sugerencias aparecerán aquí...";
                }
            } else {
                // Modo Iniciar Conversación desde Cero
                const datosPerfil = document.getElementById('intereses').value;
                if (!datosPerfil.trim()) {
                    alert("Por favor, escribe algunos gustos o detalles del perfil para fabricar los rompehielos.");
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
                resDiv.innerText = "❌ Error en el servidor. Revisa los logs de Render.";
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
    tipo = data.get('tipo') # 'texto', 'imagen' o 'iniciar'
    contenido = data.get('data')
    modo = data.get('modo')
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # CASO 1: EL USUARIO SUBIÓ UNA CAPTURA DE PANTALLA (IMAGEN)
    if tipo == 'imagen':
        # Primero usamos el modelo con ojos (Llama Vision) para extraer el chat de forma perfecta
        payload_vision = {
            "model": "llama-3.2-11b-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Transcribe exactamente el texto de este chat de app de citas. Solo devuelve la transcripción directa de lo que dicen las personas, sin comentarios adicionales."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{contenido}"}}
                    ]
                }
            ],
            "temperature": 0.1
        }
        try:
            r_vision = requests.post(url, headers=headers, json=payload_vision)
            res_vision = r_vision.json()
            chat_extraido = res_vision['choices'][0]['message']['content']
        except Exception as e:
            return jsonify({"resultado": f"Error al procesar los ojos de la IA (Vision): {str(e)}"})
        
        # Una vez extraído el texto, se lo mandamos al modelo experto en conquista
        texto_para_analizar = chat_extraido
    else:
        # Si es de texto o para iniciar, el contenido pasa directo
        texto_para_analizar = contenido

    # CONFIGURAMOS EL MENSAJE DEL SISTEMA SEGÚN EL MODO DEL PROYECTO
    if tipo == 'iniciar':
        system_prompt = (
            f"Eres un maestro del carisma y experto en crear 'abrelatas' o rompehielos para apps de citas (como Liggo o Flechazo). "
            f"Tu misión es dar exactamente 3 opciones CORTAS e impactantes para iniciar la conversación según la descripción enviada. "
            f"REGLA DE ORO: No uses frases hechas, clichés ni piropos básicos de internet. "
            f"Alinea las 3 opciones con el tono: {modo}. "
            f"- Romántico: Atento, sutil, enfocado en conectar de forma linda pero con personalidad. "
            f"- Coqueto: Divertido, ingenioso, con una pizca de picardía sana. "
            f"- Picante: Atrevido, directo y seguro, creando misterio instantáneo con mucha clase. "
            f"- Provocativo: Un reto divertido, usando psicología inversa o un juego para que ella quiera responder. "
            f"Formato estricto: Entrega exclusivamente las 3 opciones numeradas (1, 2, 3), listas para copiar y mandar. Cero explicaciones o introducciones."
        )
        user_prompt = f"Detalles del perfil o gustos: '{texto_para_analizar}'. Fabricame los 3 mejores mensajes de apertura."
    else:
        # Analizar conversación existente (ya sea que vino de texto directo o de OCR de imagen)
        system_prompt = (
            f"Eres un experto en carisma, seducción moderna y dinámicas de chat en apps de citas (como Liggo o Flechazo). "
            f"Tu misión es dar exactamente 3 opciones de respuestas cortas, fluidas, ingeniosas y que suenen 100% naturales, ideales para mensajería móvil. "
            f"REGLA DE ORO: Evita sonar artificial o formal. Prohibido ser arrogante, intenso o pesado. "
            f"Mantén siempre una vibra de alta confianza y tensión divertida. "
            f"ESTILOS DE RESPUESTA SEGÚN EL MODO SELECCIONADO ({modo}): "
            f"- Romántico: Dulce, tierno y detallista, pero moderno. Hazla sentir especial sin sonar necesitado. "
            f"- Coqueto: Pícaro, divertido y seguro. Usa cumplidos inesperados o réplicas ingeniosas que la hagan reír. "
            f"- Picante: Atrevido, magnético y directo. Genera tensión con mucha clase, elegancia y alta seguridad. "
            f"- Provocativo: Un reto juguetón. Aplica el 'tira y afloja'. Sé ese villano encantador que pone un desafío inteligente para que ella busque ganar tu atención. "
            f"Formato estricto: Entrega exclusivamente las 3 opciones en una lista numerada (1, 2, 3). No agregues introducciones, comentarios, ni textos extras antes o después."
        )
        user_prompt = f"Contexto del chat actual:\n{texto_para_analizar}\n\nGenera las 3 mejores opciones para responder bajo el modo {modo}."

    # EJECUTAMOS EL CEREBRO DE CONQUISTA PRINCIPAL (Llama 3.3 70B)
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
        resultado = res_final['choices'][0]['message']['content']
        return jsonify({"resultado": resultado})
    except Exception as e:
        return jsonify({"resultado": f"Error en el motor de conquista: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
