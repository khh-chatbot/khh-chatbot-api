from modules.cau_meal import CAUMealAPI
from modules.postech_meal import get_postech_meal
from modules.weather import get_weather_api
from modules.message_handler import MessageHandler  # 추가
from modules.memory import message_memory, get_all_reminders, check_reminders  # 추가
from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
import logging
from datetime import datetime
import os


# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.StreamHandler(sys.stdout),  # 콘솔 출력
#         logging.FileHandler('app.log')     # 파일 저장
#     ]
# )

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# 서비스 인스턴스
cau_service = CAUMealAPI()
message_handler = MessageHandler()  # 추가

# 접속 로그를 위한 미들웨어


@app.before_request
def log_request_info():
    """모든 요청에 대한 로그 기록"""
    client_ip = request.environ.get(
        'HTTP_X_FORWARDED_FOR', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    log_message = f"🌐 접속: {client_ip} → {request.method} {request.path} | User-Agent: {user_agent}"
    app.logger.info(log_message)
    print(f"[{timestamp}] {log_message}")


@app.route('/')
def home():
    client_ip = request.environ.get(
        'HTTP_X_FORWARDED_FOR', request.remote_addr)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"🎉 [{timestamp}] 홈페이지 접속! IP: {client_ip}")
    app.logger.info(f"홈페이지 접속 - IP: {client_ip}")

    return jsonify({
        "message": "크하학 API 서버가 작동 중입니다! 🎉",
        "status": "running",
        "access_time": timestamp,
        "client_ip": client_ip,
        "success": "접속 성공!"
    })


@app.route('/api/weather', methods=['GET'])
def weather():
    try:
        result = get_weather_api()
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/postech/meal', methods=['GET'])
def postech_meal():
    meal_type = request.args.get('type', None)  # 점심, 저녁, 전체
    try:
        result = get_postech_meal(meal_type)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/cau/meal', methods=['GET'])
def cau_meal():
    campus = request.args.get('campus', '서울')
    meal_type = request.args.get('type', '중식')
    try:
        result = cau_service.get_meal_data(campus=campus, meal_type=meal_type)
        formatted = cau_service.format_meal_output(result)
        return jsonify({"success": True, "data": formatted})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 통합 학식 API 추가
