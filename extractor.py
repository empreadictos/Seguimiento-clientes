import requests
from bs4 import BeautifulSoup
import time

print("🤖 Iniciando la extracción múltiple de perfiles de clientes...")

# Aquí está tu lista exacta de perfiles
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

# Nuestro disfraz para Google
disfraz = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# El robot va a revisar cada perfil uno por uno
for perfil in perfiles:
    print(f"\n🔍 Analizando {perfil['red']} de {perfil['cliente']}...")
    
    # Truco: Le pedimos a Google que busque específicamente dentro de esa URL
    url_busqueda = f"https://www.google.com/search?q=site:{perfil['url']}"
    
    try:
        respuesta = requests.get(url_busqueda, headers=disfraz)
        lentes = BeautifulSoup(respuesta.text, 'html.parser')
        texto = lentes.get_text().lower()
        
        # Buscamos palabras clave de métricas
        if "seguidores" in texto or "followers" in texto or "contactos" in texto or "me gusta" in texto:
            print(f"✅ ¡Éxito! Datos detectados en Google para {perfil['cliente']}.")
        else:
            print(f"⚠️ Google aún no muestra los números exactos en la vista previa para este enlace.")
            
    except Exception as e:
        print(f"❌ Error al buscar: {e}")
        
    # Le decimos al robot que espere 3 segundos antes de buscar el siguiente
    # (Si busca los 11 seguidos muy rápido, Google lo bloquea por parecer un virus)
    time.sleep(3) 

print("\n🏁 Misión terminada. Todos los perfiles revisados.")
