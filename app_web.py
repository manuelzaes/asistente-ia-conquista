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
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚡</text></svg>">
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
        .btn-