@app.route('/api/meal', methods=['GET'])
def unified_meal():
    """통합 학식 API - 대학 구분해서 제공"""
    university = request.args.get('university', 'postech')  # postech 또는 cau
    meal_type = request.args.get('type', None)
    campus = request.args.get('campus', '서울')  # CAU용

    try:
        if university.lower() == 'cau' or university.lower() == '중앙대':
            # 중앙대 학식
            result = cau_service.get_meal_data(
                campus=campus, meal_type=meal_type or '중식')
            formatted = cau_service.format_meal_output(result)
            return jsonify({
                "success": True,
                "data": formatted,
                "university": "중앙대학교",
                "campus": campus
            })
        else:
            # 포항공대 학식 (기본값)
            result = get_postech_meal(meal_type)
            return jsonify({
                "success": True,
                "data": result,
                "university": "포항공과대학교"
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 메시지 처리 엔드포인트 추가
@app.route('/api/message', methods=['POST'])
def process_message():
    """메시지 처리 API"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "JSON 데이터가 필요하다"})

        msg = data.get('message', '').strip()
        sender = data.get('sender', '익명')
        room = data.get('room', '기본방')

        if not msg:
            return jsonify({"success": False, "error": "메시지가 비어있다"})

        # 먼저 메모리 기능 체크
        memory_response = message_memory(msg, room, sender)
        if memory_response:
            return jsonify({
                "success": True,
                "data": {
                    "response": memory_response,
                    "type": "memory",
                    "sender": sender,
                    "room": room,
                    "original_message": msg
                }
            })

        # 메모리 기능이 없으면 일반 메시지 처리
        response = message_handler.process_message(msg, sender, room)

        if response:
            return jsonify({
                "success": True,
                "data": {
                    "response": response,
                    "type": "message",
                    "sender": sender,
                    "room": room,
                    "original_message": msg
                }
            })
        else:
            return jsonify({
                "success": True,
                "data": {
                    "response": None,
                    "message": "처리할 수 없는 메시지다"
                }
            })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 봇 상태 확인 엔드포인트 추가
@app.route('/api/bot/status', methods=['GET'])
def bot_status():
    """봇 상태 확인"""
    try:
        status = {
            "isActive": message_handler.bot_state['isActive'],
            "ailaCount": message_handler.bot_state['ailaCount'],
            "yoshiCount": message_handler.bot_state['yoshiCount']
        }
        return jsonify({"success": True, "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 봇 제어 엔드포인트 추가 (관리자용)
@app.route('/api/bot/control', methods=['POST'])
def bot_control():
    """봇 제어 (활성화/비활성화)"""
    try:
        data = request.get_json()
        action = data.get('action')
        sender = data.get('sender', '')

        # 박정욱만 제어 가능
        if sender != "박정욱":
            return jsonify({"success": False, "error": "권한이 없다"})

        if action == "activate":
            message_handler.bot_state['isActive'] = True
            return jsonify({"success": True, "data": "봇이 활성화됐다"})
        elif action == "deactivate":
            message_handler.bot_state['isActive'] = False
            return jsonify({"success": True, "data": "봇이 비활성화됐다"})
        else:
            return jsonify({"success": False, "error": "잘못된 액션이다"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 🔥 새로 추가된 API 엔드포인트들

# 리마인드 조회 API
@app.route('/api/reminders', methods=['GET'])
def get_reminders_api():
    """설정된 리마인드 조회"""
    try:
        room = request.args.get('room', None)
        result = get_all_reminders(room)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 리마인드 체크 API (주기적으로 호출)
@app.route('/api/reminders/check', methods=['GET'])
def check_reminders_api():
    """현재 실행할 리마인드 체크"""
    try:
        result = check_reminders()
        if result:
            return jsonify({"success": True, "data": result, "hasReminders": True})
        else:
            return jsonify({"success": True, "data": "실행할 리마인드가 없다", "hasReminders": False})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 메모리 관리 API
@app.route('/api/memory/list', methods=['GET'])
def list_memories():
    """저장된 메모리 조회"""
    try:
        from modules.memory import get_all_room_memories, get_all_personal_memories

        room_memories = get_all_room_memories()
        personal_memories = get_all_personal_memories()

        return jsonify({
            "success": True,
            "data": {
                "room_memories": room_memories,
                "personal_memories": personal_memories
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 🔥 리마인드 스케줄러 관련 API
@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    """리마인드 스케줄러 시작"""
    try:
        from modules.scheduler import start_reminder_scheduler

        data = request.get_json() or {}
        callback_url = data.get('callback_url')

        scheduler = start_reminder_scheduler(callback_url)
        return jsonify({"success": True, "message": "리마인드 스케줄러가 시작됐다"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """리마인드 스케줄러 정지"""
    try:
        from modules.scheduler import stop_reminder_scheduler

        stop_reminder_scheduler()
        return jsonify({"success": True, "message": "리마인드 스케줄러가 정지됐다"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/scheduler/status', methods=['GET'])
def scheduler_status():
    """스케줄러 상태 확인"""
    try:
        from modules.scheduler import get_scheduler_status

        status = get_scheduler_status()
        return jsonify({"success": True, "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 웹훅 엔드포인트 (리마인드 알림 수신용)
@app.route('/api/webhook/reminder', methods=['POST'])
def webhook_reminder():
    """리마인드 웹훅 수신"""
    try:
        data = request.get_json()

        if data and data.get('type') == 'reminder':
            message = data.get('message', '')
            timestamp = data.get('timestamp', '')

            print(f"🔔 리마인드 알림 수신: {message}")

            # 여기서 실제 카카오톡 메시지 전송 로직을 추가할 수 있다
            # 예: 특정 방에 메시지 전송

            return jsonify({"success": True, "message": "리마인드 알림을 받았다"})
        else:
            return jsonify({"success": False, "error": "잘못된 웹훅 데이터다"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 🔥 접속 테스트용 새 엔드포인트 추가
@app.route('/test')
def test_connection():
    """접속 테스트용 간단한 페이지"""
    client_ip = request.environ.get(
        'HTTP_X_FORWARDED_FOR', request.remote_addr)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"🧪 [{timestamp}] 테스트 페이지 접속! IP: {client_ip}")

    return f"""
    <html>
    <head><title>크하학 서버 접속 테스트</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>🎉 접속 성공!</h1>
        <p><strong>접속 시간:</strong> {timestamp}</p>
        <p><strong>접속 IP:</strong> {client_ip}</p>
        <p><strong>서버 상태:</strong> 정상 작동 중</p>
        <hr>
        <h2>API 테스트</h2>
        <ul>
            <li><a href="/api/weather">날씨 정보</a></li>
            <li><a href="/api/postech/meal">포항공대 학식</a></li>
            <li><a href="/api/cau/meal">중앙대 학식</a></li>
            <li><a href="/api/bot/status">봇 상태</a></li>
        </ul>
    </body>
    </html>
    """


if __name__ == '__main__':
    # 서버 시작 시 자동으로 스케줄러 시작
    try:
        from modules.scheduler import start_reminder_scheduler
        print("⏰ 자동으로 리마인드 스케줄러를 시작한다...")
        start_reminder_scheduler("http://localhost:8080/api/webhook/reminder")
    except Exception as e:
        print(f"❌ 스케줄러 시작 실패: {e}")

    print("🚀 크하학 API 서버를 시작한다...")
    print("📝 모든 접속과 요청이 로그로 기록된다.")
    app.run(host='0.0.0.0', port=8080, debug=False)
