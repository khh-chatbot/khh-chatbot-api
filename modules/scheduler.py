import schedule
import time
import threading
import requests
from datetime import datetime
from modules.memory import check_reminders


class ReminderScheduler:
    def __init__(self, callback_url=None):
        """
        리마인드 스케줄러 초기화

        Args:
            callback_url: 리마인드 알림을 보낼 콜백 URL (선택사항)
        """
        self.callback_url = callback_url
        self.is_running = False
        self.thread = None

    def start(self):
        """스케줄러 시작"""
        if self.is_running:
            print("⚠️  스케줄러가 이미 실행 중이다")
            return

        self.is_running = True

        # 매분마다 리마인드 체크
        schedule.every().minute.do(self._check_and_notify)

        # 백그라운드 스레드에서 실행
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()

        print("⏰ 리마인드 스케줄러가 시작됐다")

    def stop(self):
        """스케줄러 정지"""
        self.is_running = False
        schedule.clear()
        print("⏰ 리마인드 스케줄러가 정지됐다")

    def _run_scheduler(self):
        """스케줄러 메인 루프"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(1)  # 1초마다 체크
            except Exception as e:
                print(f"❌ 스케줄러 실행 중 오류: {e}")
                time.sleep(10)  # 오류 시 10초 대기

    def _check_and_notify(self):
        """리마인드 체크 및 알림 발송"""
        try:
            current_time = datetime.now()
            print(f"🔍 리마인드 체크 중... ({current_time.strftime('%H:%M:%S')})")

            reminder_message = check_reminders()

            if reminder_message:
                print(f"⏰ 리마인드 발견: {reminder_message}")

                # 콜백 URL이 있으면 웹훅으로 전송
                if self.callback_url:
                    self._send_webhook(reminder_message)

                # 로그에도 출력
                self._log_reminder(reminder_message)

        except Exception as e:
            print(f"❌ 리마인드 체크 중 오류: {e}")

    def _send_webhook(self, message):
        """웹훅으로 리마인드 전송"""
        try:
            payload = {
                "type": "reminder",
                "message": message,
                "timestamp": datetime.now().isoformat()
            }

            response = requests.post(
                self.callback_url,
                json=payload,
                timeout=5,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                print(f"✅ 웹훅 전송 성공")
            else:
                print(f"❌ 웹훅 전송 실패: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"❌ 웹훅 전송 오류: {e}")

    def _log_reminder(self, message):
        """리마인드를 로그 파일에 기록"""
        try:
            with open("reminder_log.txt", "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"❌ 로그 기록 오류: {e}")


# 전역 스케줄러 인스턴스
reminder_scheduler = None


def start_reminder_scheduler(callback_url=None):
    """리마인드 스케줄러 시작"""
    global reminder_scheduler

    if reminder_scheduler is None:
        reminder_scheduler = ReminderScheduler(callback_url)

    reminder_scheduler.start()
    return reminder_scheduler


def stop_reminder_scheduler():
    """리마인드 스케줄러 정지"""
    global reminder_scheduler

    if reminder_scheduler:
        reminder_scheduler.stop()


def get_scheduler_status():
    """스케줄러 상태 확인"""
    global reminder_scheduler

    if reminder_scheduler and reminder_scheduler.is_running:
        return {"status": "running", "message": "스케줄러가 실행 중이다"}
    else:
        return {"status": "stopped", "message": "스케줄러가 정지됐다"}


# 직접 실행 시 테스트
if __name__ == "__main__":
    print("🧪 리마인드 스케줄러 테스트 시작")

    # 테스트용 콜백 URL (실제로는 카카오톡 봇 서버 등)
    test_callback = "http://localhost:8080/api/webhook/reminder"

    # 스케줄러 시작
    scheduler = start_reminder_scheduler(test_callback)

    try:
        print("⏰ 스케줄러 실행 중... (Ctrl+C로 종료)")

        # 메인 스레드에서 대기
        while True:
            time.sleep(10)
            status = get_scheduler_status()
            print(f"📊 상태: {status['message']}")

    except KeyboardInterrupt:
        print("\n🛑 종료 요청 받음")
        stop_reminder_scheduler()
        print("✅ 스케줄러가 정지됐다")
