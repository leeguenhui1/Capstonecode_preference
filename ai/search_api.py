"""
인터넷 검색(Tavily) API 함수 제공.
실시간 트렌드/정보 검색 기능 담당.
"""

import requests
import os


def search_internet(search_query):
    """
    Tavily API를 활용한 실시간 인터넷 검색 기능
    입력된 검색어(search_query)에 대해 결과를 반환
    예외: API 오류 발생 시 안내 메시지 반환
    """
    api_key = os.getenv("TAVILY_API_KEY")
    url = "https://api.tavily.com/search"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"query": search_query, "include_answer": True}
    try:
        response = requests.post(url, json=data, headers=headers)
        result = response.json()
        answer = result.get("answer", "")
        return answer
    except Exception:
        return "[인터넷 검색 중 오류가 발생했습니다]"
