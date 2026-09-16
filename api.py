from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

# 1. Configuración de Base de Datos
load_dotenv()
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "admin")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "motos_crm")

DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URI)

app = FastAPI(title="API CRM Motos", description="Motor de priorización de leads con IA")

@app.get("/")
def home():
    return {"mensaje": "La API está funcionando correctamente 🚀"}

# NUEVO: Endpoint para obtener las empresas reales
@app.get("/api/empresas")
def obtener_empresas():
    try:
        df = pd.read_sql("SELECT DISTINCT id FROM empresas ORDER BY id", engine)
        return df['id'].astype(str).tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en BD: {str(e)}")

# Endpoint de leads actualizado con limpieza total de NaNs
@app.get("/api/leads/{empresa_id}")
def obtener_leads(empresa_id: str):
    try:
        query = f"""
            SELECT lead_id, nombre_cliente, telefono_limpio, ciudad_limpia, 
                   modelo_interes, presupuesto_mencionado, forma_pago, 
                   objecion_principal, score_prioridad, temperatura
            FROM leads 
            WHERE CAST(empresa_id AS TEXT) = '{empresa_id}' 
            ORDER BY score_prioridad DESC
        """
        df = pd.read_sql(query, engine)
        
        # LA SOLUCIÓN: Llenamos los NaNs con un string vacío o los reemplazamos por None
        df = df.fillna(value="") # Convierte cualquier NaN, NaT o nulo en un texto vacío
        
        return df.to_dict(orient="records")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en BD: {str(e)}")