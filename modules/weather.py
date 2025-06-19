import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from urllib.parse import quote
import ssl
import urllib3
import os
from dotenv import load_dotenv

load_dotenv()


# SSL 검증 완전 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 레거시 SSL 지원을 위한 어댑터


class SSLAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)


def get_rain_type(code):
    """강수형태 코드를 문자열로 변환"""
    rain_types = {
        "0": "없음",
        "1": "비",
        "2": "비/눈",
        "3": "눈",
        "5": "빗방울",
        "6": "빗방울/눈날림",
        "7": "눈날림"
    }
    return rain_types.get(code, "알 수 없음")


async def parse_weather_xml(xml_data):
    """날씨 XML 데이터 파싱"""
    try:
        root = ET.fromstring(xml_data)

        # items/item 경로 찾기
        items = root.findall(".//item")

        data = {}

        for item in items:
            category_elem = item.find("category")
            value_elem = item.find("obsrValue")

            if category_elem is not None and value_elem is not None:
                category = category_elem.text
                value = value_elem.text

                if category == "T1H":  # 기온
                    data["temp"] = f"{value}℃"
                elif category == "PTY":  # 강수형태
                    data["rainType"] = get_rain_type(value)
                elif category == "REH":  # 습도
                    data["humidity"] = f"{value}%"
                elif category == "WSD":  # 풍속
                    data["wind"] = f"{value}m/s"

        result = (
            f"🌡️ 기온: {data.get('temp', '-')}\n"
            f"💧 습도: {data.get('humidity', '-')}\n"
            f"🌬️ 풍속: {data.get('wind', '-')}\n"
            f"☔ 강수: {data.get('rainType', '-')}"
        )

        return result

    except ET.ParseError as e:
        return f"❌ XML 파싱 실패: {str(e)}"
    except Exception as e:
        return f"❌ 파싱 중 오류: {str(e)}"


def parse_weather_xml_sync(xml_data):
    """동기 버전의 XML 파싱 함수"""
    try:
        root = ET.fromstring(xml_data)

        # items/item 경로 찾기
        items = root.findall(".//item")

        data = {}

        for item in items:
            category_elem = item.find("category")
            value_elem = item.find("obsrValue")

            if category_elem is not None and value_elem is not None:
                category = category_elem.text
                value = value_elem.text

                if category == "T1H":  # 기온
                    data["temp"] = f"{value}℃"
                elif category == "PTY":  # 강수형태
                    data["rainType"] = get_rain_type(value)
                elif category == "REH":  # 습도
                    data["humidity"] = f"{value}%"
                elif category == "WSD":  # 풍속
                    data["wind"] = f"{value}m/s"

        result = (
            f"🌡️ 기온: {data.get('temp', '-')}\n"
            f"💧 습도: {data.get('humidity', '-')}\n"
            f"🌬️ 풍속: {data.get('wind', '-')}\n"
            f"☔ 강수: {data.get('rainType', '-')}"
        )

        return result

    except ET.ParseError as e:
        return f"❌ XML 파싱 실패: {str(e)}"
    except Exception as e:
        return f"❌ 파싱 중 오류: {str(e)}"


def get_weather_fallback(base_date, current_hour):
    """데이터가 없을 때 1시간 전 데이터로 재시도"""
    fallback_hour = current_hour - 1

    # 0시인 경우 전날 23시로 설정
    if fallback_hour < 0:
        fallback_hour = 23
        yesterday = datetime.now() - timedelta(days=1)
        base_date = yesterday.strftime("%Y%m%d")

    base_time = f"{fallback_hour:02d}00"
    print(f"📅 재시도 - 기준 날짜: {base_date}, 기준 시간: {base_time}")

    service_key = os.getenv('WEATHER_API_KEY')
    url = f"https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst?serviceKey={quote(service_key)}&pageNo=1&numOfRows=1000&dataType=XML&base_date={base_date}&base_time={base_time}&nx=102&ny=94"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        weather_info = parse_weather_xml_sync(response.text)
        print(f"🌤️ 포항 날씨 ({fallback_hour}시 기준):\n{weather_info}")
        return weather_info

    except requests.exceptions.RequestException as e:
        error_msg = f"❌ 재시도도 실패: {str(e)}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ 재시도 중 오류: {str(e)}"
        print(error_msg)
        return error_msg


def get_weather():
    """포항 날씨 정보 가져오기"""
    now = datetime.now()
    base_date = now.strftime("%Y%m%d")
    current_hour = now.hour
    base_time = f"{current_hour:02d}00"

    print(f"🕐 현재 시간: {now.hour}시 {now.minute}분")
    print(f"📅 기준 날짜: {base_date}, 기준 시간: {base_time}")

    service_key = os.getenv('WEATHER_API_KEY')
    url = f"https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst?serviceKey={quote(service_key)}&pageNo=1&numOfRows=1000&dataType=XML&base_date={base_date}&base_time={base_time}&nx=102&ny=94"

    # 강화된 SSL 설정을 위한 세션
    session = requests.Session()
    session.mount('https://', SSLAdapter())
    session.verify = False
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/xml, text/xml, */*',
        'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    })

    response = None
    try:
        response = session.get(url, timeout=15, allow_redirects=True)
        response.raise_for_status()

        weather_info = parse_weather_xml_sync(response.text)
        result_msg = f"🌤️ 포항 현재 날씨 ({current_hour}시 기준):\n{weather_info}"
        print(result_msg)
        return result_msg

    except requests.exceptions.SSLError as e:
        print(f"❌ SSL 에러: {str(e)}")
        # HTTP로 시도
        return try_http_fallback(base_date, base_time, current_hour)

    except requests.exceptions.RequestException as e:
        error_msg = f"❌ 날씨 조회 실패: {str(e)}"
        print(error_msg)

        # 데이터가 없을 경우 1시간 전 데이터로 재시도
        if "NO_DATA" in str(e) or (response and response.status_code == 200):
            print("🔄 1시간 전 데이터로 재시도...")
            return get_weather_fallback(base_date, current_hour)

        return error_msg

    except Exception as e:
        error_msg = f"❌ 날씨 조회 중 오류: {str(e)}"
        print(error_msg)
        return error_msg


def get_weather_and_reply_format():
    """카카오톡 봇용 포맷으로 날씨 정보 반환"""
    try:
        weather_result = get_weather()
        if "❌" in weather_result:
            return "날씨 정보를 가져올 수 없다."
        else:
            return f"{weather_result}\n"
    except Exception as e:
        return f"날씨 API 호출 중 오류가 발생했다. 그래도 러닝하러 가자! 🏃‍♂️\n에러: {str(e)}"


if __name__ == "__main__":
    # 테스트 실행
    get_weather()


def get_weather_api():
    """API용 날씨 정보 반환"""
    return get_weather_and_reply_format()
