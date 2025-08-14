# config.py

BONUS_PUNTUACION_TITULO = 3
PUNTUACION_MINIMA_PARA_GUARDAR = 2

# --- DICCIONARIOS DE TRADUCCIÓN (Valores 100% Verificados) ---

PROVINCIAS = {
    'a coruña': '28', 'álava/araba': '2', 'alicante/alacant': '4', 'almería': '5',
    'asturias': '6', 'barcelona': '9', 'burgos': '10', 'cantabria': '13',
    'castellón/castelló': '14', 'ciudad real': '16', 'córdoba': '17', 'girona': '19',
    'guipúzcoa/gipuzkoa': '23', 'islas baleares/illes balears': '26', 'jaén': '27',
    'la rioja': '29', 'las palmas': '20', 'león': '30', 'lleida': '31', 'madrid': '33',
    'málaga': '34', 'murcia': '36', 'navarra': '37', 'pontevedra': '40', 'salamanca': '41',
    'santa cruz de tenerife': '46', 'sevilla': '43', 'tarragona': '45', 'toledo': '48',
    'valencia/valència': '49', 'valladolid': '50', 'vizcaya/bizkaia': '51', 'zaragoza': '53'
}
MODALIDAD = {'hibrido': '3', 'presencial': '1', 'remoto': '2'}
TIPO_CONTRATO = {
    'indefinido': '1', 'formativo': '3', 'de duracion determinada': '4',
    'fijo discontinuo': '8', 'a tiempo parcial': '9'
}
JORNADA = {'completa': '1', 'parcial': '2', 'indiferente': '10'}

# NUEVO: Diccionario para fechas, con valores verificados
FECHA_PUBLICACION = {
    'cualquier fecha': 'ANY',
    'ultimas 24h': '_24_HOURS',
    'ultima semana': '_7_DAYS',
    'ultimos 15 dias': '_15_DAYS',
}

# NUEVO: Diccionario para experiencia mínima, con valores verificados
EXPERIENCIA_MINIMA = {
    'sin experiencia': '_0_YEARS',
    '1 año': '_1_YEAR',
    '2 años': '_2_YEARS',
    '3 años': '_3_YEARS',
    '5 años': '_5_YEARS',
    '10 años': '_10_YEARS',
}

# --- CONFIGURACIÓN TÉCNICA ---
API_URL = "https://www.infojobs.net/webapp/offers/search"
HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Authorization': 'Basic anVjYW1oYzpzZWNyZXRv'
}
NOMBRE_ARCHIVO_CSV = 'ofertas_filtradas.csv'