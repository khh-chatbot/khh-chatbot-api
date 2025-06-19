import json
import os
from datetime import datetime, timedelta


def message_memory(message, room, sender):
    """메모리 기능 메인 함수"""
    if "!기억" in message:
        return message_remem(message, room)
    if "뭐였" in message:
        return message_remem_return(room)
    if "뭐더라" in message:
        return message_mem_return(sender)
    if "!삭제" in message:
        return message_delete(message, room, sender)
    if "!리마인드" in message:
        return message_remind(message, room, sender)
    if "내일" in message or "오늘" in message:
        return check_reminders()
    return None


def message_remem(message, room):
    """방별 메모 저장"""
    # "!기억해" 또는 "!기억" 제거
    message = message.replace("!기억해", "").replace("!기억", "").strip()

    if len(message) != 0:
        # rem.json 파일에서 기존 데이터 로드
        if os.path.isfile("rem.json"):
            with open("rem.json", "r", encoding="utf-8") as f:
                rem_dict = json.load(f)
        else:
            rem_dict = {}

        # 방별로 메모 저장
        rem_dict[room] = message

        # JSON 파일에 저장
        json_data = json.dumps(rem_dict, ensure_ascii=False, indent=4)
        with open("rem.json", "w", encoding="utf-8") as f:
            f.write(json_data)

        return f"'{message}' 기억했다"

    return None


def message_mem_return(sender):
    """개인별 메모 조회"""
    if os.path.isfile("mem.json"):
        with open("mem.json", "r", encoding="utf-8") as f:
            mem_dict = json.load(f)
        if sender in mem_dict:
            return f"{mem_dict[sender]}\\m^^7"
    return "기억나는 게 없다"


def message_remem_return(room):
    """방별 메모 조회"""
    if os.path.isfile("rem.json"):
        with open("rem.json", "r", encoding="utf-8") as f:
            rem_dict = json.load(f)
        if room in rem_dict:
            return f"{rem_dict[room]}\\m아마 이거일 듯?"
    return "이 방에서 기억한 게 없다"


def message_delete(message, room, sender):
    """메모 삭제 기능"""
    # !삭제 방별 또는 !삭제 개인
    message = message.replace("!삭제", "").strip()

    if message == "방별" or message == "":
        # 방별 메모 삭제
        if os.path.isfile("rem.json"):
            with open("rem.json", "r", encoding="utf-8") as f:
                rem_dict = json.load(f)

            if room in rem_dict:
                deleted_content = rem_dict[room]
                del rem_dict[room]

                json_data = json.dumps(rem_dict, ensure_ascii=False, indent=4)
                with open("rem.json", "w", encoding="utf-8") as f:
                    f.write(json_data)

                return f"'{deleted_content}' 삭제했다"
            else:
                return "이 방에서 기억한 게 없다"
        else:
            return "이 방에서 기억한 게 없다"

    elif message == "개인":
        # 개인별 메모 삭제
        if os.path.isfile("mem.json"):
            with open("mem.json", "r", encoding="utf-8") as f:
                mem_dict = json.load(f)

            if sender in mem_dict:
                deleted_content = mem_dict[sender]
                del mem_dict[sender]

                json_data = json.dumps(mem_dict, ensure_ascii=False, indent=4)
                with open("mem.json", "w", encoding="utf-8") as f:
                    f.write(json_data)

                return f"개인 메모 '{deleted_content}' 삭제했다"
            else:
                return "개인 메모가 없다"
        else:
            return "개인 메모가 없다"

    else:
        return "사용법: !삭제 방별 또는 !삭제 개인"


def message_remind(message, room, sender):
    """리마인드 기능"""
    # !리마인드 내일 14:30 회의 또는 !리마인드 오늘 18:00 저녁약속
    content = message.replace("!리마인드", "").strip()

    if len(content) == 0:
        return "사용법: !리마인드 내일 14:30 회의내용 또는 !리마인드 오늘 18:00 약속내용"

    try:
        parts = content.split(" ", 2)
        if len(parts) < 3:
            return "사용법: !리마인드 내일 14:30 회의내용 또는 !리마인드 오늘 18:00 약속내용"

        day_str = parts[0]  # 내일, 오늘
        time_str = parts[1]  # 14:30
        reminder_content = parts[2]  # 회의내용

        # 날짜 계산
        if day_str == "내일":
            target_date = datetime.now() + timedelta(days=1)
        elif day_str == "오늘":
            target_date = datetime.now()
        else:
            return "날짜는 '오늘' 또는 '내일'만 가능하다"

        # 시간 파싱
        if ":" not in time_str:
            return "시간 형식: 14:30 또는 18:00"

        hour, minute = time_str.split(":")
        hour = int(hour)
        minute = int(minute)

        if not (0 <= hour <= 23) or not (0 <= minute <= 59):
            return "올바른 시간을 입력해라 (00:00 ~ 23:59)"

        # 리마인드 날짜시간 생성
        remind_datetime = target_date.replace(
            hour=hour, minute=minute, second=0, microsecond=0)

        # 과거 시간 체크
        if remind_datetime <= datetime.now():
            return "과거 시간으로는 리마인드를 설정할 수 없다"

        # 리마인드 저장
        if os.path.isfile("reminders.json"):
            with open("reminders.json", "r", encoding="utf-8") as f:
                reminders = json.load(f)
        else:
            reminders = []

        reminder = {
            "datetime": remind_datetime.isoformat(),
            "content": reminder_content,
            "room": room,
            "sender": sender,
            "created_at": datetime.now().isoformat()
        }

        reminders.append(reminder)

        json_data = json.dumps(reminders, ensure_ascii=False, indent=4)
        with open("reminders.json", "w", encoding="utf-8") as f:
            f.write(json_data)

        formatted_time = remind_datetime.strftime("%m월 %d일 %H:%M")
        return f"'{reminder_content}' 리마인드를 {formatted_time}에 설정했다"

    except ValueError:
        return "시간 형식이 잘못됐다. 예: 14:30"
    except Exception as e:
        return f"리마인드 설정 중 오류: {str(e)}"


