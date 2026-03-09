import google.generativeai as genai
import os

# 1. CONFIGURACIÓN: Pega aquí tu API KEY de Google AI Studio
API_KEY = "AIzaSyB1imze96CEYw3aAt7dhaoqOFEp4Yjf8nk"
genai.configure(api_key=API_KEY)

def obtener_consejos_ia(nombre, intereses, personalidad):
    try:
        # Configurar el modelo de Google
        model = genai.GenerativeModel('gemini-pro')
        
        # El "Prompt" que define la inteligencia de tu app
        prompt = f"""
        Actúa como un experto en carisma y citas. 
        Analiza a esta persona para ayudarme a romper el hielo:
        - Nombre: {nombre}
        - Intereses: {intereses}
        - Personalidad: {personalidad}
        
        Genera 3 opciones de mensajes rompehielos que NO sean clichés:
        1. Opción Divertida (un chiste o comentario ingenioso).
        2. Opción Basada en Intereses (algo que demuestre que pusiste atención).
        3. Opción Directa (segura y respetuosa).
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"❌ Error de conexión: {e}"

# --- MODO INTERACTIVO DIRECTO ---
if __name__ == "__main__":
    print("\n" + "="*40)
    print("💘 IA DE CONQUISTA - MODO DIRECTO")
    print("="*40)
    
    # Te pide los datos en el momento
    nom = input("👤 ¿Cómo se llama?: ")
    int_u = input("🎨 ¿Qué le gusta? (ej. anime, gym, cocina): ")
    pers_u = input("🧠 ¿Cómo es su personalidad? (ej. seria, alegre): ")
    
    print("\n" + "."*10 + " Consultando al cerebro de la IA " + "."*10)
    
    resultado = obtener_consejos_ia(nom, int_u, pers_u)
    
    print("\n" + "*"*40)
    print("🤖 LA IA TE RECOMIENDA:")
    print("*"*40)
    print(resultado)
    print("\n" + "="*40)
    
    input("\nPresiona ENTER para salir...")