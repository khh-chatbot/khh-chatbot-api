import random


def check_meme_message(msg):
    """밈 응답 체크"""

    if "아.." in msg:
        return random.choice(["글쿤..", "그래요..", "그렇군요..", "안돼..", "..메리카노"])

    elif "안사요" in msg or "안 사요" in msg or "사지말까" in msg:
        return random.choice(["이걸 안 사?", "왜요;;", "그거 사면 진짜 좋을텐데..", "아..", "헐.."])

    elif "응애" in msg:
        return random.choice(["귀여운척 하지 마세요;;", "응애 나 애기", "응애 나 아기 코린이"])

    elif "불편" in msg:
        return "불편해?\n불편하면 자세를 고쳐앉아!\n보는 자세가 불편하니깐 그런거아냐!!"

    elif "사고싶" in msg or "사야" in msg or "살까" in msg or "샀어" in msg:
        return random.choice(["축하합니다!!!", "그걸 샀네;;", "개부자;;", "와 샀네", "이걸 산다고?"])

    elif "뭐먹" in msg or "머먹" in msg:
        foods = ["돼지갈비!!", "황금볶음밥!!", "미역국!!",
                 "닭갈비!!", "떡볶이!!", "돈까스!!", "치킨!!", "라면!!"]
        return random.choice(foods)

    elif "배고파" in msg or "배고프" in msg:
        return random.choice(["돼지", "또 먹어?", "살쪄", "그만 먹어;;", "아까 먹었잖아"])

    elif "졸려" in msg or "잠와" in msg or "피곤해" in msg:
        return random.choice(["자라;;", "구라;;", "자야지;;", "자야겠다;;", "그만 좀 자라;;"])

    elif "멈춰" in msg:
        return "멈춰!!"

    elif "자라" in msg:
        return random.choice(["전기세 아깝다ㅡㅡ;;", "거북이", "잘 자라^^", "자라는 토끼랑 달리기 경주 중"])

    return None
