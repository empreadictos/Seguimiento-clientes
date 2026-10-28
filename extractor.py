import requests
from bs4 import BeautifulSoup
import time
import json
import gspread
from google.oauth2.service_account import Credentials
import os
import re
from datetime import datetime

print("🤖 Iniciando extracción de seguidores...")

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credenciales_json = os.environ.get('GOOGLE_CREDENTIALS')
credenciales_dict = json.loads(credenciales_json)
credenciales = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
cliente_gspread = gspread.authorize(credenciales)

ID_DOCUMENTO = "16JMjUvs0F4JYq2fiNupFITNmyqOSERUgQx6ZX1DSqrg"
hoja = cliente_gspread.open_by_key(ID_DOCUMENTO).sheet1

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

for perfil in perfiles:
    print(f"\n🔍 Buscando seguidores de {perfil['cliente']} en {perfil['red']}...")
    url_busqueda = f"https://www.google.com/search?q=site:{perfil['url']}"
    
    try:
        respuesta = requests.get(url_busqueda, headers=disfraz)
        lentes = BeautifulSoup(respuesta.text, 'html.parser')
        texto = lentes.get_text().lower()
        
        # Truco para extraer números cerca de la palabra seguidores/followers
        estado = "No se detectó número"
        match = re.search(r'([\d.,kmb]+)\s*(?:seguidores|followers|me gusta)', texto)
        
        if match:
            estado = f"{match.group(1).upper()} Seguidores"
        
        fila_nueva = [fecha_hoy, perfil['cliente'], perfil['red'], perfil['url'], estado]
        hoja.append_row(fila_nueva)
        print(f"✅ Guardado: {estado}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    time.sleep(3)
