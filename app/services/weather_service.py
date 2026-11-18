import requests


class WeatherService:

    def __init__(self, api_base_url: str = "https://api.open-meteo.com/v1"):
        self.api_base_url = api_base_url

    def get_solar_radiation(self, latitude: float, longitude: float) -> dict:
        url = f"{self.api_base_url}/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "shortwave_radiation_sum,sunshine_duration",
            "forecast_days": 7,
            "timezone": "auto",
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            daily = data["daily"]

            radiation_values = daily["shortwave_radiation_sum"]
            sunshine_values = daily["sunshine_duration"]

            avg_radiation_mj = sum(radiation_values) / len(radiation_values)


            avg_radiation_kwh = avg_radiation_mj / 3.6

            avg_sunshine_seconds = sum(sunshine_values) / len(sunshine_values)
            avg_sunshine_hours = avg_sunshine_seconds / 3600

            return {
                "avg_radiation_kwh_m2_day": round(avg_radiation_kwh, 3),
                "avg_sunshine_hours": round(avg_sunshine_hours, 2),
            }
        except (requests.RequestException, KeyError, ZeroDivisionError, ValueError) as e:
            raise ConnectionError(f"Could not fetch solar radiation data: {e}") from e

    def get_wind_speed(self, latitude: float, longitude: float) -> dict:
        url = f"{self.api_base_url}/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "wind_speed_10m_max",
            "forecast_days": 7,
            "timezone": "auto",
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            wind_values = data["daily"]["wind_speed_10m_max"]

            avg_wind_kmh = sum(wind_values) / len(wind_values)
            avg_wind_ms = avg_wind_kmh / 3.6


            reference_speed_ms = 11.0
            estimated_factor = (avg_wind_ms / reference_speed_ms) ** 3
            estimated_factor = max(0.02, min(estimated_factor, 0.40))

            return {
                "avg_wind_speed_ms": round(avg_wind_ms, 2),
                "avg_capacity_factor": round(estimated_factor, 3),
            }
        except (requests.RequestException, KeyError, ZeroDivisionError, ValueError) as e:
            raise ConnectionError(f"Could not fetch wind speed data: {e}") from e

    def get_historical_weather(self, latitude: float, longitude: float,
                                 days: int = 365) -> dict:
        from datetime import date, timedelta

        end_date = date.today() - timedelta(days=2)
        start_date = end_date - timedelta(days=days)

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "shortwave_radiation_sum,wind_speed_10m_max",
            "timezone": "auto",
        }
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            daily = data["daily"]

            radiation_values = [v for v in daily["shortwave_radiation_sum"] if v is not None]
            wind_values = [v for v in daily["wind_speed_10m_max"] if v is not None]

            avg_radiation_kwh = (
                (sum(radiation_values) / len(radiation_values)) / 3.6
                if radiation_values else 0.0
            )
            avg_wind_ms = (
                (sum(wind_values) / len(wind_values)) / 3.6
                if wind_values else 0.0
            )


            hub_height_m = 15.0
            reference_height_m = 10.0
            alpha = 0.14
            avg_wind_hub_ms = avg_wind_ms * (hub_height_m / reference_height_m) ** alpha


            rated_speed_ms = 11.0
            rayleigh_correction = 1.9
            raw_factor = (avg_wind_hub_ms / rated_speed_ms) ** 3 * rayleigh_correction
            capacity_factor = max(0.02, min(raw_factor, 0.40))

            return {
                "avg_radiation_kwh_m2_day": round(avg_radiation_kwh, 3),
                "avg_wind_speed_ms": round(avg_wind_ms, 2),
                "avg_wind_speed_hub_ms": round(avg_wind_hub_ms, 2),
                "avg_capacity_factor": round(capacity_factor, 3),
                "days_covered": len(daily.get("time", [])),
            }
        except (requests.RequestException, KeyError, ValueError) as e:
            raise ConnectionError(f"Could not fetch historical weather data: {e}") from e
