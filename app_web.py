import os
import re
import threading
import time
import requests
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for

app = Flask(__name__)
# Clave secreta necesaria para manejar sesiones en Flask de forma segura
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "clave_secreta_por_defecto_super_segura")

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

# ==========================================
# PLANTILLA DE LOGIN (ACCESO RESTRINGIDO)
# ==========================================
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acceso Restringido - Spark IA</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@800;900&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <style>
        body { 
            background: radial-gradient(circle at top, #121629 0%, #080912 100%);
            color: white; 
            font-family: 'Segoe UI', sans-serif; 
            text-align: center; 
            padding: 20px; 
            margin: 0; 
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            width: 100%;
            max-width: 400px; 
            background: #141724; 
            padding: 30px 24px; 
            border-radius: 20px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.6), 0 0 20px rgba(187, 134, 252, 0.08); 
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .header-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 26px;
            font-weight: 900;
            letter-spacing: 2px;
            color: #bb86fc;
            margin: 0 0 6px 0;
            text-transform: uppercase;
        }
        .subtitle { 
            font-family: 'Space Grotesk', sans-serif;
            color: #717e9e; 
            font-size: 11px; 
            margin-bottom: 24px; 
            letter-spacing: 1.5px;
            text-transform: uppercase;
            font-weight: 700;
        }
        input {
            width: 100%;
            box-sizing: border-box;
            background: #1c2033;
            color: white;
            border: 1px solid #2d354d;
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 15px;
            font-size: 14px;
            outline: none;
        }
        input:focus {
            border-color: #bb86fc;
        }
        .btn-login {
            background: linear-gradient(135deg, #a855f7, #7e22ce);
            border: none;
            width: 100%;
            padding: 14px;
            border-radius: 12px;
            color: white;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 13px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
            transition: filter 0.2s;
        }
        .btn-login:hover {
            filter: brightness(1.15);
        }
        .error-msg {
            color: #ff5252;
            font-size: 12px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2 class="header-title">⚡ SPARK IA</h2>
        <div class="subtitle">Acceso Exclusivo</div>
        
        {% if error %}
            <div class="error-msg">{{ error }}</div>
        {% endif %}

        <form method="POST" action="/login">
            <input type="text" name="usuario" placeholder="Usuario" required autocomplete="off">
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit" class="btn-login">Ingresar</button>
        </form>
    </div>
</body>
</html>
"""

# ==========================================
# PLANTILLA PRINCIPAL DE LA APP
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spark IA - Tu Asistente de Conquista</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚡</text></svg>">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@800;900&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    
    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
    <style>
        body { 
            background: radial-gradient(circle at top, #121629 0%, #080912 100%);
            color: white; 
            font-family: 'Segoe UI', sans-serif; 
            text-align: center; 
            padding: 20px; 
            margin: 0; 
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .container { 
            width: 100%;
            max-width: 480px; 
            background: #141724; 
            padding: 28px 24px; 
            border-radius: 20px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.6), 0 0 20px rgba(187, 134, 252, 0.08); 
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin: auto;
            position: relative;
        }

        .logout-btn {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.05);
            color: #9ca3af;
            border: none;
            padding: 6px 10px;
            border-radius: 8px;
            font-size: 11px;
            cursor: pointer;
            text-decoration: none;
            font-weight: 600;
        }
        .logout-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }

        .header-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 28px;
            font-weight: 900;
            letter-spacing: 2px;
            color: #bb86fc;
            margin: 0 0 4px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            text-transform: uppercase;
            text-shadow: 0 0 10px rgba(187, 134, 252, 0.3);
        }

        .header-title span.rayo {
            color: #bb86fc;
            font-size: 26px;
        }

        .subtitle { 
            font-family: 'Space Grotesk', sans-serif;
            color: #717e9e; 
            font-size: 11px; 
            margin-bottom: 22px; 
            letter-spacing: 1.5px;
            text-transform: uppercase;
            font-weight: 700;
        }

        .upload-area { 
            border: 1.5px dashed #374151; 
            border-radius: 12px; 
            padding: 18px; 
            cursor: pointer; 
            background: #1c2033; 
            margin-bottom: 15px; 
            color: #d1d5db;
            font-size: 13px;
            font-weight: 600;
        }

        #preview-img { 
            max-width: 100%; 
            max-height: 200px; 
            border-radius: 10px; 
            margin-top: 10px; 
            display: none; 
        }

        textarea { 
            width: 100%; 
            box-sizing: border-box;
            height: 70px; 
            background: #1c2033; 
            color: white; 
            border: 1px solid #2d354d; 
            border-radius: 12px; 
            padding: 12px; 
            resize: none; 
            margin-bottom: 15px; 
            font-size: 13px;
            outline: none;
        }

        .grid-botones { 
            display: grid; 
            grid-template-columns: repeat(2, 1fr); 
            gap: 10px; 
            margin-bottom: 15px; 
        }

        .btn-base { 
            border: none; 
            padding: 12px; 
            border-radius: 12px; 
            font-weight: bold; 
            cursor: pointer; 
            color: white; 
            text-transform: uppercase; 
            font-size: 12px;
        }

        .btn-ini { background: linear-gradient(135deg, #00c6ff, #0072ff); grid-column: span 2; }
        .btn-rom { background: linear-gradient(135deg, #ff69b4, #ff1493); }
        .btn-coq { background: linear-gradient(135deg, #ff9100, #ed8002); }
        .btn-pic { background: linear-gradient(135deg, #ff3d00, #dd2c00); }
        .btn-pro { background: linear-gradient(135deg, #a855f7, #7e22ce); }
        .btn-salv { background: linear-gradient(135deg, #10b981, #059669); grid-column: span 2; }

        .btn-limp { 
            background: #23283b; 
            color: #9ca3af; 
            margin-top: 5px; 
            width: 100%; 
            padding: 10px; 
            border-radius: 10px; 
            border: none; 
            cursor: pointer; 
            font-size: 12px; 
            font-weight: 600;
        }

        #res { 
            background: #1c2033; 
            padding: 18px; 
            border-radius: 12px; 
            text-align: left; 
            white-space: pre-wrap; 
            margin-top: 15px; 
            border-left: 4px solid #00D4FF; 
            min-height: 50px; 
            font-size: 14px; 
            line-height: 1.5; 
            color: #e5e7eb;
        }

        .loading { color: #888; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/logout" class="logout-btn">Salir ✕</a>
        <h2 class="header-title"><span class="rayo">⚡</span> SPARK IA</h2>
        <div class="subtitle">Asistente de Conquista v6.0</div>
        
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

# ==========================================
# RUTAS DE CONTROL DE ACCESO Y APP
# ==========================================

@app.route('/')
def home():
    # Si el usuario no ha iniciado sesión, lo mandamos al login
    if not session.get('autenticado'):
        return render_template_string(LOGIN_TEMPLATE)
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    usuario_ingresado = request.form.get('usuario', '').strip()
    password_ingresado = request.form.get('password', '').strip()

    # Obtenemos las credenciales configuradas en las variables de entorno de Render
    # Si no existen en Render, ponemos valores por defecto provisionales
    USER_CORRECTO = os.environ.get("ACCESS_USER", "admin")
    PASS_CORRECTO = os.environ.get("ACCESS_PASS", "spark2026")

    if usuario_ingresado == USER_CORRECTO and password_ingresado == PASS_CORRECTO:
        session['autenticado'] = True
        return redirect(url_for('home'))
    else:
        return render_template_string(LOGIN_TEMPLATE, error="Usuario o contraseña incorrectos.")

@app.route('/logout')
def logout():
    session.pop('autenticado', None)
    return redirect(url_for('home'))

@app.route('/procesar', methods=['POST'])
def procesar():
    if not session.get('autenticado'):
        return jsonify({'error': 'Acceso no autorizado.'}), 401

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
        f"HISTORIAL O MENSAJE DEL CHAT SUBIDO:\n\"{contexto_evaluado}\"\n\n"
        f"ROL Y PERSPECTIVA OBLIGATORIA:\n"
        f"1. Tú eres el ASISTENTE del usuario que opera esta app.\n"
        f"2. Debes escribir respuestas PARA QUE EL USUARIO SE LAS ENVÍE A LA OTRA PERSONA.\n"
        f"3. NUNCA respondas como si fueras la otra persona. Si en la imagen se lee el nombre del usuario, NUNCA uses ese nombre para responder.\n"
        f"4. Mantén cada opción fluida y directa (máximo 2 a 3 líneas por opción).\n\n"
        f"ESTILO REQUERIDO: {modo.upper()} ({estilo_instruccion})\n\n"
        f"REGLAS DE FORMATO:\n"
        f"- MUESTRA OBLIGATORIAMENTE LAS 3 OPCIONES COMPLETAS (numeradas 1, 2 y 3).\n"
        f"- NO saludes (no digas 'Hola', 'Buenas', etc.) salvo en 'Iniciar Conversación'.\n"
        f"- Escribe en español latino natural, sin introducciones ni frases explicativas."
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
                {
                    "role": "system", 
                    "content": (
                        "Eres un experto en seducción y dinámicas de conversación. "
                        "Tu tarea es generar sugerencias de mensajes para que tu usuario se los envíe a su interlocutor. "
                        "Garantiza enviar siempre exactamente 3 opciones de respuesta numéricas y completas."
                    )
                },
                {"role": "user", "content": prompt_texto}
            ],
            "temperature": 1.1,
            "max_tokens": 600
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
