from flask import Flask, render_template_string, request, jsonify
import requests
import os

app = Flask(__name__)

# 1. CONFIGURACIÓN: Pega tu API KEY de Groq aquí
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spark IA </title>
    <style>
        body { background: #121212; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 20px; }
        .container { max-width: 500px; margin: auto; }
        textarea { width: 100%; height: 120px; background: #1e1e1e; color: #00ff00; border: 2px solid #bb86fc; border-radius: 10px; padding: 10px; font-size: 16px; box-sizing: border-box; }
        button { width: 100%; padding: 18px; margin: 10px 0; border: none; border-radius: 12px; font-weight: bold; font-size: 16px; cursor: pointer; transition: 0.3s; }
        .btn-rom { background: #8A2BE2; color: white; }
        .btn-coq { background: #ff9900; color: white; }
        .btn-pic { background: #ff0000; color: white; }
        .btn-clear { background: #424242; color: #ccc; margin-top: 5px; padding: 10px; }
        #res { background: #1e1e1e; padding: 15px; border-radius: 10px; text-align: left; white-space: pre-wrap; margin-top: 20px; border-left: 5px solid #03dac6; min-height: 50px; }
        h2 { color: #bb86fc; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Spark IA</h2>
        <p>Pega el chat:</p>
        <textarea id="chat" placeholder="Escribe o pega el chat aquí..."></textarea>
        
        <button class="btn-rom" onclick="enviar('Romántico')">💖 MODO ROMÁNTICO</button>
        <button class="btn-coq" onclick="enviar('Coqueto')">😏 MODO COQUETO</button>
        <button class="btn-pic" onclick="enviar('Picante')">🔥 MODO PICANTE</button>
        <button class="btn-clear" onclick="limpiar()">🧹 Limpiar Todo</button>

        <div id="res">✨ Las sugerencias de Llama 3.3 aparecerán aquí...</div>
    </div>

    <script>
        function limpiar() {
            document.getElementById('chat').value = "";
            document.getElementById('res').innerText = "✨ Las sugerencias aparecerán aquí...";
        }

        function enviar(modo) {
            const chat = document.getElementById('chat').value;
            const resDiv = document.getElementById('res');
            if(!chat) { alert("Por favor, pega un chat primero."); return; }
            
            resDiv.innerText = "⏳ Pensando como un experto...";
            
            fetch('/generar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({chat: chat, modo: modo})
            })
            .then(response => response.json())
            .then(data => {
                resDiv.innerText = data.resultado;
            })
            .catch(error => {
                resDiv.innerText = "❌ Error: Verifica la conexión con la laptop.";
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
    chat = data.get('chat')
    modo = data.get('modo')
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system", 
                    "content": f"Eres un experto en carisma y seducción. El usuario quiere ligar. Tu misión: dar 3 opciones CORTAS (estilo WhatsApp), directas y con mucha seguridad. PROHIBIDO: frases cursis, poemas, saludos familiares o clichés. Usa un lenguaje de alguien joven, seguro de sí mismo y atrevido. El objetivo es generar tensión romántica o concretar una cita. Solo entrega las 3 opciones numeradas."
                },
                {"role": "user", "content": f"Contexto: {modo}. Ella me puso: '{chat}'. Dame 3 respuestas para conquistarla."}
            ],
            "temperature": 1.0
        }
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        res_json = r.json()
        resultado = res_json['choices'][0]['message']['content']
        return jsonify({"resultado": resultado})
    except Exception as e:
        return jsonify({"resultado": f"Error en la API: {str(e)}"})

# --- ESTA ES LA LÍNEA CLAVE ---
if __name__ == '__main__':
    # host='0.0.0.0' permite conexiones externas (tu celular)
    # port=5000 es el puerto que abriste en el Firewall

    app.run(host='0.0.0.0', port=5000, debug=True)







