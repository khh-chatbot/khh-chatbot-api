import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple


class POSTECHMealService:
    """포항공대 학식 정보 서비스"""

    def __init__(self):
        self.api_base_url = "https://food.podac.poapper.com/v1/menus"
        self.fallback_url = "https://dining.postech.ac.kr/weekly-menu/"
        self.day_names = ["월", "화", "수", "목", "금", "토", "일"]
        self.meal_type_mapping = {
            "BREAKFAST_A": ("🌅", "조식 A"),
            "BREAKFAST_B": ("🥪", "조식 B"),
            "LUNCH": ("🍱", "점심"),
            "DINNER": ("🍽", "저녁"),
            "INTERNATIONAL": ("🌍", "국제관"),
            "STAFF": ("👨‍💼", "교직원"),
        }

    def _extract_korean_menu(self, text: str) -> str:
        """한국어 메뉴만 추출"""
        if not text or not text.strip():
            return ""

        # 영어 단어와 불필요한 문자 제거
        cleaned = re.sub(r'\b[A-Za-z]+\b', '', text)
        cleaned = re.sub(r'[^\w\s*가-힣]', ' ', cleaned)

        # 한글 부분만 추출
        korean_parts = re.findall(r'[가-힣*]+(?:\s+[가-힣*]+)*', cleaned)

        if korean_parts:
            result = ' '.join(korean_parts).strip()
            # 최소 2글자 이상의 의미있는 한국어만 반환
            if len(result) >= 2:
                return result

        return ""

    def _get_week_range(self, target_date: datetime = None) -> Tuple[datetime, datetime]:
        """이번 주 월요일~일요일 범위 계산"""
        if target_date is None:
            target_date = datetime.now()

        day_of_week = target_date.weekday()

        if day_of_week == 6:  # 일요일
            monday = target_date - timedelta(days=6)
        else:
            monday = target_date - timedelta(days=day_of_week)

        sunday = monday + timedelta(days=6)
        return monday, sunday

    def _format_date(self, date: datetime) -> str:
        """YYYYMMDD 형식으로 날짜 변환"""
        return date.strftime("%Y%m%d")

    def _determine_meal_type(self, meal_type: Optional[str], current_hour: int) -> str:
        """현재 시간에 따라 식사 타입 결정"""
        if meal_type:
            return meal_type
        if 6 <= current_hour < 10:
            return "아침"
        elif 11 <= current_hour < 15:
            return "점심"
        elif 17 <= current_hour < 20:
            return "저녁"
        else:
            return "전체"

    def _fetch_menu_data(self, start_date: str, end_date: str) -> List[Dict]:
        """API에서 메뉴 데이터 가져오기"""
        api_url = f"{self.api_base_url}/period/{start_date}/{end_date}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 호출 실패: {str(e)}")

    def _filter_today_menus(self, menu_data: List[Dict], today_date: str) -> List[Dict]:
        """오늘 날짜 메뉴만 필터링"""
        return [menu for menu in menu_data if str(menu.get('date')) == today_date]

    def _filter_by_meal_type(self, menus: List[Dict], meal_type: str) -> List[Dict]:
        """식사 타입별로 메뉴 필터링"""
        if meal_type == "아침":
            return [menu for menu in menus if menu.get('type') == "BREAKFAST_A" or menu.get('type') == "BREAKFAST_B"]
        elif meal_type == "점심":
            return [menu for menu in menus if menu.get('type') == "LUNCH"]
        elif meal_type == "저녁":
            return [menu for menu in menus if menu.get('type') == "DINNER"]
        else:
            return menus  # 전체

    def _extract_menu_items(self, food: Dict) -> List[str]:
        """음식 정보에서 한국어 메뉴 아이템 추출"""
        menu_items = []

        # name_kor에서 추출
        if food.get('name_kor'):
            kor_items = re.split(r'\s{2,}|\t', food['name_kor'])
            for item in kor_items:
                cleaned = self._extract_korean_menu(item)
                if cleaned and len(cleaned) > 1:
                    menu_items.append(cleaned)

        # name_eng에서도 한국어 메뉴 추출 (필드 변경 대비)
        if food.get('name_eng'):
            eng_items = re.split(r'\s{2,}|\t', food['name_eng'])
            for item in eng_items:
                cleaned = self._extract_korean_menu(item)
                if cleaned and len(cleaned) > 1 and cleaned not in menu_items:
                    menu_items.append(cleaned)

        return menu_items

    def _format_nutrition_info(self, menu: Dict) -> str:
        """영양 정보 포맷팅"""
        kcal = menu.get('kcal', 0)
        protein = menu.get('protein', 0)

        if kcal > 0 or protein > 0:
            return f"📊 {kcal}kcal, 단백질 {protein}g"
        return ""

    def _format_menu_text(self, filtered_menus: List[Dict], today_name: str, meal_type: str) -> str:
        """메뉴 텍스트 포맷팅"""
        # 헤더 생성
        if meal_type == "전체":
            menu_text = f"📍 포항공대 오늘({today_name})\n"
        elif meal_type == "점심":
            menu_text = f"📍 포항공대 오늘({today_name})\n"
        elif meal_type == "저녁":
            menu_text = f"📍 포항공대 오늘({today_name})\n"
        else:
            menu_text = f"📍 포항공대 오늘({today_name}) {meal_type}:"

        if not filtered_menus:
            menu_text += "오늘 메뉴를 찾을 수 없다.\n"
            menu_text += f"직접 확인: {self.fallback_url}"
            return menu_text

        # 메뉴 정보 추가
        for menu in filtered_menus:
            type_icon, type_name = self.meal_type_mapping.get(
                menu.get('type'), ("🍴", menu.get('type', '알 수 없음'))
            )
            menu_text += f"{type_icon} {type_name}:\n"

            # 음식 목록
            foods = menu.get('foods', [])
            if foods:
                for food in foods:
                    menu_items = self._extract_menu_items(food)
                    for menu_item in menu_items:
                        menu_text += f"  • {menu_item}\n"
            else:
                menu_text += "  • 메뉴 정보 없음\n"

            # 영양 정보
            nutrition_info = self._format_nutrition_info(menu)
            if nutrition_info:
                menu_text += f"{nutrition_info}"

        return menu_text

    def get_meal_info(self, meal_type: Optional[str] = None) -> str:
        """포항공대 학식 정보 메인 함수"""
        try:
            today = datetime.now()
            monday, sunday = self._get_week_range(today)

            start_date = self._format_date(monday)
            end_date = self._format_date(sunday)
            today_date = self._format_date(today)
            today_name = self.day_names[today.weekday()]

            # 식사 타입 결정
            meal_type = self._determine_meal_type(meal_type, today.hour)

            # API에서 데이터 가져오기
            menu_data = self._fetch_menu_data(start_date, end_date)

            # 오늘 메뉴 필터링
            today_menus = self._filter_today_menus(menu_data, today_date)

            # 식사 타입별 필터링
            filtered_menus = self._filter_by_meal_type(today_menus, meal_type)

            # 결과 텍스트 생성
            return self._format_menu_text(filtered_menus, today_name, meal_type)

        except Exception as e:
            error_msg = (
                f"학식 정보를 가져올 수 없다.\n"
                f"직접 확인: {self.fallback_url}\n"
                f"에러: {str(e)}"
            )
            return error_msg


def get_postech_meal(meal_type: Optional[str] = None) -> str:
    """포항공대 학식 정보 가져오기 (기존 함수명 호환)"""
    service = POSTECHMealService()
    return service.get_meal_info(meal_type)


def test_postech_meal():
    """테스트 함수"""
    service = POSTECHMealService()

    print("🧪 === 전체 메뉴 테스트 ===")
    print(service.get_meal_info("전체"))

    print("\n🧪 === 점심 메뉴 테스트 ===")
    print(service.get_meal_info("아침"))

    print("\n🧪 === 점심 메뉴 테스트 ===")
    print(service.get_meal_info("점심"))

    print("\n🧪 === 저녁 메뉴 테스트 ===")
    print(service.get_meal_info("저녁"))


if __name__ == "__main__":
    test_postech_meal()
