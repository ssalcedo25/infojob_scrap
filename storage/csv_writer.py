import csv
from config import NOMBRE_ARCHIVO_CSV

def guardar_ofertas_en_csv(ofertas_finales):
    """
    Guarda la lista de ofertas finales en un archivo CSV.
    Añade las columnas de puntuación y tecnologías encontradas.
    """
    if not ofertas_finales:
        print("\nNo hay ofertas que cumplan los criterios para guardar.")
        return

    print(f"\n💾 Guardando {len(ofertas_finales)} ofertas en '{NOMBRE_ARCHIVO_CSV}'...")
    
    # Ordena las ofertas por puntuación, de mayor a menor
    ofertas_ordenadas = sorted(ofertas_finales, key=lambda x: x['puntuacion'], reverse=True)

    with open(NOMBRE_ARCHIVO_CSV, 'w', newline='', encoding='utf-8-sig') as archivo_csv:
        # Define las columnas del CSV, incluyendo las nuevas
        columnas = [
            'puntuacion', 'titulo', 'empresa', 'ciudad', 'modalidad', 
            'salario', 'experiencia', 'tecnologias', 'enlace'
        ]
        
        escritor_csv = csv.DictWriter(archivo_csv, fieldnames=columnas, extrasaction='ignore')
        escritor_csv.writeheader()
        
        for oferta in ofertas_ordenadas:
             # Convierte la lista de tecnologías en un string separado por comas
            oferta['tecnologias'] = ', '.join(oferta['tecnologias'])
            escritor_csv.writerow(oferta)

    print(f"¡Éxito! Archivo '{NOMBRE_ARCHIVO_CSV}' creado y ordenado por relevancia.")