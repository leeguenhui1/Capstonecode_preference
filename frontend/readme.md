## 가상환경 설정 및 의존성 설치 방법

이 프로젝트는 python 기반의 Steamlit ui(애플리케이션) 입니다. 실행 전에 가상환경을 만들고 
필요한 패키지를 설치해주세요.

### Conda 환경 사용 시

1. Python 3.11 버전으로 가상환경 생성:
   ```bash
   conda create -n streamlit-app python=3.11

2. 가상환경 활성화

   conda activate steamlit-app

3. 패키지 설치
   pip install -r requirements.txt

### venv 사용 시 (Python 내장 가상환경)
   
1.  가상환경 생성:

    python -m venv venv

2.  가상환경 활성화 (Mac/Linux):

    source venv/bin/activate

3.  가상환경 활성화 (Windows):

    venv\Scripts\activate

4.  패키지 설치:


    pip install -r requirements.txt

# web page 실행.

 streamlit run pagename.py
