"""
날씨 정보 및 예보 API 함수 제공.
실시간/미래 날씨 데이터 조회 기능 담당.
"""

import requests
from constants import seoul_keywords, gyeonggi_keywords, weather_map
from common import global_lat_lon
from collections import Counter


def get_weather_forecast(location, date):
    """
    지정한 지역(location)과 날짜(date)에 대해 Open-Meteo API를 호출하여
    해당 날짜의 최고기온과 대표 날씨 상태를 반환합니다.
    지역명이 없으면 서울/경기로 자동 대체
    """
    lat_lon = global_lat_lon.get(location, None)
    if lat_lon is None:
        if any(k in location for k in seoul_keywords):
            lat_lon = global_lat_lon.get("서울")
            location = "서울"
        elif any(k in location for k in gyeonggi_keywords):
            lat_lon = global_lat_lon.get("경기도")
            location = "경기도"
        else:
            return f"[{location}의 위치 정보를 찾을 수 없습니다.]"
    lat, lon = lat_lon
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,weathercode&timezone=Asia%2FSeoul&start_date={date}&end_date={date}"
    response = requests.get(url)
    data = response.json()
    if "hourly" not in data:
        return f"[{date} {location}의 날씨 예보 데이터를 찾을 수 없습니다. 날짜가 과거이거나 예보가 제공되지 않는 경우일 수 있습니다.]"
    temps = data["hourly"]["temperature_2m"]
    codes = data["hourly"]["weathercode"]
    max_temp = max(temps) if temps else None
    code_counter = Counter(codes)
    main_code = code_counter.most_common(1)[0][0] if codes else None
    weather_status = weather_map.get(main_code, "정보 없음")
    return {
        "date": date,
        "location": location,
        "max_temperature": max_temp,
        "weather": weather_status,
    }


def get_celsius_temperature(location):
    """
    지정한 지역(location)의 현재 기온과 날씨 상태를 Open-Meteo API로 조회하여 반환합니다.
    지역명이 없으면 서울/경기로 자동 대체
    """
    lat_lon = global_lat_lon.get(location, None)
    if lat_lon is None:
        if any(k in location for k in seoul_keywords):
            lat_lon = global_lat_lon.get("서울")
            location = "서울"
        elif any(k in location for k in gyeonggi_keywords):
            lat_lon = global_lat_lon.get("경기도")
            location = "경기도"
        else:
            return None
    lat, lon = lat_lon
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    data = response.json()
    temperature = data["current_weather"]["temperature"]
    weather_code = data["current_weather"].get("weathercode", None)
    weather_status = weather_map.get(weather_code, "정보 없음")
    return {"temperature": temperature, "weather": weather_status}
