# main.py
import time
from ui.terminal import obtener_preferencias_usuario
from scraping.infojobs_scraper import obtener_ofertas_candidatas, analizar_ofertas_en_detalle
from core.scoring import calcular_puntuacion
from storage.csv_writer import guardar_ofertas_en_csv
from config import PUNTUACION_MINIMA_PARA_GUARDAR, BONUS_PUNTUACION_TITULO

def main():
    inicio = time.time()
    preferencias = obtener_preferencias_usuario()

    # --- FASE 1: Búsqueda rápida en la API ---
    ofertas_api = obtener_ofertas_candidatas(preferencias)
    if not ofertas_api:
        print("El proceso ha finalizado porque no se encontraron ofertas en la Fase 1.")
        return

    ofertas_a_analizar = ofertas_api[:50] # Limita a las primeras 50 ofertas para evitar sobrecarga

    # --- FASE 2: Scraping detallado para enriquecer datos ---
    print(f"\n🔍 [FASE 2] Analizando las primeras {len(ofertas_a_analizar)} de {len(ofertas_api)} ofertas...")
    ofertas_detalladas = analizar_ofertas_en_detalle(ofertas_a_analizar) # Pasa la lista limitada

    # --- FASE 3: Puntuación y filtrado ---
    print(f"\n💯 [FASE 3] Puntuando y filtrando {len(ofertas_detalladas)} ofertas...", flush=True)
    
    PALABRAS_CLAVE_SCORING = {palabra: 2 for palabra in preferencias["palabras_especificas"]}
    
    ofertas_finales = []
    for oferta in ofertas_detalladas:
        puntuacion, tecnologias = calcular_puntuacion(oferta, PALABRAS_CLAVE_SCORING, BONUS_PUNTUACION_TITULO)
        
        if puntuacion >= PUNTUACION_MINIMA_PARA_GUARDAR:
            oferta['puntuacion'] = puntuacion
            oferta['tecnologias'] = tecnologias
            ofertas_finales.append(oferta)
            print(f"  -> ACEPTADA ({puntuacion} pts): {oferta['titulo']}", flush=True)
        else:
            print(f"  -> DESCARTADA ({puntuacion} pts): {oferta['titulo']}", flush=True)

    # --- FASE 4: Guardado en CSV ---
    guardar_ofertas_en_csv(ofertas_finales)
    
    fin = time.time()
    print(f"\n🎉 --- PROCESO COMPLETADO EN {((fin - inicio) / 60):.2f} MINUTOS --- 🎉", flush=True)

if __name__ == "__main__":
    main()