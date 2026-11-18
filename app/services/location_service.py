import math
import time

import requests

from app.config import request_timeout


class LocationNotFound(ValueError):
    pass


class LocationServiceUnavailable(ConnectionError):
    pass


class LocationService:

    nominatim_search_url = "https://nominatim.openstreetmap.org/search"
    nominatim_reverse_url = "https://nominatim.openstreetmap.org/reverse"
    open_meteo_geocode_url = "https://geocoding-api.open-meteo.com/v1/search"

    user_agent = (
        "SmartEnergyComparison/1.0 (Ashesi University student project; "
        "contact: your-email@ashesi.edu.gh)"
    )

    min_seconds_between_calls = 1.1
    _last_call_time = 0.0
    _cache = {}

    earth_radius_km = 6371.0

    ghana_bounds = {"lat_min": 4.5, "lat_max": 11.2,
                    "lon_min": -3.3, "lon_max": 1.3}


    @classmethod
    def _respect_rate_limit(cls):
        elapsed = time.time() - cls._last_call_time
        if elapsed < cls.min_seconds_between_calls:
            time.sleep(cls.min_seconds_between_calls - elapsed)
        cls._last_call_time = time.time()

    @classmethod
    def _nominatim_get(cls, url: str, params: dict):
        cls._respect_rate_limit()
        try:
            response = requests.get(
                url,
                params=params,
                headers={"User-Agent": cls.user_agent,
                         "Accept-Language": "en"},
                timeout=request_timeout,
            )
            response.raise_for_status()
            return response.json(), True
        except (requests.RequestException, ValueError):


            return None, False


    @classmethod
    def geocode(cls, location_text: str, country_code: str = "gh") -> dict:
        if not location_text or not str(location_text).strip():
            raise ValueError("Location cannot be empty")

        text = str(location_text).strip()

        coords = cls._try_parse_coordinates(text)
        if coords:
            return cls.reverse_geocode(*coords)

        cache_key = f"fwd:{text.lower()}:{country_code}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        reachable = False

        result, nominatim_up = cls._geocode_nominatim(text, country_code)
        reachable = reachable or nominatim_up

        if not result:
            result, open_meteo_up = cls._geocode_open_meteo(text)
            reachable = reachable or open_meteo_up

        if result:
            cls._cache[cache_key] = result
            return result


        if reachable:
            raise LocationNotFound(
                f"No place called {location_text!r} was found. "
                f"Check the spelling, or try a nearby town."
            )
        raise LocationServiceUnavailable(
            "Could not reach the location service. Check your internet "
            "connection and try again."
        )

    @classmethod
    def _geocode_nominatim(cls, text: str, country_code: str):
        params = {
            "q": text,
            "format": "json",
            "limit": 5,
            "addressdetails": 1,
        }
        if country_code:
            params["countrycodes"] = country_code

        data, reachable = cls._nominatim_get(cls.nominatim_search_url, params)


        if reachable and not data and country_code:
            params.pop("countrycodes")
            data, reachable = cls._nominatim_get(cls.nominatim_search_url, params)


        if not data or not isinstance(data, list):
            return None, reachable

        match = data[0]
        if not isinstance(match, dict) or "lat" not in match or "lon" not in match:
            return None, reachable
        address = match.get("address", {})
        if not isinstance(address, dict):
            address = {}

        return {
            "place_name": cls._short_name(match, address),
            "display_name": match.get("display_name", ""),
            "region": address.get("state", address.get("region", "")),
            "country": address.get("country", ""),
            "latitude": float(match["lat"]),
            "longitude": float(match["lon"]),
            "place_type": match.get("type", ""),
            "method": "nominatim",
            "exists": True,
            "in_ghana": cls.is_in_ghana(float(match["lat"]), float(match["lon"])),
        }, True

    @classmethod
    def _geocode_open_meteo(cls, text: str):
        try:
            response = requests.get(
                cls.open_meteo_geocode_url,
                params={"name": text, "count": 5, "language": "en",
                        "format": "json"},
                timeout=request_timeout,
            )
            response.raise_for_status()
            payload = response.json()


            if not isinstance(payload, dict):
                return None, False
            results = payload.get("results") or []
        except (requests.RequestException, ValueError):
            return None, False

        if not results:


            return None, True

        match = next((r for r in results if r.get("country_code") == "GH"),
                     results[0])
        return {
            "place_name": match["name"],
            "display_name": ", ".join(
                p for p in [match.get("name"), match.get("admin1"),
                            match.get("country")] if p
            ),
            "region": match.get("admin1", ""),
            "country": match.get("country", ""),
            "latitude": float(match["latitude"]),
            "longitude": float(match["longitude"]),
            "place_type": "town",
            "method": "open-meteo",
            "exists": True,
            "in_ghana": match.get("country_code") == "GH",
        }, True

    @classmethod
    def reverse_geocode(cls, latitude: float, longitude: float) -> dict:
        latitude = float(latitude)
        longitude = float(longitude)

        cache_key = f"rev:{round(latitude, 4)}:{round(longitude, 4)}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        result, reachable = cls._reverse_nominatim(latitude, longitude)

        if result:
            cls._cache[cache_key] = result
            return result

        if not reachable:
            raise LocationServiceUnavailable(
                "Could not reach the location service. Check your "
                "internet connection and try again."
            )
        raise LocationNotFound(
            f"No known place at {latitude:.4f}, {longitude:.4f}."
        )

    @classmethod
    def _reverse_nominatim(cls, latitude: float, longitude: float):
        data, reachable = cls._nominatim_get(cls.nominatim_reverse_url, {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "zoom": 14,
            "addressdetails": 1,
        })


        if not isinstance(data, dict) or "error" in data:
            return None, reachable

        address = data.get("address", {})
        if not isinstance(address, dict):
            address = {}
        return {
            "place_name": cls._short_name(data, address),
            "display_name": data.get("display_name", ""),
            "region": address.get("state", ""),
            "country": address.get("country", ""),
            "latitude": latitude,
            "longitude": longitude,
            "place_type": data.get("type", ""),
            "method": "nominatim_reverse",
            "exists": True,
            "distance_km": 0.0,
            "in_ghana": cls.is_in_ghana(latitude, longitude),
        }, True

    @staticmethod
    def _short_name(match: dict, address: dict) -> str:
        for key in ("amenity", "building", "shop", "office",
                    "village", "town", "suburb", "city", "municipality",
                    "county", "state_district", "state"):
            if address.get(key):
                return address[key]
        display = match.get("display_name", "")
        return display.split(",")[0] if display else "Unknown location"

    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = (math.sin(dphi / 2) ** 2
             + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
        return LocationService.earth_radius_km * 2 * math.atan2(
            math.sqrt(a), math.sqrt(1 - a))

    @staticmethod
    def _try_parse_coordinates(text: str):
        if "," not in text:
            return None
        parts = [p.strip() for p in text.split(",")]
        if len(parts) != 2:
            return None
        try:
            lat, lon = float(parts[0]), float(parts[1])
        except ValueError:
            return None
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return (lat, lon)
        return None

    @staticmethod
    def is_in_ghana(latitude: float, longitude: float) -> bool:
        b = LocationService.ghana_bounds
        return (b["lat_min"] <= latitude <= b["lat_max"]
                and b["lon_min"] <= longitude <= b["lon_max"])

    @classmethod
    def validate(cls, location_text: str) -> dict:
        if not location_text or not str(location_text).strip():
            return {"valid": False, "reason": "empty",
                    "message": "Enter a town or area name",
                    "location": None}

        try:
            location = cls.geocode(location_text)
        except LocationNotFound as e:
            return {"valid": False, "reason": "not_found",
                    "message": str(e), "location": None}
        except LocationServiceUnavailable as e:
            return {"valid": False, "reason": "unavailable",
                    "message": str(e), "location": None}

        if not location["in_ghana"]:
            return {
                "valid": True, "reason": "found",
                "message": (f"Found {location['place_name']}, but it is outside "
                            f"Ghana. Tariff and emission figures assume "
                            f"Ghanaian supply."),
                "location": location,
            }

        return {"valid": True, "reason": "found",
                "message": f"Found {location['display_name']}",
                "location": location}

    @classmethod
    def resolve_manual_location(cls, location_text: str) -> dict:
        return cls.geocode(location_text)

    @classmethod
    def resolve_coordinates(cls, latitude: float, longitude: float) -> dict:
        return cls.reverse_geocode(latitude, longitude)

    @classmethod
    def resolve(cls, place_name=None, latitude=None, longitude=None) -> dict:
        if latitude is not None and longitude is not None:
            return cls.reverse_geocode(float(latitude), float(longitude))
        if place_name:
            return cls.geocode(place_name)
        result = cls.reverse_geocode(5.6037, -0.1870)
        result["method"] = "default"
        return result
