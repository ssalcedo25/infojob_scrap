# Módulo encargado de la interacción con el usuario a través de la terminal.
# ui/terminal.py
from config import FECHA_PUBLICACION, EXPERIENCIA_MINIMA

def obtener_preferencias_usuario():
    """
    Dialoga con el usuario para obtener sus preferencias de búsqueda y filtros,
    mostrando opciones válidas para evitar errores y mejorar la experiencia.
    """
    
    # Usamos flush=True para asegurar que los prints aparezcan inmediatamente
    # en la terminal antes de que el input pause el programa.
    
    print("="*50, flush=True)
    print("🤖 Asistente de Búsqueda de Empleo InfoJobs 🤖", flush=True)
    print("="*50, flush=True)

    # --- Preguntas Generales y Palabras Clave ---
    termino_general = input("➡️ 1. ¿Término general de búsqueda? (ej: Programador, Administrativo): ").lower()

    print("\n➡️ 2. Palabras clave específicas para puntuar (separadas por coma)", flush=True)
    print("   (ej: python, finanzas, fiscalidad, sap, aws)", flush=True)
    keywords_str = input("   > ")
    palabras_especificas = [k.strip().lower() for k in keywords_str.split(',') if k.strip()]

    print("\n--- Filtros Adicionales (deja en blanco para omitir) ---", flush=True)
    
    # --- Filtros con entrada de texto libre (procesados como listas) ---
    provincias_str = input("➡️ 3. Provincias (separadas por coma, ej: Navarra, Murcia, Madrid): ")
    provincias = [p.strip().lower() for p in provincias_str.split(',') if p.strip()]

    modalidad_str = input("➡️ 4. Modalidad (separadas por coma, ej: remoto, hibrido, presencial): ")
    modalidades = [m.strip().lower() for m in modalidad_str.split(',') if m.strip()]

    contrato_str = input("➡️ 5. Tipo de contrato (separados por coma, ej: indefinido, formativo): ")
    contratos = [c.strip().lower() for c in contrato_str.split(',') if c.strip()]
    
    jornada_str = input("➡️ 6. Jornada laboral (separadas por coma, ej: completa, parcial): ")
    jornadas = [j.strip().lower() for j in jornada_str.split(',') if j.strip()]

    # --- Filtros con opciones guiadas ---
    print("\n➡️ 7. Fecha de publicación. Opciones disponibles:", flush=True)
    # Se muestran las claves del diccionario de configuración para guiar al usuario
    print(f"   {', '.join(FECHA_PUBLICACION.keys())}", flush=True)
    fecha_str = input("   > ").lower()

    print("\n➡️ 8. Experiencia mínima. Opciones disponibles:", flush=True)
    # Se muestran las claves del diccionario de configuración para guiar al usuario
    print(f"   {', '.join(EXPERIENCIA_MINIMA.keys())}", flush=True)
    experiencia_str = input("   > ").lower()
    
    salario_min_str = input("\n➡️ 9. Salario mínimo anual deseado (solo números, ej: 30000): ")

    # --- Construcción del diccionario final de preferencias ---
    preferencias = {
        # Si el término es vacío, se usa "oferta" por defecto para buscar todo
        "termino_general": termino_general if termino_general else "oferta",
        "palabras_especificas": palabras_especificas,
        "provincias": provincias,
        "modalidades": modalidades,
        "contratos": contratos,
        "jornadas": jornadas,
        "fecha_publicacion": fecha_str,
        "experiencia_min": experiencia_str,
        # Se verifica que el salario sea un número antes de añadirlo
        "salario_min": salario_min_str if salario_min_str.isdigit() else "",
    }
    
    print("\n👍 ¡Perfecto! Comenzando la búsqueda con tus preferencias...", flush=True)
    return preferencias