import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# 1. Configuración de conexión
load_dotenv()
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "admin")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "motos_crm")

DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def cargar_a_base_de_datos():
    print("Conectando a PostgreSQL...")
    try:
        engine = create_engine(DATABASE_URI)
        conexion = engine.connect()
        print("¡Conexión exitosa a la base de datos!\n")
    except Exception as e:
        print(f"Error de conexión: {e}")
        return

    # --- 1. CARGAR EMPRESAS Y LEADS ---
    try:
        df_leads = pd.read_csv('leads_maestros_score.csv')
        # Crear tabla de empresas base
        df_empresas = pd.DataFrame({'id': df_leads['empresa_id'].unique()})
        df_empresas['nombre'] = 'Comercializadora ' + df_empresas['id'].astype(str)
        
        print("Cargando tabla 'empresas'...")
        df_empresas.to_sql('empresas', engine, if_exists='replace', index=False)
        
        print("Cargando tabla 'leads'...")
        df_leads.to_sql('leads', engine, if_exists='replace', index=False)
    except Exception as e:
        print(f"Error cargando leads: {e}")

    # --- 2. CARGAR ASESORES ---
    try:
        df_asesores = pd.read_csv('asesores.csv')
        print("Cargando tabla 'asesores'...")
        df_asesores.to_sql('asesores', engine, if_exists='replace', index=False)
    except FileNotFoundError:
        print("No se encontró asesores.csv")

    # --- 3. CARGAR CATÁLOGO DE PRODUCTOS ---
    try:
        df_catalogo = pd.read_csv('catalogo_motos.csv')
        print("Cargando tabla 'catalogo_motos'...")
        df_catalogo.to_sql('catalogo_motos', engine, if_exists='replace', index=False)
    except FileNotFoundError:
        print("No se encontró catalogo_motos.csv")

    # --- 4. CARGAR HISTÓRICO DE CIERRES ---
    try:
        df_historico = pd.read_csv('historico_cierres.csv')
        print("Cargando tabla 'historico_cierres'...")
        df_historico.to_sql('historico_cierres', engine, if_exists='replace', index=False)
    except FileNotFoundError:
        print("No se encontró historico_cierres.csv")

    conexion.close()
    print("\n¡Éxito! Todo el modelo de datos relacional (5 tablas) está persistido en PostgreSQL.")

if __name__ == "__main__":
    cargar_a_base_de_datos()