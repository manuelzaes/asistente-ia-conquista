from flask import Flask, render_template_string, request, jsonify
import requests
import os
# Importamos las librerías necesarias para el sistema anti-suspensión
from apscheduler.schedulers.background import BackgroundScheduler
import time

app = Flask(__name__)

# CONFIGURACIÓN: API KEY de Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# CONFIGURACIÓN DEL DESPERTADOR: Pon aquí la URL exacta de tu aplicación en Render
RENDER_APP_URL = "https://asistente-ia-conquista.onrender.com"

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
        .btn-coq:hover {
