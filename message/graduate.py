import datetime
import random


def check_graduate_message(msg):
    """졸업/전역/아카데미 관련 메시지 체크"""

    # 아카데미 마지막 체크 (우선순위 높음)
    if "아카데미" in msg:
        return calculate_academy_end()

    if "합숙" in msg:
        return calculate_ski_training()

    # "소해", "졸업", "전역" 키워드가 있을 때만 작동
    if not any(keyword in msg for keyword in ["소해", "졸업", "전역"]):
        return None

    # # 특정 인물 체크
    # if "우진" in msg:
    #     return calculate_wj_graduate()
    # elif "재희" in msg:
    #     return calculate_jh_graduate()

    return None


def calculate_ski_training():
    """합숙까지 계산 (JavaScript 로직과 동일)"""
    today = datetime.datetime.now()
    end_date = datetime.datetime(
        2026, 1, 5, 0, 0, 0)  # 2026년 1월 5일 0시 0분 0초
    diff_time = end_date - today

    # 전체 밀리초를 일수로 변환
    diff_days = int(diff_time.total_seconds() // (24 * 60 * 60))

    # 남은 시간 계산
    remaining_seconds = diff_time.total_seconds() % (24 * 60 * 60)
    diff_hours = int(remaining_seconds // (60 * 60))
    diff_minutes = int((remaining_seconds % (60 * 60)) // 60)

    if diff_time.total_seconds() > 0:
        if diff_days > 0:
            return f"용평 갈 때까지 {diff_days}일 {diff_hours}시간 {diff_minutes}분 남았다"
        else:
            return f"용평 갈 때까지 {diff_hours}시간 {diff_minutes}분 남았다"
    elif diff_time.total_seconds() > -86400:  # -24시간보다 크면 (오늘)
        return "합숙 시작함. 예린이 말 잘 들으셈."
    else:
        past_days = abs(diff_days)
        return f"합숙은 {past_days}일 전에 끝났다"


def calculate_academy_end():
    """아카데미 마지막까지 계산 (JavaScript 로직과 동일)"""
    today = datetime.datetime.now()
    end_date = datetime.datetime(
        2025, 12, 12, 0, 0, 0)  # 2025년 12월 12일 0시 0분 0초
    diff_time = end_date - today

    # 전체 밀리초를 일수로 변환
    diff_days = int(diff_time.total_seconds() // (24 * 60 * 60))

    # 남은 시간 계산
    remaining_seconds = diff_time.total_seconds() % (24 * 60 * 60)
    diff_hours = int(remaining_seconds // (60 * 60))
    diff_minutes = int((remaining_seconds % (60 * 60)) // 60)

    if diff_time.total_seconds() > 0:
        if diff_days > 0:
            return f"아카데미 마지막까지 {diff_days}일 {diff_hours}시간 {diff_minutes}분 남았다"
        else:
            return f"아카데미 마지막까지 {diff_hours}시간 {diff_minutes}분 남았다"
    elif diff_time.total_seconds() > -86400:  # -24시간보다 크면 (오늘)
        return "오늘이 아카데미 마지막날이다"
    else:
        past_days = abs(diff_days)
        return f"아카데미가 {past_days}일 전에 끝났다"


def calculate_wj_graduate():
    """서우진 전역 계산"""
    messages = [
        "우진이의 전문하사 지원을 응원한다!",
        f"전역까지는 {(datetime.date(2025, 12, 23)-datetime.date.today()).days:d}일 남음.",
        f"{(datetime.date(2025, 12, 23)-datetime.date.today()).days:d} \n {(datetime.date(2025, 12, 23)-datetime.date.today()).days:d} \n {(datetime.date(2025, 12, 23)-datetime.date.today()).days:d}",
    ]
    return random.choice(messages)


def calculate_jh_graduate():
    """재희 전역 계산"""
    return f"재희가 입대한지 {(datetime.date.today() - datetime.date(2025, 6, 9)).days:d}일 ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ"
