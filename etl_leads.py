import pandas as pd
import re
import unicodedata

# ==========================================
# 1. FUNCIONES DE LIMPIEZA
# ==========================================

def limpiar_telefono(telefono):
    """Extrae solo los 10 dígitos del teléfono de Colombia."""
    if pd.isna(telefono):
        return None
    
    tel_str = str(telefono)
    solo_numeros = re.sub(r'\D', '', tel_str)
    
    if len(solo_numeros) == 12 and solo_numeros.startswith('57'):
        solo_numeros = solo_numeros[2:]
        
    if len(solo_numeros) == 10:
        return solo_numeros
    return None

def normalizar_texto(texto):
    """Convierte a mayúsculas, quita espacios extra y elimina tildes."""
    if pd.isna(texto):
        return None
    
    texto = str(texto).strip().upper()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                  if unicodedata.category(c) != 'Mn')
    
    if 'BOGOTA' in texto: return 'BOGOTA'
    if 'MEDELLIN' in texto: return 'MEDELLIN'
        
    return texto

# ==========================================
# 2. PROCESAMIENTO DEL DATAFRAME
# ==========================================

def procesar_leads(ruta_archivo):
    print("Iniciando carga de leads...")
    df = pd.read_csv(ruta_archivo, encoding='utf-8')
    print(f"Total leads crudos cargados: {len(df)}")
    
    # 1. Limpiar Teléfonos
    df['telefono_limpio'] = df['telefono'].apply(limpiar_telefono)
    
    # 2. Normalizar Fechas (usamos 'fecha_registro')
    df['fecha_limpia'] = pd.to_datetime(df['fecha_registro'], errors='coerce', dayfirst=True)
    
    # 3. Normalizar Ciudades
    df['ciudad_limpia'] = df['ciudad'].apply(normalizar_texto)
    
    # 4. Normalizar Emails (minúsculas, sin espacios)
    df['email_limpio'] = df['email'].astype(str).str.lower().str.strip()
    # Volver nulos los que eran nulos originalmente
    df.loc[df['email'].isna(), 'email_limpio'] = None 
    
    # 5. RESOLUCIÓN DE DUPLICADOS MULTICANAL
    # Ordenamos por fecha descendente para conservar siempre la interacción más reciente
    df = df.sort_values(by='fecha_limpia', ascending=False)
    
    # Eliminamos duplicados basados en el teléfono_limpio
    # Solo tomamos en cuenta los que sí tienen un teléfono válido
    df_con_telefono = df.dropna(subset=['telefono_limpio']).copy()
    df_deduplicado = df_con_telefono.drop_duplicates(subset=['telefono_limpio'], keep='first').copy()
    
    # Si hay leads sin teléfono (quizás solo dejaron email), los guardamos también para no perderlos
    df_sin_telefono = df[df['telefono_limpio'].isna()].copy()
    
    # Unimos todo nuevamente
    df_final = pd.concat([df_deduplicado, df_sin_telefono], ignore_index=True)
    
    print(f"Total leads después de limpiar y deduplicar: {len(df_final)}")
    
    return df_final

# ==========================================
# 3. EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    df_limpio = procesar_leads('leads.csv')
    df_limpio.to_csv('leads_limpios.csv', index=False, encoding='utf-8')
    print("\n¡Limpieza terminada con éxito! Archivo guardado como 'leads_limpios.csv'.")