# CRM Motos - Pipeline IA

## ¿Qué hace?
Este proyecto es un CRM (Customer Relationship Management) diseñado para la gestión y análisis de ventas de motocicletas. Proporciona una interfaz interactiva donde los asesores y administradores pueden visualizar métricas clave, gestionar leads, consultar el catálogo de motos y analizar el histórico de cierres. Está construido con una arquitectura desacoplada que separa la lógica de negocio (Backend) de la interfaz de usuario (Frontend), asegurando escalabilidad y rendimiento.

## ¿Cómo se ejecuta?

### Entorno Local
1. **Clonar el repositorio:** `git clone <url-del-repo>`
2. **Levantar Base de Datos:** `sudo docker-compose up -d`
3. **Preparar Entorno:** 
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   # CRM Motos - Pipeline IA

## ¿Qué hace?
Este proyecto es un CRM (Customer Relationship Management) diseñado para la gestión y análisis de ventas de motocicletas. Proporciona una interfaz interactiva donde los asesores y administradores pueden visualizar métricas clave, gestionar leads, consultar el catálogo de motos y analizar el histórico de cierres. Está construido con una arquitectura desacoplada que separa la lógica de negocio (Backend) de la interfaz de usuario (Frontend), asegurando escalabilidad y rendimiento.

## ¿Cómo se ejecuta?

### Entorno Local
1. **Clonar el repositorio:** `git clone <url-del-repo>`
2. **Levantar Base de Datos:** `sudo docker-compose up -d`
3. **Preparar Entorno:** 
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

4. Poblar Base de Datos: python cargar_bd.py

5. Ejecutar Servicios:

        Backend: uvicorn api:app --reload --port 8000

        Frontend: streamlit run dashboard.py --server.port 8501

**Entorno de Producción (AWS)**

La aplicación está desplegada en una instancia EC2 de AWS con Ubuntu 24.04. Los servicios se ejecutan de forma nativa e ininterrumpida mediante Systemd (api.service y dashboard.service). Las actualizaciones se despliegan automáticamente al hacer push a la rama main gracias a GitHub Actions.
Decisiones Tomadas

    Arquitectura Desacoplada: Se separó el backend (FastAPI) del frontend (Streamlit) para permitir que en el futuro la API pueda ser consumida por otras plataformas (ej. aplicación móvil).

    Gestión de Servicios con Systemd: Se descartó el uso de comandos volátiles como nohup a favor de crear servicios nativos de Linux. Esto garantiza que la aplicación se reinicie automáticamente si el servidor se apaga o falla, asegurando alta disponibilidad.

    Integración Continua (CI/CD): Se implementó un pipeline en GitHub Actions para eliminar los despliegues manuales. El pipeline se conecta vía SSH de forma segura, actualiza el código e instruye a Systemd para reiniciar los servicios sin tiempos de inactividad prolongados.

    Base de Datos Contenerizada: Se optó por ejecutar PostgreSQL dentro de Docker para estandarizar el entorno de datos y evitar conflictos de configuración entre el entorno local y producción.

**Supuestos Asumidos**

    Volumen de Tráfico: Se asume que el tráfico actual puede ser manejado eficientemente por los recursos de la capa gratuita de AWS (Instancia t2.micro, 1GB RAM, apoyada por memoria Swap).

    Modelo de Datos: Se asume que la carga inicial de datos desde archivos CSV (empresas, leads, asesores, catálogo e histórico) refleja fielmente el modelo relacional necesario para la operación del negocio.

**¿Qué haría con más tiempo?**

    Implementar HTTPS/SSL: Configurar un proxy inverso con Nginx y Let's Encrypt para asegurar las comunicaciones web y usar un dominio personalizado.

    Dockerización Completa: Empaquetar FastAPI y Streamlit en sus propios contenedores Docker para unificar todo el ecosistema usando docker-compose.

    Pruebas Automatizadas: Integrar pytest en el pipeline de GitHub Actions para bloquear despliegues si el código nuevo rompe alguna funcionalidad existente.