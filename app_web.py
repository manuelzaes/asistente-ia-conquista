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
                    preview.src = e.target.result
