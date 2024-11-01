# archivo: app/actions/distance_calculation_action.py

import requests
from geopy.distance import geodesic  # Asegurarse de importar geodesic aquí


class DistanceCalculationAction:
    SAN_ANTONIO_COORDS = (29.4241, -98.4936)  # Coordenadas de San Antonio, TX
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self):
        self.contact_info = "Por favor, comuníquese con nosotros al teléfono (XXX-XXX-XXXX) o al correo contacto@empresa.com para obtener más información."

    def geocode_address(self, address):
        """Convierte la dirección en coordenadas usando la API de Nominatim."""
        params = {
            'q': address,
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

            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
            else:
                # En lugar de lanzar una excepción, devolvemos None para manejarlo en BoxRequestAction
                return None
        
        except requests.exceptions.RequestException:
            # Error de conexión, devolvemos None para manejarlo en el flujo
            return None

    def calculate_distance_and_cost(self, origin_address, destination_address, cost_per_mile):
        origin_coords = self.geocode_address(origin_address)
        destination_coords = self.geocode_address(destination_address)

        if not origin_coords or not destination_coords:
            return None, None  # Devuelve None si no se encuentran coordenadas

        # Calcular la distancia y el costo
        distance = geodesic(origin_coords, destination_coords).miles
        cost = distance * cost_per_mile
        return distance, cost
