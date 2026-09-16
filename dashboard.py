import streamlit as st
import requests
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="CRM Motos - Mis Leads", page_icon="🏍️", layout="wide")

st.title("🏍️ Tablero de Gestión Comercial")
st.subheader("Lista priorizada de gestión diaria")

st.sidebar.title("🔐 Acceso Asesor")
st.sidebar.markdown("En producción, esto se toma del Login del usuario.")

# NUEVO: Consultamos las empresas reales directamente a nuestra API
try:
    res_empresas = requests.get("http://127.0.0.1:8000/api/empresas")
    if res_empresas.status_code == 200:
        empresas_disponibles = res_empresas.json()
    else:
        empresas_disponibles = ["Error cargando BD"]
except:
    empresas_disponibles = ["API desconectada"]

empresa_activa = st.sidebar.selectbox("Seleccione su Comercializadora:", empresas_disponibles)

st.sidebar.divider()
st.sidebar.info(f"**Modo Seguro:** Solo estás viendo los clientes asignados a la empresa **{empresa_activa}**.")

# Consumo de la API para traer leads
if st.button("Consultar Mis Leads de Hoy"):
    with st.spinner("Consultando base de datos segura..."):
        try:
            url_api = f"http://127.0.0.1:8000/api/leads/{empresa_activa}"
            respuesta = requests.get(url_api)
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                
                if len(datos) > 0:
                    df = pd.DataFrame(datos)
                    leads_calientes = len(df[df['temperatura'] == 'Caliente 🔥'])
                    
                    st.markdown("### 📊 Resumen de tu bandeja")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Leads Asignados", len(df))
                    col2.metric("Leads Calientes (Prioridad)", leads_calientes)
                    col3.metric("Objeciones Detectadas", df['objecion_principal'].notna().sum())
                    
                    st.markdown("### 📋 Tus clientes para contactar ya")
                    df_vista = df[['score_prioridad', 'temperatura', 'nombre_cliente', 'telefono_limpio', 'modelo_interes', 'forma_pago', 'objecion_principal']]
                    df_vista.columns = ['Score', 'Temp.', 'Cliente', 'Teléfono', 'Moto Interés', 'Pago', 'Alerta / Objeción']
                    
                    st.dataframe(df_vista, use_container_width=True, hide_index=True)
                else:
                    st.warning("No tienes leads asignados para el día de hoy.")
            else:
                st.error("Error del servidor al consultar los leads.")
                
        except Exception as e:
            st.error(f"Error de conexión. Asegúrate de que la API (uvicorn) esté corriendo.")