import os
import requests
import gspread
import json
from datetime import datetime

META_TOKEN = os.environ.get('META_TOKEN')
GOOGLE_CREDS_JSON = os.environ.get('GOOGLE_CREDENTIALS')

CLIENTES = {
    "Naty Torrente": {"ig_id": "17841413473849283", "fb_id": "1520359784483889", "sheet": "Naty Torrente"},
    "Espacio Macala": {"ig_id": "17841477438562593", "fb_id": "957947710741211", "sheet": "Espacio Macala"},
    "Empreadictos": {"ig_id": "17841400527891627", "fb_id": "653238674533202", "sheet": "Empreadictos"}
}

LIMITE_POSTS = 15

def procesar_clientes():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    
    print("Conectando con Google Sheets para memoria histórica...")
    try:
        credenciales_dict = json.loads(GOOGLE_CREDS_JSON)
        gc = gspread.service_account_from_dict(credenciales_dict)
        doc = gc.open("Resultados clientes EMPREADICTOS")
    except Exception as e:
        print(f"❌ Error crítico conectando a Google Sheets: {str(e)}")
        return

    for cliente, datos in CLIENTES.items():
        ig_id = datos["ig_id"]
        fb_id = datos["fb_id"]
        nombre_pestana = datos["sheet"]
        print(f"\n--- Analizando interacciones de {cliente} ---")
        
        try:
            hoja = doc.worksheet(nombre_pestana)
        except gspread.exceptions.WorksheetNotFound:
            print(f"❌ No se encontró la pestaña '{nombre_pestana}'. Saltando.")
            continue

        # 1. LEER EL PASADO (Memoria del Excel)
        registros = hoja.get_all_values()
        historial_links = {}
        
        if len(registros) == 0:
            # Añadimos la columna Visualizaciones
            hoja.append_row(["Fecha de Consulta", "Red Social", "Seguidores Totales", "Fecha del Post", "Tipo / Mensaje", "Likes Totales", "Comentarios Totales", "Visualizaciones (Views)", "Interacción Hoy (Incremento)", "Link del Post"])
        else:
            for fila in registros[1:]:
                if len(fila) >= 10:
                    link = fila[9]
                    try:
                        likes_viejos = int(fila[5])
                        comentarios_viejos = int(fila[6])
                        historial_links[link] = {'likes': likes_viejos, 'comentarios': comentarios_viejos}
                    except ValueError:
                        pass

        filas_a_guardar = []

        # 2. EXTRAER SEGUIDORES TOTALES
        seguidores_ig = 0
        seguidores_fb = 0
        try:
            res_ig_basic = requests.get(f"https://graph.facebook.com/v18.0/{ig_id}?fields=followers_count&access_token={META_TOKEN}").json()
            seguidores_ig = res_ig_basic.get('followers_count', 0)
            
            res_fb_basic = requests.get(f"https://graph.facebook.com/v18.0/{fb_id}?fields=followers_count&access_token={META_TOKEN}").json()
            seguidores_fb = res_fb_basic.get('followers_count', 0)
        except Exception as e:
            print(f"⚠️ Error obteniendo seguidores: {str(e)}")

        # 3. ANALIZAR INSTAGRAM
        url_ig = f"https://graph.facebook.com/v18.0/{ig_id}/media?fields=id,media_type,like_count,comments_count,permalink,timestamp&limit={LIMITE_POSTS}&access_token={META_TOKEN}"
        try:
            res_ig = requests.get(url_ig).json()
            if 'data' in res_ig:
                for post in res_ig['data']:
                    post_id = post.get('id')
                    link = post.get('permalink', 'N/A')
                    likes_actuales = post.get('like_count', 0)
                    comentarios_actuales = post.get('comments_count', 0)
                    fecha_post = post.get('timestamp', '')[:10]
                    tipo = post.get('media_type', 'N/A')
                    
                    # EXTRAER VISUALIZACIONES IG
                    views = 0
                    try:
                        metrica = 'plays' if tipo == 'VIDEO' else 'impressions'
                        url_views = f"https://graph.facebook.com/v18.0/{post_id}/insights?metric={metrica}&access_token={META_TOKEN}"
                        res_views = requests.get(url_views).json()
                        if 'data' in res_views and len(res_views['data']) > 0:
                            views = res_views['data'][0]['values'][0]['value']
                    except:
                        views = "N/D"

                    es_nuevo = (fecha_post == fecha_hoy)
                    incremento = ""
                    guardar = False

                    if es_nuevo:
                        incremento = "🌟 PUBLICACIÓN NUEVA"
                        guardar = True
                    else:
                        if link in historial_links:
                            diff_likes = likes_actuales - historial_links[link]['likes']
                            diff_comentarios = comentarios_actuales - historial_links[link]['comentarios']
                            if diff_likes > 0 or diff_comentarios > 0:
                                incremento = f"📈 INCREMENTO: +{diff_likes} Likes, +{diff_comentarios} Comentarios"
                                guardar = True
                        else:
                            incremento = "Registro Base (Para comparar mañana)"
                            guardar = True

                    if guardar:
                        filas_a_guardar.append([fecha_hoy, "Instagram", seguidores_ig, fecha_post, tipo, likes_actuales, comentarios_actuales, views, incremento, link])
        except Exception as e:
            print(f"❌ Error leyendo Instagram de {cliente}: {str(e)}")

        # 4. ANALIZAR FACEBOOK
        url_fb = f"https://graph.facebook.com/v18.0/{fb_id}/posts?fields=id,message,permalink_url,likes.summary(true),comments.summary(true),created_time&limit={LIMITE_POSTS}&access_token={META_TOKEN}"
        try:
            res_fb = requests.get(url_fb).json()
            if 'data' in res_fb:
                for post in res_fb['data']:
                    post_id = post.get('id')
                    link = post.get('permalink_url', 'N/A')
                    likes_actuales = post.get('likes', {}).get('summary', {}).get('total_count', 0)
                    comentarios_actuales = post.get('comments', {}).get('summary', {}).get('total_count', 0)
                    fecha_post = post.get('created_time', '')[:10]
                    mensaje = post.get('message', 'Sin texto')[:30] + "..."

                    # EXTRAER VISUALIZACIONES FB
                    views = 0
                    try:
                        url_views_fb = f"https://graph.facebook.com/v18.0/{post_id}/insights/post_impressions?access_token={META_TOKEN}"
                        res_views_fb = requests.get(url_views_fb).json()
                        if 'data' in res_views_fb and len(res_views_fb['data']) > 0:
                            views = res_views_fb['data'][0]['values'][0]['value']
                    except:
                        views = "N/D"

                    es_nuevo = (fecha_post == fecha_hoy)
                    incremento = ""
                    guardar = False

                    if es_nuevo:
                        incremento = "🌟 PUBLICACIÓN NUEVA"
                        guardar = True
                    else:
                        if link in historial_links:
                            diff_likes = likes_actuales - historial_links[link]['likes']
                            diff_comentarios = comentarios_actuales - historial_links[link]['comentarios']
                            if diff_likes > 0 or diff_comentarios > 0:
                                incremento = f"📈 INCREMENTO: +{diff_likes} Likes, +{diff_comentarios} Comentarios"
                                guardar = True
                        else:
                            incremento = "Registro Base (Para comparar mañana)"
                            guardar = True

                    if guardar:
                        filas_a_guardar.append([fecha_hoy, "Facebook", seguidores_fb, fecha_post, mensaje, likes_actuales, comentarios_actuales, views, incremento, link])
        except Exception as e:
            print(f"❌ Error leyendo Facebook de {cliente}: {str(e)}")

        # 5. GUARDAR EN EXCEL
        if filas_a_guardar:
            for fila in filas_a_guardar:
                hoja.append_row(fila)
            print(f"✅ Se guardaron {len(filas_a_guardar)} movimientos hoy en '{nombre_pestana}'")
        else:
            print(f"😴 No hubo interacciones nuevas hoy para {cliente}")

if __name__ == "__main__":
    procesar_clientes()
    print("Flujo 100% completado.")
