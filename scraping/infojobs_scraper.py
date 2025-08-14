import requests
import time
import json
import re
import random
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Se importan todos los diccionarios de configuración necesarios para los filtros
from config import (
    API_URL, HEADERS, PROVINCIAS, MODALIDAD, 
    TIPO_CONTRATO, JORNADA, FECHA_PUBLICACION, EXPERIENCIA_MINIMA
)

def obtener_ofertas_candidatas(preferencias):
    """
    Fase 1: Usa la API de InfoJobs para obtener una lista de ofertas inicial 
    basada en un diccionario de preferencias del usuario.
    """
    
    # --- Creación del diccionario de parámetros para la petición ---
    parametros = {
        'keyword': preferencias.get("termino_general", ""),  # Usar .get para evitar errores si la clave no existe
        'sortBy': 'RELEVANCE',
        'maxResults': 50,
    }

    # --- Traducción y adición de filtros verificados desde el diccionario de preferencias ---
    ids_provincias = [PROVINCIAS[p] for p in preferencias.get("provincias", []) if p in PROVINCIAS]
    if ids_provincias: 
        parametros['provinceIds'] = ','.join(ids_provincias)

    ids_modalidades = [MODALIDAD[m] for m in preferencias.get("modalidades", []) if m in MODALIDAD]
    if ids_modalidades: 
        parametros['teleworkingIds'] = ','.join(ids_modalidades)

    ids_contratos = [TIPO_CONTRATO[c] for c in preferencias.get("contratos", []) if c in TIPO_CONTRATO]
    if ids_contratos: 
        parametros['contractTypeIds'] = ','.join(ids_contratos)
    
    ids_jornadas = [JORNADA[j] for j in preferencias.get("jornadas", []) if j in JORNADA]
    if ids_jornadas: 
        parametros['workdayIds'] = ','.join(ids_jornadas)

    salario_min = preferencias.get("salario_min")
    if salario_min:
        parametros['salaryMin'] = salario_min

    valor_fecha = FECHA_PUBLICACION.get(preferencias.get("fecha_publicacion"))
    if valor_fecha:
        parametros['sinceDate'] = valor_fecha

    valor_experiencia = EXPERIENCIA_MINIMA.get(preferencias.get("experiencia_min"))
    if valor_experiencia:
        parametros['experienceMin'] = valor_experiencia
    
    # --- Inicio de la comunicación con la API ---
    print("\n🚀 [FASE 1] Realizando búsqueda en la API con los siguientes filtros:")
    for key, value in parametros.items():
        print(f"     -> {key}: {value}", flush=True)

    session = requests.Session()
    session.headers.update(HEADERS)

    pagina_actual = 1
    ofertas_candidatas_api = []
    
    # Bucle para recorrer todas las páginas de resultados
    while True:
        parametros['page'] = pagina_actual

        try:
            respuesta = session.get(API_URL, params=parametros)
            respuesta.raise_for_status()
            datos = respuesta.json()
            ofertas_de_esta_pagina = datos.get('offers', [])
            
            if not ofertas_de_esta_pagina:
                print("✅ No se encontraron más ofertas en la API.", flush=True)
                break
            
            ofertas_candidatas_api.extend(ofertas_de_esta_pagina)
            
            total_paginas = datos.get('navigation', {}).get('totalPages', 1)
            if pagina_actual >= total_paginas:
                print(f"✅ Se han recogido todas las {total_paginas} páginas de la API.", flush=True)
                break
            
            print(f"     -> Página {pagina_actual}/{total_paginas} procesada...", flush=True)
            pagina_actual += 1
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la petición a la API: {e}.", flush=True)
            break

    print(f"\nRecogida de API completada. Total de ofertas candidatas: {len(ofertas_candidatas_api)}.", flush=True)
    return ofertas_candidatas_api

