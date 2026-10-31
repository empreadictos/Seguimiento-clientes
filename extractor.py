import os
import requests
import gspread
import json
from datetime import datetime

META_TOKEN = os.environ.get('META_TOKEN')
GOOGLE_CREDS_JSON = os.environ.get('GOOGLE_CREDENTIALS')

CLIENTES = {
    "Naty Torrente": {"ig_id": "17841413473849283", "sheet": "Naty Torrente"},
    "Espacio Macala": {"ig_id": "17841477438562593", "sheet": "Espacio Macala"},
    "Empreadictos": {"ig_id": "17841400527891627", "sheet": "Empreadictos"}
}

def extraer_datos_avanzados():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    resultados_por_cliente = {}

    for cliente, datos in CLIENTES.items():
        ig_id = datos["ig_id"]
        print(f"--- Procesando a {cliente} ---")
        
        try:
            url_basic = f"https://graph.facebook.com/v18.0/{ig_id}?fields=followers_count&access_token={META_TOKEN}"
            res_basic = requests.get(url_basic).json()
            seguidores = res_basic.get('followers_count', 0)

            url_demo = f"https://graph.facebook.com/v18.0/{ig_id}/insights?metric=audience_gender_age&period=lifetime&access_token={META_TOKEN}"
            res_demo = requests.get(url_demo).json()
            audiencia_top = "No disp."
            if 'data' in res_demo and len(res_demo['data']) > 0:
                valores_demo = res_demo['data'][0]['values'][0]['value']
                if valores_demo:
                    audiencia_top = max(valores_demo, key=valores_demo.get)

            url_media = f"https://graph.facebook.com/v18.0/{ig_id}/media?fields=media_type,like_count,comments_count,permalink&limit=1&access_token={META_TOKEN}"
            res_media = requests.get(url_media).json()
            
            tipo_post, likes_post, comentarios_post, link_post = "N/A", 0, 0, "N/A"
            if 'data' in res_media and len(res_media['data']) > 0:
                ultimo_post = res_media['data'][0]
                tipo_post = ultimo_post.get('media_type', 'N/A')
                likes_post = ultimo_post.get('like_count', 0)
                comentarios_post = ultimo_post.get('comments_count', 0)
                link_post = ultimo_post.get('permalink', 'N/A')

            fila = [fecha_hoy, seguidores, audiencia_top, tipo_post, likes_post, comentarios_post, link_post]
            resultados_por_cliente[cliente] = fila
            print(f"✅ Datos obtenidos: {fila}")

        except Exception as e:
            print(f"❌ Error con {cliente}: {str(e)}")
            
    return resultados_por_cliente

def guardar_en_sheets_separados(datos_clasificados):
    print("Conectando con Google Sheets...")
    try:
        credenciales_dict = json.loads(GOOGLE_CREDS_JSON)
        gc = gspread.service_account_from_dict(credenciales_dict)
        doc = gc.open("Resultados clientes EMPREADICTOS")
        
        for cliente, fila in datos_clasificados.items():
            nombre_pestana = CLIENTES[cliente]["sheet"]
            try:
                hoja = doc.worksheet(nombre_pestana)
                hoja.append_row(fila)
                print(f"✅ Fila guardada en la pestaña '{nombre_pestana}'")
            except gspread.exceptions.WorksheetNotFound:
                print(f"❌ No se encontró la pestaña '{nombre_pestana}'")
                
    except Exception as e:
        print(f"❌ Error escribiendo en Google Sheets: {str(e)}")

if __name__ == "__main__":
    datos = extraer_datos_avanzados()
    guardar_en_sheets_separados(datos)
    print("Flujo 100% completado.")
