def check_admin_message(msg, sender, bot_state):
    """관리자 명령어 체크 (박정욱만 가능)"""

    if sender != "박정욱":
        return None

    if msg == "크하학 종료":
        bot_state['isActive'] = False
        return "봇이 비활성화됐다. '크하학 시작'으로 다시 켤 수 있다."

    if msg == "크하학 시작":
        bot_state['isActive'] = True
        return "봇이 다시 활성화됐다!"

    if msg == "봇 상태":
        return f"현재 봇 상태: {'활성화' if bot_state['isActive'] else '비활성화'}"

    return None