def analizar_ofertas_en_detalle(ofertas_candidatas_api):
    """
    Fase 2: Reconstruida con pausas aleatorias para evitar la detección de bots.
    """
    print("\n🔍 [FASE 2] Iniciando el análisis detallado con Playwright para enriquecer datos...")
    ofertas_detalladas = []
    if not ofertas_candidatas_api:
        return []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(user_agent=HEADERS['User-Agent'])
        page = context.new_page()

        for i, oferta_resumen in enumerate(ofertas_candidatas_api):
            link = oferta_resumen.get('link')
            if not link: continue
            
            url_oferta = urljoin("https://www.infojobs.net", link)
            titulo_resumen = oferta_resumen.get('title', 'SIN TITULO')
            print(f"   -> Analizando #{i+1}/{len(ofertas_candidatas_api)}: {titulo_resumen}", flush=True)

            try:
                page.goto(url_oferta, wait_until='domcontentloaded', timeout=30000)
                oferta_completa = None
                
                for intento in range(2):
                    if intento == 1:
                        print("     -> Reintentando extracción de datos tras la pausa...", flush=True)

                    html = page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    script_initial = soup.find('script', string=lambda t: t and 'window.__INITIAL_PROPS__' in t)
                    if script_initial and script_initial.string:
                        print("     -> Método encontrado: __INITIAL_PROPS__", flush=True)
                        match = re.search(r'JSON\.parse\("(.*)"\)', script_initial.string)
                        if match:
                            json_str = match.group(1).encode('utf-8').decode('unicode_escape')
                            json_data = json.loads(json_str)
                            oferta_completa = json_data.get('offer', {})

                    if not oferta_completa:
                        script_next = soup.find('script', {'id': '__NEXT_DATA__'})
                        if script_next and script_next.string:
                            print("     -> Método encontrado: __NEXT_DATA__", flush=True)
                            json_data = json.loads(script_next.string)
                            oferta_completa = json_data.get('props', {}).get('pageProps', {}).get('offer', {})
                    
                    if oferta_completa:
                        break
                    
                    if intento == 0:
                        print("     ⚠️ No se encontraron datos. Posible CAPTCHA.", flush=True)
                        print("     ✅ Resuelve el CAPTCHA y pulsa 'Resume' (▶️) en la ventana de Playwright Inspector.", flush=True)
                        page.pause()
                
                if oferta_completa:
                    oferta_estandarizada = {
                        'titulo': oferta_completa.get('title', 'N/A'),
                        'empresa': oferta_completa.get('profile', {}).get('name', 'N/A'),
                        'ciudad': oferta_completa.get('city', {}).get('value', 'N/A'),
                        'provincia': oferta_completa.get('province', {}).get('value', 'N/A'),
                        'modalidad': oferta_completa.get('teleworking', {}).get('value', 'N/A'),
                        'experiencia': oferta_completa.get('experienceMin', {}).get('value', 'N/A'),
                        'salario': oferta_completa.get('salaryDescription', "No especificado"),
                        'descripcion': oferta_completa.get('description', ''),
                        'enlace': url_oferta
                    }
                else:
                    print("     ❌ No se pudo extraer información detallada. Usando datos de la API.", flush=True)
                    oferta_estandarizada = {
                        'titulo': oferta_resumen.get('title', 'N/A'), 'empresa': oferta_resumen.get('profile', {}).get('name', 'N/A'),
                        'ciudad': oferta_resumen.get('city', 'N/A'), 'provincia': oferta_resumen.get('province', {}).get('value', 'N/A'),
                        'modalidad': oferta_resumen.get('teleworking', 'N/A'), 'experiencia': oferta_resumen.get('experienceMin', {}).get('value', 'N/A'),
                        'salario': oferta_resumen.get('salaryDescription', 'No especificado'), 'descripcion': oferta_resumen.get('description', ''),
                        'enlace': urljoin("https://www.infojobs.net", oferta_resumen.get('link', ''))
                    }
                
                ofertas_detalladas.append(oferta_estandarizada)

            except Exception as e:
                print(f"     ❌ Error fatal al procesar la oferta: {type(e).__name__}. Usando datos de la API.", flush=True)
                ofertas_detalladas.append({
                    'titulo': oferta_resumen.get('title', 'N/A'), 'empresa': oferta_resumen.get('profile', {}).get('name', 'N/A'),
                    'ciudad': oferta_resumen.get('city', 'N/A'), 'provincia': oferta_resumen.get('province', {}).get('value', 'N/A'),
                    'modalidad': oferta_resumen.get('teleworking', 'N/A'), 'experiencia': oferta_resumen.get('experienceMin', {}).get('value', 'N/A'),
                    'salario': oferta_resumen.get('salaryDescription', 'No especificado'), 'descripcion': oferta_resumen.get('description', ''),
                    'enlace': urljoin("https://www.infojobs.net", oferta_resumen.get('link', ''))
                })
                continue
            
            # --- PAUSA ALEATORIA PARA SIMULAR COMPORTAMIENTO HUMANO ---
            pausa = random.uniform(2, 5)
            print(f"     -> Pausa de {pausa:.1f} segundos...", flush=True)
            time.sleep(pausa)

        browser.close()
    
    print(f"\n✅ Análisis detallado completado.")
    return ofertas_detalladas
    """
    Fase 2: Reconstruida para buscar PRIMERO __INITIAL_PROPS__ y luego __NEXT_DATA__ como fallback,
    manejando CAPTCHAs de forma inteligente.
    """
    print("\n🔍 [FASE 2] Iniciando el análisis detallado con Playwright para enriquecer datos...")
    ofertas_detalladas = []
    if not ofertas_candidatas_api:
        return []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(user_agent=HEADERS['User-Agent'])
        page = context.new_page()

        for i, oferta_resumen in enumerate(ofertas_candidatas_api):
            link = oferta_resumen.get('link')
            if not link: continue
            
            url_oferta = urljoin("https://www.infojobs.net", link)
            titulo_resumen = oferta_resumen.get('title', 'SIN TITULO')
            print(f"   -> Analizando #{i+1}/{len(ofertas_candidatas_api)}: {titulo_resumen}", flush=True)

            try:
                page.goto(url_oferta, wait_until='domcontentloaded', timeout=30000)
                
                oferta_completa = None
                
                # Bucle de reintento, igual que en tu versión original
                for intento in range(2):
                    if intento == 1:
                        print("     -> Reintentando extracción de datos tras la pausa...", flush=True)

                    html = page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 1. Primer intento: buscar __INITIAL_PROPS__
                    script_initial = soup.find('script', string=lambda t: t and 'window.__INITIAL_PROPS__' in t)
                    if script_initial and script_initial.string:
                        print("     -> Método encontrado: __INITIAL_PROPS__", flush=True)
                        match = re.search(r'JSON\.parse\("(.*)"\)', script_initial.string)
                        if match:
                            json_str = match.group(1).encode('utf-8').decode('unicode_escape')
                            json_data = json.loads(json_str)
                            oferta_completa = json_data.get('offer', {})

                    # 2. Segundo intento (fallback): buscar __NEXT_DATA__
                    if not oferta_completa:
                        script_next = soup.find('script', {'id': '__NEXT_DATA__'})
                        if script_next and script_next.string:
                            print("     -> Método encontrado: __NEXT_DATA__", flush=True)
                            json_data = json.loads(script_next.string)
                            oferta_completa = json_data.get('props', {}).get('pageProps', {}).get('offer', {})
                    
                    # Si hemos encontrado datos, salimos del bucle de reintento
                    if oferta_completa:
                        break
                    
                    # Si no encontramos datos en el primer intento, pausamos para CAPTCHA
                    if intento == 0:
                        print("     ⚠️ No se encontraron datos. Posible CAPTCHA.", flush=True)
                        print("     ✅ Resuelve el CAPTCHA y pulsa 'Resume' (▶️) en la ventana de Playwright Inspector.", flush=True)
                        page.pause()
                
                # --- Estandarización de datos ---
                if oferta_completa:
                    # Usamos los datos ricos del scraping
                    oferta_estandarizada = {
                        'titulo': oferta_completa.get('title', 'N/A'),
                        'empresa': oferta_completa.get('profile', {}).get('name', 'N/A'),
                        'ciudad': oferta_completa.get('city', {}).get('value', 'N/A'),
                        'provincia': oferta_completa.get('province', {}).get('value', 'N/A'),
                        'modalidad': oferta_completa.get('teleworking', {}).get('value', 'N/A'),
                        'experiencia': oferta_completa.get('experienceMin', {}).get('value', 'N/A'),
                        'salario': oferta_completa.get('salaryDescription', "No especificado"),
                        'descripcion': oferta_completa.get('description', ''),
                        'enlace': url_oferta
                    }
                else:
                    # Si después de todo no hay datos, usamos el fallback de la API
                    print("     ❌ No se pudo extraer información detallada. Usando datos de la API.", flush=True)
                    oferta_estandarizada = {
                        'titulo': oferta_resumen.get('title', 'N/A'),
                        'empresa': oferta_resumen.get('profile', {}).get('name', 'N/A'),
                        'ciudad': oferta_resumen.get('city', 'N/A'),
                        'provincia': oferta_resumen.get('province', {}).get('value', 'N/A'),
                        'modalidad': oferta_resumen.get('teleworking', 'N/A'),
                        'experiencia': oferta_resumen.get('experienceMin', {}).get('value', 'N/A'),
                        'salario': oferta_resumen.get('salaryDescription', 'No especificado'),
                        'descripcion': oferta_resumen.get('description', ''),
                        'enlace': urljoin("https://www.infojobs.net", oferta_resumen.get('link', ''))
                    }
                
                ofertas_detalladas.append(oferta_estandarizada)

            except Exception as e:
                print(f"     ❌ Error fatal al procesar la oferta: {type(e).__name__}. Usando datos de la API.", flush=True)
                # Fallback final en caso de error grave en la página
                ofertas_detalladas.append({
                    'titulo': oferta_resumen.get('title', 'N/A'),
                    'empresa': oferta_resumen.get('profile', {}).get('name', 'N/A'),
                    'ciudad': oferta_resumen.get('city', 'N/A'),
                    'provincia': oferta_resumen.get('province', {}).get('value', 'N/A'),
                    'modalidad': oferta_resumen.get('teleworking', 'N/A'),
                    'experiencia': oferta_resumen.get('experienceMin', {}).get('value', 'N/A'),
                    'salario': oferta_resumen.get('salaryDescription', 'No especificado'),
                    'descripcion': oferta_resumen.get('description', ''),
                    'enlace': urljoin("https://www.infojobs.net", oferta_resumen.get('link', ''))
                })
                continue

        browser.close()
    
    print(f"\n✅ Análisis detallado completado.")
    return ofertas_detalladas
    """
    Fase 2: Usa Playwright para visitar cada oferta y extraer datos detallados,
    incluyendo información que no viene en la API inicial, como el salario.
    """
    print("\n🔍 [FASE 2] Iniciando el análisis detallado con Playwright para enriquecer datos...")
    ofertas_detalladas = []
    if not ofertas_candidatas_api:
        return []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=50) # headless=True para que no se vea el navegador
        context = browser.new_context(user_agent=HEADERS['User-Agent'])
        page = context.new_page()

        for i, oferta_resumen in enumerate(ofertas_candidatas_api):
            link = oferta_resumen.get('link')
            if not link: continue
            
            url_oferta = urljoin("https://www.infojobs.net", link)
            titulo_resumen = oferta_resumen.get('title', 'SIN TITULO')
            print(f"    -> Analizando #{i+1}/{len(ofertas_candidatas_api)}: {titulo_resumen}", flush=True)

            try:
                page.goto(url_oferta, wait_until='domcontentloaded', timeout=20000)
                
                oferta_completa = None
                script_next = page.locator('script#__NEXT_DATA__').inner_text()
                
                if script_next:
                    json_data = json.loads(script_next)
                    oferta_completa = json_data.get('props', {}).get('pageProps', {}).get('offer', {})
                else: # Fallback por si no encuentra el script
                    print("         ⚠️ No se encontró __NEXT_DATA__, usando datos de la API.", flush=True)
                    oferta_completa = oferta_resumen
                
                # Estandarizamos el diccionario de salida con los datos más ricos
                salario_desc = "No especificado"
                if 'salaryDescription' in oferta_completa:
                    salario_desc = oferta_completa['salaryDescription']

                oferta_estandarizada = {
                    'titulo': oferta_completa.get('title', 'N/A'),
                    'empresa': oferta_completa.get('profile', {}).get('name', 'N/A'),
                    'ciudad': oferta_completa.get('city', 'N/A'),
                    'provincia': oferta_completa.get('province', {}).get('value', 'N/A'),
                    'modalidad': oferta_completa.get('teleworking', {}).get('value', 'N/A'),
                    'experiencia': oferta_completa.get('experienceMin', {}).get('value', 'N/A'),
                    'salario': salario_desc,
                    'descripcion': oferta_completa.get('description', ''),
                    'enlace': url_oferta
                }
                ofertas_detalladas.append(oferta_estandarizada)

            except Exception as e:
                print(f"         ❌ Error grave al analizar la oferta: {type(e).__name__}. Usando datos de la API.", flush=True)
                # Si falla el scraping, usamos los datos básicos de la API para no perder la oferta
                ofertas_detalladas.append({
                    'titulo': oferta_resumen.get('title', 'N/A'),
                    'empresa': oferta_resumen.get('profile', {}).get('name', 'N/A'),
                    'ciudad': oferta_resumen.get('city', 'N/A'),
                    'provincia': oferta_resumen.get('province', {}).get('value', 'N/A'),
                    'modalidad': oferta_resumen.get('teleworking', {}).get('value', 'N/A'),
                    'experiencia': oferta_resumen.get('experienceMin', {}).get('value', 'N/A'),
                    'salario': oferta_resumen.get('salaryDescription', 'No especificado'),
                    'descripcion': oferta_resumen.get('description', ''),
                    'enlace': urljoin("https://www.infojobs.net", oferta_resumen.get('link', ''))
                })
                continue

        browser.close()
    
    print(f"✅ Análisis detallado completado.")
    return ofertas_detalladas