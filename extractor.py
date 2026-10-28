import requests
from bs4 import BeautifulSoup
import time
import json
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime

print("🤖 Iniciando la extracción y conexión con Google Sheets...")

# 1. Configuración de Google Sheets
# Leemos la llave secreta que guardamos en la caja fuerte de GitHub
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credenciales_json = os.environ.get('GOOGLE_CREDENTIALS')
credenciales_dict = json.loads(credenciales_json)
credenciales = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
cliente_gspread = gspread.authorize(credenciales)

# 2. Abrir el archivo exacto (usamos el ID de tu enlace)
# El ID es lo que está entre "/d/" y "/edit" en tu enlace
ID_DOCUMENTO = "16JMjUvs0F4JYq2fiNupFITNmyqOSERUgQx6ZX1DSqrg"
hoja = cliente_gspread.open_by_key(ID_DOCUMENTO).sheet1

print("✅ Conectado exitosamente al Cuadro de Métricas.")

# 3. Lista de perfiles a buscar
perfiles = [
    {"cliente": "Empreadictos", "red": "Instagram", "url": "instagram.com/empreadictos"},
    {"cliente": "Naty Torrente", "red": "Instagram", "url": "instagram.com/natytorrente"},
    {"cliente": "Espacio Macala", "red": "Instagram", "url": "instagram.com/espacio_macala"},
    {"cliente": "Espacio Macala", "red": "TikTok", "url": "tiktok.com/@espaciomacala"},
    {"cliente": "Naty Torrente", "red": "TikTok", "url": "tiktok.com/@naty.torrente"},
    {"cliente": "Empreadictos", "red": "TikTok", "url": "tiktok.com/@empreadictos"},
    {"cliente": "Empreadictos", "red": "Facebook", "url": "facebook.com/empreadictoscol"},
    {"cliente": "Naty Torrente", "red": "Facebook", "url": "facebook.com/profile.php?id=61595734711890"},
    {"cliente": "Espacio Macala", "red": "Facebook", "url": "facebook.com/Espaciomacala"},
    {"cliente": "Nicolás Martínez", "red": "LinkedIn", "url": "linkedin.com/in/nicolas-martinez-mayorga-48100b106"},
    {"cliente": "Dubán Parra", "red": "LinkedIn", "url": "linkedin.com/in/duban-parra-romero-15a743190"}
]

disfraz = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
fecha_hoy = datetime.now().strftime("%Y-%m-%d")

# 4. Iniciar la extracción y escritura
for perfil in perfiles:
    print(f"\n🔍 Analizando {perfil['red']} de {perfil['cliente']}...")
    url_busqueda = f"https://www.google.com/search?q=site:{perfil['url']}"
    
    try:
        respuesta = requests.get(url_busqueda, headers=disfraz)
        lentes = BeautifulSoup(respuesta.text, 'html.parser')
        texto = lentes.get_text().lower()
        
        estado = "Revisado (Falta ajustar extracción de número)"
        if "seguidores" in texto or "followers" in texto or "contactos" in texto or "me gusta" in texto:
             estado = "Datos detectados"
        
        # Escribir la fila en Google Sheets
        fila_nueva = [fecha_hoy, perfil['cliente'], perfil['red'], perfil['url'], estado]
        hoja.append_row(fila_nueva)
        print(f"✅ Fila agregada al Sheet: {fila_nueva}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    time.sleep(3) 

print("\n🏁 ¡Misión terminada y datos guardados en tu Drive!")
