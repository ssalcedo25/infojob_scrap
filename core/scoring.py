def calcular_puntuacion(oferta, palabras_clave, bonus_titulo):
    """
    Calcula una puntuación para una oferta basada en palabras clave dinámicas
    y un bonus que se reciben como parámetros.
    """
    puntuacion = 0
    # Combina descripción y título para la búsqueda
    texto_a_buscar = (oferta.get('descripcion', '') + ' ' + oferta.get('titulo', '')).lower()
    titulo = oferta.get('titulo', '').lower()
    
    palabras_encontradas = set()

    # Itera sobre las palabras clave y sus pesos recibidos como parámetro
    for palabra, peso in palabras_clave.items():
        if palabra.lower() in texto_a_buscar:
            puntuacion += peso
            palabras_encontradas.add(palabra)
            # Aplica bonus si la palabra también está en el título
            if palabra.lower() in titulo:
                puntuacion += bonus_titulo

    return puntuacion, sorted(list(palabras_encontradas))