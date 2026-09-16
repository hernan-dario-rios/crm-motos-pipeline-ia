import os
import json
import pandas as pd
from google import genai
from google.genai import types
import time
from dotenv import load_dotenv

# ==========================================
# CONFIGURACIÓN SEGURA DE CREDENCIALES
# ==========================================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("¡Error CRÍTICO!: No se encontró GEMINI_API_KEY. Verifica que exista el archivo .env")

client = genai.Client(api_key=API_KEY)

# ==========================================
# FUNCIONES DE PROCESAMIENTO
# ==========================================

def aplanar_conversacion(mensajes):
    """Toma la lista de mensajes y la convierte en un bloque de texto."""
    texto_plano = ""
    for msg in mensajes:
        texto_plano += f"{msg['emisor'].upper()} ({msg['hora']}): {msg['texto']}\n"
    return texto_plano

def extraer_informacion_por_lote(lote_conversaciones):
    """Envía un bloque entero de conversaciones a la IA y pide un Array de JSONs."""
    
    # 1. Construimos el mega-texto con todas las conversaciones del lote
    texto_lote = ""
    for conv in lote_conversaciones:
        texto_lote += f"\n--- INICIO CONVERSACION_ID: {conv['conversacion_id']} ---\n"
        texto_lote += aplanar_conversacion(conv['mensajes'])
        texto_lote += f"--- FIN CONVERSACION_ID: {conv['conversacion_id']} ---\n"

    # 2. El Prompt ahora exige devolver una lista de objetos
    prompt = f"""
    Eres un analista de ventas experto en un concesionario de motos. Lee el siguiente lote de conversaciones de WhatsApp.
    Extrae la información y devuelve un ARREGLO JSON (lista) donde cada objeto tenga exactamente estas claves:
    
    - "conversacion_id": (string) El ID de la conversación analizada.
    - "modelo_interes": (string) El nombre de la moto mencionada, o null si no se menciona.
    - "presupuesto_mencionado": (numero) El valor en dinero mencionado para inicial o presupuesto (ej. 2000000). null si no hay.
    - "forma_pago": (string) Puede ser "contado", "financiada", o null.
    - "intencion_declarada": (string) Resumen corto. Ej: "solo mirar precios", "comprar urgente", "comparando", o null.
    - "objecion_principal": (string) Obstáculo de compra. Ej: "muy caro", "reportado", "tasa alta", o null.
    - "pidio_cita": (boolean) true si el cliente confirma que irá al local o pide cita, false en caso contrario.

    Conversaciones a analizar:
    {texto_lote}
    """
    
    max_reintentos = 3
    for intento in range(max_reintentos):
        try:
            # Usamos el modelo 3.6-flash que Google exigió en el error de ayer
            response = client.models.generate_content(
                model='gemini-3.6-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            return json.loads(response.text)
            
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                print(f"    [!] Cuota superada. Esperando 60 segundos... (Intento {intento + 1}/{max_reintentos})")
                time.sleep(60)
            else:
                print(f"    [!] Error IA inesperado: {error_msg}")
                break
                
    # Si falla, devolvemos una lista vacía para no romper el programa
    return []

def iniciar_pipeline_ia(ruta_json):
    print("Cargando conversaciones...")
    with open(ruta_json, 'r', encoding='utf-8') as archivo:
        conversaciones = json.load(archivo)
    
    total = len(conversaciones)
    print(f"Total a procesar: {total} conversaciones.")
    
    resultados_ia = []
    LOTE_SIZE = 15  # Procesaremos de a 15 conversaciones por petición
    
    # Iteramos sobre la lista saltando de a LOTE_SIZE
    for i in range(0, total, LOTE_SIZE):
        lote = conversaciones[i : i + LOTE_SIZE]
        print(f"Procesando lote {i//LOTE_SIZE + 1} (Conversaciones {i+1} a {min(i+LOTE_SIZE, total)} de {total})...")
        
        datos_extraidos_lote = extraer_informacion_por_lote(lote)
        
        # Cruzamos el resultado de la IA con el lead_id original
        for conv_ia in datos_extraidos_lote:
            # Buscamos el lead_id original en nuestro lote
            lead_id_original = next((c['lead_id'] for c in lote if c['conversacion_id'] == conv_ia.get('conversacion_id')), None)
            
            registro = {
                "conversacion_id": conv_ia.get("conversacion_id"),
                "lead_id": lead_id_original,
                "modelo_interes": conv_ia.get("modelo_interes"),
                "presupuesto_mencionado": conv_ia.get("presupuesto_mencionado"),
                "forma_pago": conv_ia.get("forma_pago"),
                "intencion_declarada": conv_ia.get("intencion_declarada"),
                "objecion_principal": conv_ia.get("objecion_principal"),
                "pidio_cita": conv_ia.get("pidio_cita")
            }
            resultados_ia.append(registro)
        
        # Guardado incremental por cada lote
        pd.DataFrame(resultados_ia).to_csv('leads_ia_extraidos_backup.csv', index=False)
        
        # Pausa obligatoria entre lotes para cuidar la cuota gratuita (10 segundos)
        time.sleep(10)
        
    df_ia = pd.DataFrame(resultados_ia)
    return df_ia

if __name__ == "__main__":
    df_resultado = iniciar_pipeline_ia('conversaciones.json')
    df_resultado.to_csv('leads_ia_extraidos.csv', index=False, encoding='utf-8')
    print(f"\n¡Análisis por lotes completado al 100%! {len(df_resultado)} leads extraídos.")
    print("Revisa el archivo 'leads_ia_extraidos.csv'.")