import requests
from datetime import datetime, timedelta
import json


class CAUMealAPI:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://mportal.cau.ac.kr"

        # 브라우저 헤더 설정
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Content-Type': 'application/json;charset=UTF-8',
            'Referer': 'https://mportal.cau.ac.kr/main.do',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.session.headers.update(self.headers)

        # 캠퍼스 코드
        self.campus = {
            '서울': '1',
            '안성': '2'
        }

        # 식사 시간 코드
        self.meal_time = {
            '조식': '10',
            '중식': '20',
            '석식': '40'
        }

    def get_meal_data(self, campus='서울', meal_type='중식', date_offset=0, debug=False):
        """
        학식 데이터 가져오기

        Args:
            campus: '서울' 또는 '안성'
            meal_type: '조식', '중식', '석식'
            date_offset: 0(오늘), -1(어제), 1(내일), ...
            debug: True면 상세 디버그 정보 출력
        """
        try:
            # API 엔드포인트
            api_url = f"{self.base_url}/portlet/p005/p005.ajax"

            # 요청 파라미터 (JavaScript의 vm.searchInfo와 동일)
            params = {
                'tabs': self.campus.get(campus, '1'),      # 캠퍼스
                'tabs2': self.meal_time.get(meal_type, '20'),  # 식사시간
                'daily': date_offset                        # 날짜 오프셋
            }

            print(f"API 요청: {api_url}")
            print(f"파라미터: {params}")

            # POST 요청 (JavaScript에서 $http.post 사용)
            response = self.session.post(api_url, json=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                print(f"응답 성공: {len(data.get('list', []))}개 항목")

                # 디버그 모드면 실제 응답 구조 출력
                if debug:
                    print("\n=== 디버그: 실제 응답 데이터 ===")
                    print(f"전체 응답 키: {list(data.keys())}")
                    print(f"isEmpty: {data.get('isEmpty')}")

                    if 'list' in data and data['list']:
                        print(f"첫 번째 항목: {data['list'][0]}")
                        print(f"첫 번째 항목 키들: {list(data['list'][0].keys())}")

                        # 각 항목의 상세 내용 확인
                        for i, item in enumerate(data['list'][:3]):  # 처음 3개만
                            print(f"\n--- 항목 {i+1} ---")
                            for key, value in item.items():
                                print(f"{key}: {value}")

                    print("=== 디버그 종료 ===\n")

                return self.parse_meal_response(data, campus, meal_type, date_offset, debug)
            else:
                print(f"API 응답 오류: {response.status_code}")
                print(f"응답 내용: {response.text}")
                return None

        except Exception as e:
            print(f"API 호출 오류: {e}")
            return None

    def parse_meal_response(self, data, campus, meal_type, date_offset, debug=False):
        """API 응답 데이터 파싱"""
        try:
            # 날짜 계산
            target_date = datetime.now() + timedelta(days=date_offset)
            day_names = ['월', '화', '수', '목', '금', '토', '일']

            meal_data = {
                'date': target_date.strftime('%Y-%m-%d'),
                'day': day_names[target_date.weekday()],
                'campus': campus,
                'meal_type': meal_type,
                'restaurants': [],
                # 'N'이면 False, 'Y'이면 True
                'isEmpty': data.get('isEmpty') == 'Y'
            }

            # 식당별 메뉴 정보 처리
            meal_list = data.get('list', [])

            if not meal_list:
                print("메뉴 데이터가 비어있다")
                return meal_data

            # 식당별로 그룹화 (course별로도 분류)
            restaurants = {}

            for item in meal_list:
                if debug:
                    print(f"\n처리 중인 항목: {item}")

                # 식당명과 코스 정보
                rest_name = (item.get('rest') or
                             item.get('restName') or
                             item.get('restaurant') or
                             item.get('cafeteria') or
                             '식당명 없음')

                course = item.get('course', '')
                price = item.get('price', '')
                time = item.get('time', '')

                menu_detail = (item.get('menuDetail') or
                               item.get('menu') or
                               item.get('menuInfo') or
                               item.get('food') or '')

                if debug:
                    print(f"식당명: {rest_name}")
                    print(f"코스: {course}")
                    print(f"메뉴 상세: {menu_detail}")
                    print(f"가격: {price}")
                    print(f"시간: {time}")

                # 식당별 그룹화를 위한 키 생성
                if rest_name not in restaurants:
                    restaurants[rest_name] = {
                        'name': rest_name,
                        'courses': []
                    }

                # JavaScript의 getRowData 함수와 동일한 로직
                parsed_menu = self.get_row_data(menu_detail)
                if debug:
                    print(f"파싱된 메뉴: {parsed_menu}")

                if parsed_menu:
                    # 코스별로 메뉴 정리
                    course_info = {
                        'course': course,
                        'price': price,
                        'time': time,
                        'menus': parsed_menu
                    }
                    restaurants[rest_name]['courses'].append(course_info)

            # 결과 정리
            meal_data['restaurants'] = list(restaurants.values())

            if debug:
                print(f"\n최종 식당 수: {len(meal_data['restaurants'])}")
                for rest in meal_data['restaurants']:
                    total_menus = sum(len(course['menus'])
                                      for course in rest['courses'])
                    print(
                        f"- {rest['name']}: {len(rest['courses'])}개 코스, {total_menus}개 메뉴")

            return meal_data

        except Exception as e:
            print(f"응답 파싱 오류: {e}")
            return None

    def get_row_data(self, input_data):
        """
        JavaScript의 getRowData 함수를 Python으로 구현
        쉼표로 구분된 문자열을 파싱하여 메뉴 리스트 반환
        """
        if not input_data:
            return []

        # None이나 빈 문자열 체크
        if input_data is None or str(input_data).strip() == '':
            return []

        input_str = str(input_data).strip()

        if ',' in input_str:
            # 쉼표로 분리
            menu_items = input_str.split(',')
            result = [item.strip() for item in menu_items if item.strip()]
            return result
        else:
            # 단일 메뉴
            return [input_str] if input_str else []

    def get_all_meals_today(self, campus='서울'):
        """오늘의 모든 식사 정보 가져오기"""
        return self.get_all_meals_today_with_offset(campus=campus, date_offset=0)

    def get_all_meals_today_with_offset(self, campus='서울', date_offset=0):
        """특정 날짜의 모든 식사 정보 가져오기"""
        target_date = datetime.now() + timedelta(days=date_offset)

        all_meals = {
            'date': target_date.strftime('%Y-%m-%d'),
            'campus': campus,
            'meals': {}
        }

        meal_types = ['조식', '중식', '석식']

        for meal_type in meal_types:
            print(f"\n=== {meal_type} 정보 가져오는 중 ===")
            meal_data = self.get_meal_data(
                campus=campus, meal_type=meal_type, date_offset=date_offset)

            if meal_data and not meal_data.get('isEmpty', True):
                all_meals['meals'][meal_type] = meal_data
            else:
                print(f"{meal_type} 정보 없음")

        return all_meals

    def format_meal_output(self, meal_data):
        """메뉴 데이터를 읽기 좋게 포맷팅"""
        if not meal_data:
            return "학식 정보를 가져올 수 없다"

        if isinstance(meal_data, dict) and 'meals' in meal_data:
            # 전체 식사 정보 포맷팅
            output = f"📍 중앙대학교 {meal_data['campus']}캠퍼스 {meal_data['date']} 학식:\n\n"

            meal_icons = {'조식': '🌅', '중식': '🍱', '석식': '🌙'}

            for meal_type, data in meal_data['meals'].items():
                icon = meal_icons.get(meal_type, '🍽️')
                output += f"{icon} {meal_type}:\n"

                if data.get('isEmpty', True):
                    output += "  메뉴 정보 없음\n\n"
                    continue

                for restaurant in data.get('restaurants', []):
                    output += f"  🏪 {restaurant['name']}:\n"

                    # 코스별로 정리
                    if 'courses' in restaurant:
                        for course in restaurant['courses']:
                            course_name = course.get('course', '')
                            price = course.get('price', '')
                            time = course.get('time', '')

                            # 코스 정보 출력
                            course_info = f"    📋 {course_name}"
                            if price:
                                course_info += f" ({price})"
                            if time:
                                course_info += f" [{time}]"
                            output += course_info + "\n"

                            # 메뉴 출력
                            for menu in course.get('menus', []):
                                output += f"      • {menu}\n"

                    # 기존 방식 호환 (courses가 없는 경우)
                    elif 'menus' in restaurant and restaurant['menus']:
                        for menu in restaurant['menus']:
                            output += f"    • {menu}\n"
                    else:
                        output += "    • 메뉴 정보 없음\n"
                    output += "\n"

            return output

        else:
            # 단일 식사 정보 포맷팅
            meal_icons = {'조식': '🌅', '중식': '🍱', '석식': '🌙'}
            icon = meal_icons.get(meal_data.get('meal_type', ''), '🍽️')

            output = f"📍 중앙대학교 {meal_data['campus']}캠퍼스 {meal_data['date']}({meal_data['day']}) {icon} {meal_data['meal_type']}:\n\n"

            if meal_data.get('isEmpty', True):
                output += "메뉴 정보가 없다\n"
                return output

            for restaurant in meal_data.get('restaurants', []):
                output += f"🏪 {restaurant['name']}:\n"

                # 코스별로 정리
                if 'courses' in restaurant:
                    for course in restaurant['courses']:
                        course_name = course.get('course', '')
                        price = course.get('price', '')
                        time = course.get('time', '')

                        # 코스 정보 출력
                        course_info = f"  📋 {course_name}"
                        if price:
                            course_info += f" ({price})"
                        if time:
                            course_info += f" [{time}]"
                        output += course_info + "\n"

                        # 메뉴 출력
                        for menu in course.get('menus', []):
                            output += f"    • {menu}\n"

                # 기존 방식 호환 (courses가 없는 경우)
                elif 'menus' in restaurant and restaurant['menus']:
                    for menu in restaurant['menus']:
                        output += f"  • {menu}\n"
                else:
                    output += "  • 메뉴 정보 없음\n"
                output += "\n"

            return output

    def save_to_json(self, meal_data, filename=None):
        """JSON 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cau_meal_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(meal_data, f, ensure_ascii=False, indent=2)

        print(f"데이터가 {filename}에 저장됐다")


def main():
    """메인 실행 함수 - 오늘 학식만 조회"""
    api = CAUMealAPI()

    print("📍 중앙대학교 서울캠퍼스 오늘 학식 정보")
    print("=" * 50)

    # 오늘 조식
    print("\n🌅 조식:")
    breakfast = api.get_meal_data(campus='서울', meal_type='조식', date_offset=0)
    if breakfast and not breakfast.get('isEmpty', True):
        for restaurant in breakfast.get('restaurants', []):
            print(f"🏪 {restaurant['name']}")
            if 'courses' in restaurant:
                for course in restaurant['courses']:
                    print(
                        f"  📋 {course.get('course', '')} ({course.get('price', '')}) [{course.get('time', '')}]")
                    for menu in course.get('menus', []):
                        print(f"    • {menu}")
            print()
    else:
        print("  조식 정보가 없다\n")

    # 오늘 중식
    print("🍱 중식:")
    lunch = api.get_meal_data(campus='서울', meal_type='중식', date_offset=0)
    if lunch and not lunch.get('isEmpty', True):
        for restaurant in lunch.get('restaurants', []):
            print(f"🏪 {restaurant['name']}")
            if 'courses' in restaurant:
                for course in restaurant['courses']:
                    print(
                        f"  📋 {course.get('course', '')} ({course.get('price', '')}) [{course.get('time', '')}]")
                    for menu in course.get('menus', []):
                        print(f"    • {menu}")
            print()
    else:
        print("  중식 정보가 없다\n")

    # 오늘 석식
    print("🌙 석식:")
    dinner = api.get_meal_data(campus='서울', meal_type='석식', date_offset=0)
    if dinner and not dinner.get('isEmpty', True):
        for restaurant in dinner.get('restaurants', []):
            print(f"🏪 {restaurant['name']}")
            if 'courses' in restaurant:
                for course in restaurant['courses']:
                    print(
                        f"  📋 {course.get('course', '')} ({course.get('price', '')}) [{course.get('time', '')}]")
                    for menu in course.get('menus', []):
                        print(f"    • {menu}")
            print()
    else:
        print("  석식 정보가 없다\n")

    return {'breakfast': breakfast, 'lunch': lunch, 'dinner': dinner}


def get_all_meals_today_with_offset(self, campus='서울', date_offset=0):
    """특정 날짜의 모든 식사 정보 가져오기"""
    target_date = datetime.now() + timedelta(days=date_offset)

    all_meals = {
        'date': target_date.strftime('%Y-%m-%d'),
        'campus': campus,
        'meals': {}
    }

    meal_types = ['조식', '중식', '석식']

    for meal_type in meal_types:
        print(f"\n=== {meal_type} 정보 가져오는 중 ===")
        meal_data = self.get_meal_data(
            campus=campus, meal_type=meal_type, date_offset=date_offset)

        if meal_data and not meal_data.get('isEmpty', True):
            all_meals['meals'][meal_type] = meal_data
        else:
            print(f"{meal_type} 정보 없음")

    return all_meals


# 메소드를 클래스에 추가
CAUMealAPI.get_all_meals_today_with_offset = get_all_meals_today_with_offset

# 개별 함수들


def get_today_lunch(campus='서울'):
    """오늘 점심 메뉴만 간단히 조회"""
    api = CAUMealAPI()
    return api.get_meal_data(campus=campus, meal_type='중식')


def get_today_dinner(campus='서울'):
    """오늘 저녁 메뉴만 간단히 조회"""
    api = CAUMealAPI()
    return api.get_meal_data(campus=campus, meal_type='석식')


if __name__ == "__main__":
    main()
