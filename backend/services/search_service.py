"""
인터넷 검색 API 함수를 제공합니다.
Tavily API를 사용하여 실시간 정보를 검색합니다.
"""
import requests
from config import TAVILY_API_KEY

def search_internet(search_query):
    url = "https://api.tavily.com/search"
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    data = {"query": search_query, "include_answer": True}
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get("answer", "검색 결과를 찾을 수 없습니다.")
    except Exception as e:
        print(f"Tavily API error: {e}")
        return "[인터넷 검색 중 오류가 발생했습니다]"