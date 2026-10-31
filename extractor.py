import os
import requests
import gspread
import json
from datetime import datetime

META_TOKEN = os.environ.get('META_TOKEN')
GOOGLE_CREDS_JSON = os.environ.get('GOOGLE_CREDENTIALS')

# Ya incluí los IDs de Facebook que rescaté de tus mensajes anteriores
CLIENTES = {
    "Naty Torrente": {"ig_id": "17841413473849283", "fb_id": "1520359784483889", "sheet": "Naty Torrente"},
    "Espacio Macala": {"ig_id": "17841477438562593", "fb_id": "957947710741211", "sheet": "Espacio Macala"},
    "Empreadictos": {"ig_id": "17841400527891627", "fb_id": "653238674533202", "sheet": "Empreadictos"}
}

# Cantidad de publicaciones recientes a extraer por cada red (para no saturar tu Excel)
LIMITE_POSTS = 5

def extraer_datos_completos():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    filas_por_cliente = {}

    for cliente, datos in CLIENTES.items():
        ig_id = datos["ig_id"]
        fb_id = datos["fb_id"]
        filas_cliente = []
        print(f"--- Procesando Publicaciones de {cliente} ---")

        try:
            # 1. Seguidores Totales IG y FB
            res_ig_basic = requests.get(f"https://graph.facebook.com/v18.0/{ig_id}?fields=followers_count&access_token={META_TOKEN}").json()
            seguidores_ig = res_ig_basic.get('followers_count', 0)

            res_fb_basic = requests.get(f"https://graph.facebook.com/v18.0/{fb_id}?fields=followers_count&access_token={META_TOKEN}").json()
            seguidores_fb = res_fb_basic.get('followers_count', 0)

            # 2. Últimas publicaciones de INSTAGRAM
            url_ig_media = f"https://graph.facebook.com/v18.0/{ig_id}/media?fields=media_type,like_count,comments_count,permalink&limit={LIMITE_POSTS}&access_token={META_TOKEN}"
            res_ig_media = requests.get(url_ig_media).json()

            if 'data' in res_ig_media:
                for post in res_ig_media['data']:
                    fila = [
                        fecha_hoy,
                        "Instagram",
                        seguidores_ig,
                        post.get('media_type', 'N/A'),
                        post.get('like_count', 0),
                        post.get('comments_count', 0),
                        post.get('permalink', 'N/A')
                    ]
                    filas_cliente.append(fila)

            # 3. Últimas publicaciones de FACEBOOK
            url_fb_posts = f"https://graph.facebook.com/v18.0/{fb_id}/posts?fields=message,permalink_url,likes.summary(true),comments.summary(true)&limit={LIMITE_POSTS}&access_token={META_TOKEN}"
            res_fb_posts = requests.get(url_fb_posts).json()

            if 'data' in res_fb_posts:
                for post in res_fb_posts['data']:
                    likes_fb = post.get('likes', {}).get('summary', {}).get('total_count', 0)
                    comments_fb = post.get('comments', {}).get('summary', {}).get('total_count', 0)
                    
                    # Cortamos el texto del post para que no sea gigante en el Excel
                    mensaje = post.get('message', 'Publicación sin texto')[:40] + "..." 
                    
                    fila = [
                        fecha_hoy,
                        "Facebook",
                        seguidores_fb,
                        mensaje,
                        likes_fb,
                        comments_fb,
                        post.get('permalink_url', 'N/A')
                    ]
                    filas_cliente.append(fila)

            filas_por_cliente[cliente] = filas_cliente
            print(f"✅ Se obtuvieron {len(filas_cliente)} publicaciones de {cliente}")

        except Exception as e:
            print(f"❌ Error extrayendo datos de {cliente}: {str(e)}")

    return filas_por_cliente

def guardar_en_sheets(datos):
    print("Conectando con Google Sheets...")
    try:
        credenciales_dict = json.loads(GOOGLE_CREDS_JSON)
        gc = gspread.service_account_from_dict(credenciales_dict)
        doc = gc.open("Resultados clientes EMPREADICTOS")

        for cliente, filas in datos.items():
            nombre_pestana = CLIENTES[cliente]["sheet"]
            try:
                hoja = doc.worksheet(nombre_pestana)
                
                # Si la hoja está en blanco, le ponemos los títulos de las columnas automáticamente
                if len(hoja.get_all_values()) == 0:
                    hoja.append_row(["Fecha de Consulta", "Red Social", "Seguidores Totales", "Tipo / Mensaje", "Likes", "Comentarios", "Link del Post"])
                
                # Guardar todas las publicaciones encontradas
                for fila in filas:
                    hoja.append_row(fila)
                print(f"✅ {len(filas)} filas guardadas correctamente en '{nombre_pestana}'")
                
            except gspread.exceptions.WorksheetNotFound:
                print(f"❌ No se encontró la pestaña '{nombre_pestana}'. Revisa las mayúsculas/espacios.")

    except Exception as e:
        print(f"❌ Error escribiendo en Google Sheets: {str(e)}")

if __name__ == "__main__":
    datos = extraer_datos_completos()
    guardar_en_sheets(datos)
    print("Flujo 100% completado.")
