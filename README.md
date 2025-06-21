# khh-chatbot-API

와봇을 클론 코딩한 크하학봇입니다.

[와봇 링크](https://github.com/yymin1022/Wa_API)

**사람들을 행복하게 해주기 위해 만든 카카오톡 봇입니다.😊**  

카카오톡 봇용 Flask API 서버입니다. 학식 정보, 날씨 정보, 메모리 기능, 리마인드 등을 제공합니다.

## 주요 기능 ✨

### 🍱 학식 정보
- **포항공과대학교**: 아침, 점심, 저녁 메뉴
- **중앙대학교**: 서울/안성캠퍼스 조식, 중식, 석식

### 🌤️ 날씨 정보  
- **포항, 서울, 부산** 3개 지역 지원
- 기온, 습도, 풍속, 강수형태 제공

### 🧠 메모리 기능
- **방별 메모**: `!기억 내용` / `뭐였지?`
- **개인 메모**: 개인별 메모 저장/조회
- **메모 삭제**: `!삭제 방별` / `!삭제 개인`

### ⏰ 리마인드 기능
- **리마인드 설정**: `!리마인드 내일 14:30 회의`
- **자동 알림**: 설정된 시간에 자동 알림
- **리마인드 조회**: 설정된 리마인드 목록 확인

### 👥 친구 응답
- 특정 친구 이름 언급시 개별 응답
- 졸업/전역 카운트다운
- 감정 표현 반응 (웃음, 울음, 스트레스 등)

### 🎭 밈 응답
- 다양한 밈 문구 응답
- 상황별 재미있는 반응

## API 엔드포인트 📡

### 기본 정보
```
GET /                     # 서버 상태 확인
GET /test                 # 접속 테스트 페이지
```

### 학식 정보
```
GET /api/postech/meal     # 포항공대 학식
GET /api/cau/meal         # 중앙대 학식  
GET /api/meal             # 통합 학식 (university 파라미터로 구분)
```

### 날씨 정보
```
GET /api/weather          # 날씨 정보 (기본: 포항)
```

### 메시지 처리
```
POST /api/message         # 카카오톡 메시지 처리
```

### 봇 관리
```
GET /api/bot/status       # 봇 상태 확인
POST /api/bot/control     # 봇 제어 (관리자만)
```

### 리마인드
```
GET /api/reminders        # 리마인드 목록 조회
GET /api/reminders/check  # 현재 실행할 리마인드 체크
```

### 스케줄러
```
POST /api/scheduler/start  # 리마인드 스케줄러 시작
POST /api/scheduler/stop   # 리마인드 스케줄러 정지
GET /api/scheduler/status  # 스케줄러 상태 확인
```

## 설치 및 실행 🚀

### 1. 환경 설정
```bash
# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일 생성:
```env
WEATHER_API_KEY=your_weather_api_key_here
```

### 3. 서버 실행
```bash
# 개발 모드
python app.py

# 프로덕션 모드 (Gunicorn)
gunicorn -c gunicorn.conf.py app:app
```

## 카카오톡 봇 사용법 💬

### 학식 조회
```
학식          # 포항공대 학식
중학          # 중앙대 서울캠퍼스 (시간대별 자동)
다학          # 중앙대 안성캠퍼스 (시간대별 자동)
```

### 날씨 조회
```
날씨          # 포항 날씨
포항 날씨     # 포항 날씨
서울 날씨     # 서울 날씨  
부산 날씨     # 부산 날씨
```

### 메모리 기능
```
!기억 점심약속 2시     # 방별 메모 저장
뭐였지?              # 방별 메모 조회
!삭제 방별           # 방별 메모 삭제
!삭제 개인           # 개인 메모 삭제
```

### 리마인드 기능  
```
!리마인드 내일 14:30 회의    # 리마인드 설정
!리마인드 오늘 18:00 약속    # 오늘 리마인드 설정
```

### 특별 기능
```
크하학        # 봇 정체성 확인
친구별 응답        # 친구별 응답
```

## 프로젝트 구조 📁

```
├── app.py                    # 메인 Flask 애플리케이션
├── gunicorn.conf.py         # Gunicorn 설정
├── modules/                 # 핵심 모듈들
│   ├── weather.py           # 날씨 API (포항/서울/부산)
│   ├── postech_meal.py      # 포항공대 학식 API
│   ├── cau_meal.py          # 중앙대 학식 API
│   ├── memory.py            # 메모리 및 리마인드 기능
│   ├── message_handler.py   # 메시지 처리 핸들러
│   └── scheduler.py         # 리마인드 스케줄러
├── message/                 # 메시지 응답 모듈들
│   ├── friends.py           # 친구별 응답
│   ├── graduate.py          # 졸업/전역 관련
│   ├── cry_laugh_stress.py  # 감정 표현 응답
│   ├── meme.py             # 밈 응답
│   └── admin.py            # 관리자 명령어
├── response.js             # 카카오톡 봇 JavaScript 코드
└── README.md               # 이 파일
```

## 개발 참여 🤝

궁금한 점이나 개선 사항이 있으시면 **Pull Request**를 날려주세요!

### 기여 방법
1. 이 저장소를 Fork 합니다
2. 새로운 브랜치를 생성합니다 (`git checkout -b feature/새기능`)
3. 변경사항을 커밋합니다 (`git commit -am '새 기능 추가'`)
4. 브랜치에 Push 합니다 (`git push origin feature/새기능`)
5. Pull Request를 생성합니다

### 개발 가이드라인
- 새로운 기능은 `modules/` 또는 `message/` 디렉토리에 추가
- 에러 처리 및 로깅 포함
- 테스트 함수 작성 권장

## 라이선스 📄

이 프로젝트는 개인 프로젝트입니다.

## 문의 📞

궁금한 점이 있으시면 Issue를 생성하거나 Pull Request를 보내주세요!

---

Made with ❤️ by Jeje