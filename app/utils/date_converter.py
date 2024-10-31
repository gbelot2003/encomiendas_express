# archivo: app/utils/date_converter.py

from datetime import datetime, timedelta
import re
import locale

# Asegurar configuración regional en español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Cambiar según el sistema; 'es_ES.UTF-8' para sistemas Unix

class DateConverter:
    @staticmethod
    def parse_date(natural_date_str):
        """Convierte una fecha en texto a un objeto datetime."""
        natural_date_str = natural_date_str.lower().strip()

        # Hoy a las HH:MM (por ejemplo, "hoy a las 8 pm")
        if "hoy" in natural_date_str:
            return DateConverter._convert_today(natural_date_str)

        # Mañana a las HH:MM (por ejemplo, "mañana a las 12 pm")
        elif "mañana" in natural_date_str:
            return DateConverter._convert_tomorrow(natural_date_str)

        # Fecha completa en formato específico (por ejemplo, "31 de octubre 20:00")
        elif re.match(r"\d{1,2} de \w+ \d{1,2}:\d{2}", natural_date_str):
            return DateConverter._convert_specific_date(natural_date_str)

        # Otros formatos pueden ser agregados aquí
        else:
            raise ValueError(f"Formato de fecha no reconocido: {natural_date_str}")

    @staticmethod
    def _convert_today(natural_date_str):
        """Convierte expresiones como 'hoy a las 8 pm'."""
        today = datetime.now()
        hour, minute = DateConverter._extract_time(natural_date_str)
        return today.replace(hour=hour, minute=minute, second=0, microsecond=0)

    @staticmethod
    def _convert_tomorrow(natural_date_str):
        """Convierte expresiones como 'mañana a las 12 pm'."""
        tomorrow = datetime.now() + timedelta(days=1)
        hour, minute = DateConverter._extract_time(natural_date_str)
        return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)

    @staticmethod
    def _convert_specific_date(natural_date_str):
        """Convierte expresiones como '31 de octubre 20:00' a datetime."""
        try:
            return datetime.strptime(natural_date_str, "%d de %B %H:%M")
        except ValueError as e:
            raise ValueError(f"Error en el formato de fecha específica: {e}")

    @staticmethod
    def _extract_time(natural_date_str):
        """Extrae la hora y minutos de expresiones como 'a las 8 pm' o 'a las 6:30 pm'."""
        match = re.search(r"(\d{1,2}):?(\d{2})?\s*([ap]\.?m\.?)", natural_date_str)
        if not match:
            raise ValueError("No se encontró una hora válida en la expresión.")

        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        period = match.group(3)

        # Convertir la hora al formato de 24 horas
        if 'p' in period and hour != 12:
            hour += 12
        elif 'a' in period and hour == 12:
            hour = 0

        return hour, minute
