import pandas as pd
import numpy as np

# ==========================================
# REGLAS DE SCORING Y NEGOCIO
# ==========================================

def calcular_score(row):
    score = 10  # Puntaje base para cualquier lead que entra
    
    # 1. Indicador más fuerte: Pide Cita
    if pd.notna(row.get('pidio_cita')) and row.get('pidio_cita') == True:
        score += 40
        
    # 2. Tiene presupuesto en mente
    if pd.notna(row.get('presupuesto_mencionado')):
        score += 20
        
    # 3. Facilidad de Cierre (Forma de pago)
    forma_pago = str(row.get('forma_pago')).lower()
    if 'contado' in forma_pago:
        score += 20
    elif 'financiada' in forma_pago or 'credito' in forma_pago:
        score += 10
        
    # 4. Fricción (Objeciones detectadas)
    objecion = str(row.get('objecion_principal')).lower()
    if objecion != 'nan' and objecion != 'none' and objecion.strip() != '':
        score -= 15
        
    # 5. Baja intención
    intencion = str(row.get('intencion_declarada')).lower()
    baja_intencion = ['curiosidad', 'comparando', 'mirando', 'solo']
    if any(palabra in intencion for palabra in baja_intencion):
        score -= 10
        
    # Asegurar que el score no se salga de los límites 0 - 100
    return max(0, min(100, score))

def asignar_temperatura(score):
    if score >= 60:
        return 'Caliente 🔥'
    elif score >= 30:
        return 'Tibio 🌤️'
    else:
        return 'Frío ❄️'

# ==========================================
# EJECUCIÓN DEL CRUCE DE DATOS
# ==========================================

def ejecutar_scoring():
    print("Iniciando Consolidación y Scoring...")
    
    try:
        # Cargar los datos limpios y los enriquecidos por IA
        df_leads = pd.read_csv('leads_limpios.csv')
        df_ia = pd.read_csv('leads_ia_extraidos.csv')
    except FileNotFoundError as e:
        print(f"Error: Faltan archivos base. Asegúrate de tener los dos CSVs listos.\nDetalle: {e}")
        return
        
    # Cruce de datos (Left Join en 'lead_id')
    # Conservamos todos los leads, incluso los que llegaron por Meta o Web y no tienen chat de IA
    df_consolidado = pd.merge(df_leads, df_ia, on='lead_id', how='left')
    
    # Aplicar la lógica matemática fila por fila
    print("Calculando Temperatura de los leads...")
    df_consolidado['score_prioridad'] = df_consolidado.apply(calcular_score, axis=1)
    df_consolidado['temperatura'] = df_consolidado['score_prioridad'].apply(asignar_temperatura)
    
    # Ordenamiento final para los asesores: 
    # Primero por Empresa, luego por Asesor, y finalmente por Prioridad (los más altos arriba)
    df_consolidado = df_consolidado.sort_values(
        by=['empresa_id', 'punto_venta_id', 'score_prioridad'], 
        ascending=[True, True, False]
    )
    
    # Guardar la base maestra final
    df_consolidado.to_csv('leads_maestros_score.csv', index=False, encoding='utf-8')
    print(f"\n¡Éxito! Se consolidaron {len(df_consolidado)} leads.")
    print("Archivo generado: 'leads_maestros_score.csv'")

if __name__ == "__main__":
    ejecutar_scoring()