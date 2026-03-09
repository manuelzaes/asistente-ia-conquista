import tkinter as tk
from tkinter import messagebox
import requests
import json

# 1. CONFIGURACIÓN: Pega tu API KEY de Groq aquí
GROQ_API_KEY = "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"

def limpiar_campos():
    text_chat.delete(1.0, tk.END)
    text_resultado.config(state=tk.NORMAL)
    text_resultado.delete(1.0, tk.END)
    text_resultado.config(state=tk.DISABLED)

def generar_respuesta(modo):
    conversacion = text_chat.get(1.0, tk.END).strip()
    if not conversacion or len(conversacion) < 10:
        messagebox.showwarning("Atención", "Pega el chat para analizarlo.")
        return

    estilos = {
        "Romántico": "Sé un poeta moderno: dulce y sincero.",
        "Coqueto": "Sé ingenioso, divertido y seguro.",
        "Picante": "Sé audaz y seductor. Genera tensión con clase."
    }

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": "llama-3.3-70b-versatile", 
        "messages": [
            {"role": "system", "content": f"Experto en carisma. Da 3 opciones en modo {modo}. {estilos[modo]}"},
            {"role": "user", "content": f"Chat:\n{conversacion}"}
        ],
        "temperature": 0.8
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        data = response.json()
        if "choices" in data:
            resultado = data["choices"][0]["message"]["content"]
            text_resultado.config(state=tk.NORMAL)
            text_resultado.delete(1.0, tk.END)
            text_resultado.insert(tk.END, f"✨ SUGERENCIAS {modo.upper()}:\n\n{resultado}")
            text_resultado.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("Error", f"Fallo de conexión: {e}")

# --- INTERFAZ ---
root = tk.Tk()
root.title("Asistente de Seducción v2.2 - UTP")
root.geometry("550x700")
root.configure(bg="#121212")

tk.Label(root, text="💬 PEGA EL CHAT AQUÍ:", fg="#bb86fc", bg="#121212", font=("Arial", 11, "bold")).pack(pady=10)
text_chat = tk.Text(root, height=10, width=60, bg="#1e1e1e", fg="white", font=("Consolas", 10))
text_chat.pack(pady=5)

frame_btns = tk.Frame(root, bg="#121212")
frame_btns.pack(pady=15)

tk.Button(frame_btns, text="💖 Romántico", command=lambda: generar_respuesta("Romántico"), bg="#ff4dff", width=12, font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
tk.Button(frame_btns, text="😏 Coqueto", command=lambda: generar_respuesta("Coqueto"), bg="#ff9900", width=12, font=("Arial", 9, "bold")).grid(row=0, column=1, padx=5)
tk.Button(frame_btns, text="🔥 Picante", command=lambda: generar_respuesta("Picante"), bg="#ff0000", fg="white", width=12, font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5)

tk.Button(root, text="🧹 Limpiar Todo", command=limpiar_campos, bg="#424242", fg="white", width=20, font=("Arial", 9)).pack(pady=5)

tk.Label(root, text="🤖 RESPUESTAS SUGERIDAS:", fg="#03dac6", bg="#121212", font=("Arial", 10, "bold")).pack(pady=5)
text_resultado = tk.Text(root, height=12, width=60, wrap=tk.WORD, state=tk.DISABLED, bg="#1e1e1e", fg="#00ff00", font=("Arial", 10))
text_resultado.pack(pady=10)

root.mainloop()