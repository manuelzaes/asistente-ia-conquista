import os
from flask import Flask, render_template_string

app = Flask(__name__)

# Intenta obtener la API Key de las variables de Render
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spark IA - Tu Asistente de Conquista</title>
    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
    <style>
        body {{ background-color: #121212; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 20px; margin: 0; }}
        .container {{ max-width: 500px; margin: auto; background: #1e1e1e; padding: 25px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); margin-top: 20px; }}
        h2 {{ color: #bb86fc; margin-bottom: 5px; }}
        .subtitle {{ color: #888; font-size: 14px; margin-bottom: 20px; }}
        .upload-area {{ border: 2px dashed #888; border-radius: 15px; padding: 20px; cursor: pointer; background: #252525; margin-bottom: 15px; }}
        #preview-img {{ max-width: 100%; max-height: 250px; border-radius: 10px; margin-top: 10px; display: none; }}
        textarea, input[type="password"] {{ width: 90%; background: #2a2a2a; color: white; border: 1px solid #444; border-radius: 12px; padding: 12px; resize: none; margin-bottom: 15px; font-size: 14px; }}
        textarea {{ height: 60px; }}
        
        .grid-botones {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 15px; }}
        .btn-base {{ border: none; padding: 12px; border-radius: 12px; font-weight: bold; cursor: pointer; color: white; text-transform: uppercase; font-size: 12px; }}
        .btn-ini {{ background: linear-gradient(135deg, #00c6ff, #0072ff); grid-column: span 2; }}
        .btn-rom {{ background: linear-gradient(135deg, #ff69b4, #ff1493); }}
        .btn-coq {{ background: linear-gradient(135deg, #ff9100, #ed8002); }}
        .btn-pic {{ background: linear-gradient(135deg, #ff3d00, #dd2c00); }}
        .btn-pro {{ background: linear-gradient(135deg, #a855f7, #7e22ce); }}
        .btn-salv {{ background: linear-gradient(135deg, #10b981, #059669); grid-column: span 2; }}
        .btn-limp {{ background: #444; color: #ccc; margin-top: 10px; width: 100%; padding: 10px; border-radius: 10px; border: none; cursor: pointer; font-size: 12px; }}
        
        #res {{ background: #2a2a2a; padding: 18px; border-radius: 12px; text-align: left; white-space: pre-wrap; margin-top: 15px; border-left: 5px solid #00D4FF; min-height: 50px; font-size: 14px; line-height: 1.5; }}
        .loading {{ color: #888; font-style: italic; }}
        #status-ocr {{ font-size: 12px; color: #00c6ff; margin-top: 5px; display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Spark IA</h2>
        <div class="subtitle">Asistente de Conquista v5.0</div>
        
        <input type="password" id="api-key-input" placeholder="Pega tu Groq API Key aquí (gsk_...)" value="{GROQ_KEY}">
        
        <div class="upload-area" onclick="document.getElementById('file-input').click();">
            <span id="upload-text">📸 Subir captura del chat</span>
            <input type="file" id="file-input" accept="image/*" onchange="cargarImagen(event)" style="display:none;">
            <img id="preview-img">
            <div id="status-ocr">🔍 Leyendo imagen...</div>
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

        async function cargarImagen(event) {{
            const file = event.target.files[0];
            if (file) {{
                const reader = new FileReader();
                reader.onload = async function(e) {{
                    imagenBase64 = e.target.result;
                    document.getElementById('preview-img').src = imagenBase64;
                    document.getElementById('preview-img').style.display = 'block';
                    document.getElementById('upload-text').style.display = 'none';
                    
                    const status = document.getElementById('status-ocr');
                    status.style.display = 'block';
                    status.innerText = "🔍 Leyendo texto de la captura...";
                    
                    try {{
                        const result = await Tesseract.recognize(imagenBase64, 'spa');
                        textoExtraidoOCR = result.data.text.trim();
                        status.innerText = "✅ Captura procesada con éxito";
                    }} catch (err) {{
                        status.innerText = "⚠️ Ingrese texto manualmente abajo.";
                    }}
                }};
                reader.readAsDataURL(file);
            }}
        }}

        function limpiarTodo() {{
            imagenBase64 = null;
            textoExtraidoOCR = "";
            document.getElementById('file-input').value = "";
            document.getElementById('preview-img').style.display = 'none';
            document.getElementById('upload-text').style.display = 'block';
            document.getElementById('status-ocr').style.display = 'none';
            document.getElementById('texto-adicional').value = "";
            document.getElementById('res').innerText = "Sube una captura o escribe contexto y elige un estilo.";
        }}

        async function generarRespuesta(modo) {{
            const resDiv = document.getElementById('res');
            const apiKey = document.getElementById('api-key-input').value.trim();
            const textoManual = document.getElementById('texto-adicional').value;
            
            if (!apiKey) {{
                resDiv.innerText = "⚠️ Ingresa tu API Key de Groq (gsk_...) en la casilla superior.";
                return;
            }}
            
            const contextoFinal = (textoExtraidoOCR + "\\n" + textoManual).trim();
            
            if (!contextoFinal && modo !== 'Iniciar Conversación') {{
                resDiv.innerText = "⚠️ Suba una captura o escriba el mensaje en el cuadro de texto.";
                return;
            }}
            
            resDiv.innerHTML = '<span class="loading">🤔 Generando opciones de respuesta...</span>';
            
            const prompt = `Escribe EXCLUSIVAMENTE en español latino. Eres un experto en seducción y citas.

Genera ÚNICAMENTE 3 opciones de respuesta cortas y directas en tono **${{modo.toUpperCase()}}**.

Formato estricto:
1. "Opción 1"
2. "Opción 2"
3. "Opción 3"

REGLAS:
- Cero intros, cero saludos, cero explicaciones.
- Empieza directamente con "1.".
- Contexto brindado: "${{contextoFinal}}"`;

            const modelos = ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"];
            let respuestaExitosa = false;

            for (let model of modelos) {{
                try {{
                    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {{
                        method: "POST",
                        headers: {{
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${{apiKey}}`
                        }},
                        body: JSON.stringify({{
                            model: model,
                            messages: [{{ role: "user", content: prompt }}],
                            temperature: 0.7,
                            max_tokens: 250
                        }})
                    }});

                    const data = await response.json();

                    if (response.ok && data.choices && data.choices[0]) {{
                        resDiv.innerText = data.choices[0].message.content.trim();
                        respuestaExitosa = true;
                        break;
                    }}
                }} catch (err) {{
                    continue;
                }}
            }}

            if (!respuestaExitosa) {{
                resDiv.innerText = "❌ Error: API Key no válida o sin cuota disponible. Verifica tu clave en console.groq.com.";
            }}
        }}
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