def check_reminders():
    """현재 시간의 리마인드 체크"""
    if not os.path.isfile("reminders.json"):
        return None

    try:
        with open("reminders.json", "r", encoding="utf-8") as f:
            reminders = json.load(f)

        current_time = datetime.now()
        triggered_reminders = []
        remaining_reminders = []

        for reminder in reminders:
            remind_time = datetime.fromisoformat(reminder["datetime"])

            # 현재 시간이 리마인드 시간을 지났는지 체크 (5분 이내)
            time_diff = (current_time - remind_time).total_seconds()

            if 0 <= time_diff <= 300:  # 0~5분 이내
                triggered_reminders.append(reminder)
            elif time_diff < 0:  # 아직 시간이 안 됨
                remaining_reminders.append(reminder)
            # time_diff > 300이면 이미 지난 리마인드 (삭제)

        # 남은 리마인드만 저장
        if len(remaining_reminders) != len(reminders):
            json_data = json.dumps(remaining_reminders,
                                   ensure_ascii=False, indent=4)
            with open("reminders.json", "w", encoding="utf-8") as f:
                f.write(json_data)

        # 실행할 리마인드가 있으면 반환
        if triggered_reminders:
            messages = []
            for reminder in triggered_reminders:
                formatted_time = datetime.fromisoformat(
                    reminder["datetime"]).strftime("%H:%M")
                messages.append(
                    f"⏰ {formatted_time} 리마인드: {reminder['content']}")

            return "\n".join(messages)

    except Exception as e:
        return f"리마인드 체크 중 오류: {str(e)}"

    return None


def get_all_reminders(room=None):
    """모든 리마인드 조회 (선택적으로 방별)"""
    if not os.path.isfile("reminders.json"):
        return "설정된 리마인드가 없다"

    try:
        with open("reminders.json", "r", encoding="utf-8") as f:
            reminders = json.load(f)

        if room:
            reminders = [r for r in reminders if r.get("room") == room]

        if not reminders:
            return "설정된 리마인드가 없다"

        result = "📋 설정된 리마인드 목록:\n"
        for i, reminder in enumerate(reminders, 1):
            remind_time = datetime.fromisoformat(reminder["datetime"])
            formatted_time = remind_time.strftime("%m월 %d일 %H:%M")
            result += f"{i}. {formatted_time} - {reminder['content']}\n"

        return result

    except Exception as e:
        return f"리마인드 조회 중 오류: {str(e)}"


def save_personal_memory(sender, content):
    """개인 메모 저장 (확장 기능)"""
    if os.path.isfile("mem.json"):
        with open("mem.json", "r", encoding="utf-8") as f:
            mem_dict = json.load(f)
    else:
        mem_dict = {}

    mem_dict[sender] = content

    json_data = json.dumps(mem_dict, ensure_ascii=False, indent=4)
    with open("mem.json", "w", encoding="utf-8") as f:
        f.write(json_data)


def get_all_room_memories():
    """모든 방 메모리 조회 (디버그용)"""
    if os.path.isfile("rem.json"):
        with open("rem.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_all_personal_memories():
    """모든 개인 메모리 조회 (디버그용)"""
    if os.path.isfile("mem.json"):
        with open("mem.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def clear_room_memory(room):
    """특정 방 메모리 삭제"""
    if os.path.isfile("rem.json"):
        with open("rem.json", "r", encoding="utf-8") as f:
            rem_dict = json.load(f)

        if room in rem_dict:
            del rem_dict[room]

            json_data = json.dumps(rem_dict, ensure_ascii=False, indent=4)
            with open("rem.json", "w", encoding="utf-8") as f:
                f.write(json_data)
            return True
    return False


def clear_personal_memory(sender):
    """특정 개인 메모리 삭제"""
    if os.path.isfile("mem.json"):
        with open("mem.json", "r", encoding="utf-8") as f:
            mem_dict = json.load(f)

        if sender in mem_dict:
            del mem_dict[sender]

            json_data = json.dumps(mem_dict, ensure_ascii=False, indent=4)
            with open("mem.json", "w", encoding="utf-8") as f:
                f.write(json_data)
            return True
    return False


# 테스트 함수
def test_memory_functions():
    """메모리 기능 테스트"""
    print("=== 메모리 기능 테스트 ===")

    # 방별 메모 테스트
    print("\n--- 방별 메모 테스트 ---")
    result1 = message_memory("!기억 점심약속 2시", "테스트방", "사용자1")
    print(f"저장: {result1}")

    result2 = message_memory("뭐였지?", "테스트방", "사용자2")
    print(f"조회: {result2}")

    # 삭제 테스트
    print("\n--- 삭제 테스트 ---")
    result3 = message_memory("!삭제 방별", "테스트방", "사용자1")
    print(f"삭제: {result3}")

    # 리마인드 테스트
    print("\n--- 리마인드 테스트 ---")
    result4 = message_memory("!리마인드 내일 14:30 회의 있음", "테스트방", "사용자1")
    print(f"리마인드: {result4}")


if __name__ == "__main__":
    test_memory_functions()
