# Capstone
# main.py 실행 방법 ->  Vs code → cmd → 파일 위치로 이동 → uvicorn main:app —reload

달리진 파일 : 

일단 선호도 기능 구현에 있어, 
static/js/chatbotpage.js

chatbot_router.py
preference_reouter.py
chatbot_service.py
main.py
preference_schemas.py

2차적으로 ai 돌아가게 하려고 수정한 파일 ( 애초에 ai 작동이 안되었어서 , 선호도 와는 무관하게 수정한거 같음. )

api kes.env -> .env 로 이름 수정.
common/client.py
config.py

부수적으로 수정한 부분 (선호도 무관 ) 

user_router.py
