"""
JSON 파일을 기반으로 위치 및 전화번호 데이터를 불러오고 처리하는 서비스입니다.
"""
import os
import json
from typing import List, Dict

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

PARKS_JSON_PATH = os.path.join(DATA_DIR, '도시공원정보현황(제공표준).json')
RESTAURANTS_JSON_PATH = os.path.join(DATA_DIR, '모범음식점현황.json')

def load_json_data(file_path: str, name_key: str, lat_key: str, lng_key: str, tel_key: str) -> List[Dict]:
    """
    JSON 파일을 불러와 'tel' 키를 포함한 표준 형식으로 파싱하는 공통 함수입니다.
    """
    if not os.path.exists(file_path):
        print(f"오류: 다음 경로에 파일이 없습니다: {file_path}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        processed_data = []
        for item in data:
            lat_val = item.get(lat_key)
            lng_val = item.get(lng_key)

            if all(k in item for k in [name_key, lat_key, lng_key]) and lat_val and lng_val:
                try:
                    # 'tel' 필드를 표준 형식에 추가합니다.
                    processed_data.append({
                        'name': item[name_key],
                        'lat': float(lat_val),
                        'lng': float(lng_val),
                        'tel': item.get(tel_key, '정보 없음') # 전화번호가 없으면 '정보 없음'으로 처리합니다.
                    })
                except (ValueError, TypeError):
                    # 위도, 경도 값을 숫자로 변환할 수 없으면 해당 데이터를 건너뜁니다.
                    continue
                    
        return processed_data
        
    except Exception as e:
        print(f"JSON 파일 처리 중 오류 발생 {file_path}: {e}")
        return []

def load_parks_data() -> List[Dict]:
    """도시공원 JSON 파일에서 데이터를 읽어옵니다."""
    # 공원 파일에 맞는 전화번호 키('MNGINST_TELNO')를 지정합니다.
    return load_json_data(
        PARKS_JSON_PATH, 
        name_key='PARK_NM', 
        lat_key='REFINE_WGS84_LAT', 
        lng_key='REFINE_WGS84_LOGT',
        tel_key='MNGINST_TELNO'
    )

def load_restaurants_data() -> List[Dict]:
    """모범음식점 JSON 파일에서 데이터를 읽어옵니다."""
    # 음식점 파일에 맞는 전화번호 키('TELNO')를 지정합니다.
    return load_json_data(
        RESTAURANTS_JSON_PATH, 
        name_key='BIZEST_NM', 
        lat_key='REFINE_WGS84_LAT', 
        lng_key='REFINE_WGS84_LOGT',
        tel_key='TELNO'
    )