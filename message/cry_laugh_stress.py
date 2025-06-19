import random


def check_cry_laugh_stress_message(msg):
    """감정 표현 체크"""
    if "ㅠ" in msg or "ㅜ" in msg:
        return check_cry(msg)
    elif "ㅋ" in msg or "ㅎ" in msg:
        return check_laugh(msg)
    elif ";" in msg:
        return check_stress(msg)
    return None


def check_cry(msg):
    """울음 체크"""
    messages = ["뭘 울어요;;", "왜 우시는 거예요?", "ㅋㅋ얘 운다"]
    if sum(msg.count(char) for char in "ㅠㅜ") >= 3:
        return random.choice(messages)
    return None


def check_laugh(msg):
    """웃음 체크"""
    messages = ["뭘 웃어요;;", "안웃긴데;;", "이게 웃겨요?"]
    if sum(msg.count(char) for char in "ㅋㄱㄲㄴㅌㅎ") >= 20:
        return random.choice(messages)
    return None


def check_stress(msg):
    """스트레스 체크"""
    if sum(msg.count(char) for char in ";:,.") >= 4:
        return "어림도 없지"
    return None
