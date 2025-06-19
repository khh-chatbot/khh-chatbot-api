# test_util/test_api.py

import requests
import json
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8080')

# 🔽 이 부분을 실제 도메인으로 변경했습니다!
BASE_URL = API_BASE_URL


def test_basic_apis():
    """기본 API 테스트"""
    print(f"=== 기본 API 테스트 (대상: {BASE_URL}) ===")

    # 서버 상태 확인
    try:
        response = requests.get(f'{BASE_URL}/')
        if response.status_code == 200:
            print("✅ 서버 상태: 정상")
            print(f"📝 응답: {response.json()['message']}")
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

    # 날씨 API
    print("\n--- 날씨 API ---")
    try:
        response = requests.get(f'{BASE_URL}/api/weather')
        result = response.json()
        if result['success']:
            print("✅ 날씨 API 성공")
            print(f"📄 날씨 정보: {result['data'][:100]}...")
        else:
            print(f"❌ 날씨 API 실패: {result.get('error')}")
    except Exception as e:
        print(f"❌ 날씨 API 오류: {e}")

    # 통합 학식 API (중앙대)
    print("\n--- 통합 학식 API (중앙대) ---")
    try:
        response = requests.get(f'{BASE_URL}/api/meal?university=cau&type=중식')
        result = response.json()
        if result['success']:
            print("✅ 중앙대 학식 API 성공")
            print(f"📄 학식 정보: {result['data'][:100]}...")
        else:
            print(f"❌ 중앙대 학식 API 실패: {result.get('error')}")
    except Exception as e:
        print(f"❌ 중앙대 학식 API 오류: {e}")

    return True


def test_message_api():
    """메시지 API 테스트"""
    print("\n=== 메시지 API 테스트 ===")

    try:
        test_case = {"message": "크하학", "sender": "도메인테스터", "room": "라이브방"}
        response = requests.post(
            f'{BASE_URL}/api/message',
            json=test_case,
            headers={'Content-Type': 'application/json'}
        )
        result = response.json()

        if result['success']:
            print(f"✅ 메시지 API 성공: {result['data'].get('response')}")
        else:
            print(f"❌ 메시지 API 실패: {result.get('error')}")
    except Exception as e:
        print(f"❌ 메시지 API 오류: {e}")


# --- (이하 다른 테스트 함수들은 동일합니다) ---

def test_all():
    """모든 테스트 실행"""
    print(f"🧪 === 크하학 API 전체 테스트 시작 (대상: {BASE_URL}) ===\n")
    if not test_basic_apis():
        print("❌ 서버 연결 실패로 테스트 중단")
        return
    test_message_api()
    # 필요하다면 다른 테스트 함수들도 여기에 추가
    print("\n🎉 === 도메인 기반 테스트 완료 ===")


if __name__ == '__main__':
    test_all()
