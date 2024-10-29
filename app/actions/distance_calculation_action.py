# app/actions/distance_calculation_action.py
import requests
from geopy.distance import geodesic

class DistanceCalculationAction:
    SAN_ANTONIO_COORDS = (29.4241, -98.4936)  # Coordenadas de San Antonio, TX
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self, destination_address):
        self.destination_address = destination_address
        self.contact_info = "Por favor, comuníquese con nosotros al teléfono (XXX-XXX-XXXX) o al correo contacto@empresa.com para obtener más información."

    def geocode_address(self):
        """Convierte la dirección en coordenadas usando la API de Nominatim."""
        params = {
            'q': self.destination_address,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'emviosexpress/1.0 (gerardo.belot@gmail.com)'  # Reemplaza con tu información
        }
        try:
            response = requests.get(self.NOMINATIM_URL, params=params, headers=headers)
            response.raise_for_status()  # Verifica si hubo un error HTTP
            data = response.json()

            # Validar y extraer las coordenadas si se encuentran
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
            else:
                raise ValueError("No se encontraron coordenadas para la dirección proporcionada.")
        
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error de conexión con el servicio de geocodificación: {e}")
        except ValueError as e:
            raise ValueError(f"Error de geocodificación: {e}")

    def calculate_distance_and_cost(self, destination_coords):
        # Calcular la distancia desde San Antonio a las coordenadas del destino
        distance = geodesic(self.SAN_ANTONIO_COORDS, destination_coords).miles

        # Determinar el mensaje adecuado según la distancia
        if distance <= 30:
            cost = distance * 1  # 1 dólar por milla
            return f"La distancia es de {distance:.2f} millas. El costo es ${cost:.2f} USD."
        else:
            # Devuelve el mensaje de contacto si la distancia supera 30 millas
            return (f"La distancia desde {self.destination_address} hasta nuestras oficinas es de aproximadamente "
                    f"{distance:.2f} millas, lo cual excede nuestro rango de 30 millas. {self.contact_info}")

    def handle(self):
        try:
            # Geocodificar la dirección para obtener coordenadas
            destination_coords = self.geocode_address()
            # Retorna el mensaje específico de acuerdo a la distancia
            result = self.calculate_distance_and_cost(destination_coords)
            return result
        except ValueError as e:
            return str(e)
