"""
날씨 정보 및 예보 API 함수를 제공합니다.
Open-Meteo API를 사용하여 실시간/미래 날씨 데이터를 조회합니다.
"""
import requests
from collections import Counter
from constants.constants import seoul_keywords, gyeonggi_keywords, weather_map, global_lat_lon

def get_weather_forecast(location, date):
    lat_lon = global_lat_lon.get(location)
    if not lat_lon:
        if any(k in location for k in seoul_keywords):
            lat_lon, location = global_lat_lon.get("서울"), "서울"
        elif any(k in location for k in gyeonggi_keywords):
            lat_lon, location = global_lat_lon.get("경기도"), "경기도"
        else:
            return f"[{location}의 위치 정보를 찾을 수 없습니다.]"
    
    lat, lon = lat_lon
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,weathercode&timezone=Asia%2FSeoul&start_date={date}&end_date={date}"
    response = requests.get(url)
    data = response.json()

    if "hourly" not in data:
        return f"[{date} {location}의 날씨 예보 데이터를 찾을 수 없습니다.]"
    
    temps = data["hourly"]["temperature_2m"]
    codes = data["hourly"]["weathercode"]
    max_temp = max(temps) if temps else None
    main_code = Counter(codes).most_common(1)[0][0] if codes else None
    
    return {
        "date": date,
        "location": location,
        "max_temperature": max_temp,
        "weather": weather_map.get(main_code, "정보 없음"),
    }

def get_celsius_temperature(location):
    lat_lon = global_lat_lon.get(location)
    if not lat_lon:
        if any(k in location for k in seoul_keywords):
            lat_lon, location = global_lat_lon.get("서울"), "서울"
        elif any(k in location for k in gyeonggi_keywords):
            lat_lon, location = global_lat_lon.get("경기도"), "경기도"
        else:
            return None
            
    lat, lon = lat_lon
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    data = response.json()["current_weather"]
    
    return {
        "temperature": data["temperature"],
        "weather": weather_map.get(data.get("weathercode"), "정보 없음"),
    }
