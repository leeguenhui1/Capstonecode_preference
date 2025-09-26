"""
공통 유틸리티 함수 모음.
날짜 파싱 등 보조 기능 제공.
"""

import re
from datetime import datetime, timedelta


def parse_natural_date(text, base_date=None):
    """
    '이번 주말', '내일', '모레', '다음주 토요일' 등 자연어 날짜를 yyyy-mm-dd로 변환
    base_date: 기준 날짜 (기본값: 오늘)
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
        return (base_date + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    m = re.search(r"다음주\s*([월화수목금토일])", text)
    if m:
        target_weekday = weekday_map[m.group(1)]
        days_ahead = 7 - base_date.weekday() + target_weekday
        return (base_date + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    m = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if m:
        return m.group(0)
    if "오늘" in text:
        return base_date.strftime("%Y-%m-%d")
    return base_date.strftime("%Y-%m-%d")
