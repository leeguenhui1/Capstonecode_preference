"""
자연어 형태의 날짜 텍스트를 파싱하는 유틸리티 함수를 제공합니다.
"""
import re
from datetime import datetime, timedelta

def parse_natural_date(text, base_date=None):
    """
    '이번 주말', '내일' 등 자연어 날짜를 'YYYY-MM-DD' 형식으로 변환합니다.
    """
    if base_date is None:
        base_date = datetime.now()
    text = text.strip()
    weekday_map = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}

    if "내일" in text:
        return (base_date + timedelta(days=1)).strftime("%Y-%m-%d")
    if "모레" in text:
        return (base_date + timedelta(days=2)).strftime("%Y-%m-%d")
    if "이번 주말" in text or "주말" in text:
        days_ahead = 5 - base_date.weekday()
        if days_ahead < 0:
            days_ahead += 7
        return (base_date + timedelta(days_ahead)).strftime("%Y-%m-%d")
    
    m = re.search(r"다음주\s*([월화수목금토일])", text)
    if m:
        target_weekday = weekday_map[m.group(1)]
        days_ahead = 7 - base_date.weekday() + target_weekday
        return (base_date + timedelta(days_ahead)).strftime("%Y-%m-%d")
    
    m = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if m:
        return m.group(0)
        
    if "오늘" in text:
        return base_date.strftime("%Y-%m-%d")
        
    return base_date.strftime("%Y-%m-%d")