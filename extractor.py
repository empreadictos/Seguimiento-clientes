import os
import requests
from datetime import datetime

# 1. Traemos la llave maestra que guardamos en los Secrets de GitHub
META_TOKEN = os.environ.get('META_TOKEN')

# 2. Los IDs exactos de los clientes de tu agencia
CLIENTES = {
    "Naty Torrente": "1520359784483889",
    "Espacio Macala": "957947710741211",
    "Empreadictos": "653238674533202"
}

def extraer_metricas_meta():
    print("Iniciando extracción oficial mediante Meta Graph API...")
    resultados_finales = []
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    
    for cliente, page_id in CLIENTES.items():
        # Endpoint oficial para extraer seguidores y likes de la página
        url = f"https://graph.facebook.com/v18.0/{page_id}?fields=followers_count,fan_count&access_token={META_TOKEN}"
        
        try:
            respuesta = requests.get(url).json()
            
            if 'error' in respuesta:
                print(f"❌ Error de permisos con {cliente}: {respuesta['error']['message']}")
                continue
                
            seguidores = respuesta.get('followers_count', 0)
            likes = respuesta.get('fan_count', 0)
            
            print(f"✅ {cliente} procesado: {seguidores} Seguidores.")
            
            # Estructura lista para enviar a tu Google Sheet
            resultados_finales.append([
                fecha_hoy,
                cliente,
                "Facebook",
                seguidores,
                likes
            ])
            
        except Exception as e:
            print(f"❌ Error de conexión con {cliente}: {str(e)}")
            
    return resultados_finales

if __name__ == "__main__":
    datos_extraidos = extraer_metricas_meta()
    
    # Aquí se mantiene tu lógica original de Google Sheets (gspread)
    # que toma la variable 'datos_extraidos' y la escribe en tu archivo 
    # "Resultados clientes EMPREADICTOS"
    
    print("Flujo completado. Datos listos para el cuadro de seguimiento.")
