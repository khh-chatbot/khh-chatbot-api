// 갤럭시용 카카오톡 봇 - Flask API 연동 버전

const API_BASE_URL = CONFIG.API_BASE_URL || "http://localhost:8080";

// 상태 관리 객체 (간단하게)
let botState = {
    isActive: true,
    lastRequestTime: {},
};

function response(room, msg, sender, isGroupChat, replier) {
    // 요청 제한 (도배 방지)
    if (!checkRateLimit(sender)) {
        return;
    }

    // 봇 비활성화 상태면 관리자 명령어만 처리
    if (!botState.isActive) {
        if (sender === "박정욱") {
            if (msg === "크하학 시작") {
                botState.isActive = true;
                replier.reply("봇이 다시 활성화됐다!");
                return;
            }
        }
        return;
    }

    // Flask API로 메시지 전송
    try {
        const apiResponse = callFlaskAPI(msg, sender, room);
        
        if (apiResponse && apiResponse.success) {
            const responseData = apiResponse.data;
            
            if (responseData.response) {
                replier.reply(responseData.response);
            }
            
            // 관리자 명령어 처리
            if (responseData.type === "admin" && sender === "박정욱") {
                if (msg === "크하학 종료") {
                    botState.isActive = false;
                }
            }
        } else {
            // API 호출 실패시 기본 응답
            handleOfflineResponse(msg, sender, replier);
        }
    } catch (e) {
        // 네트워크 오류시 기본 응답
        handleOfflineResponse(msg, sender, replier);
    }
}

function callFlaskAPI(message, sender, room) {
    try {
        const payload = {
            message: message,
            sender: sender,
            room: room
        };

        // HTTP POST 요청
        const response = org.jsoup.Jsoup.connect(API_BASE_URL + "/api/message")
            .method(org.jsoup.Connection.Method.POST)
            .header("Content-Type", "application/json")
            .requestBody(JSON.stringify(payload))
            .timeout(5000) // 5초 타임아웃
            .ignoreContentType(true)
            .execute();

        if (response.statusCode() === 200) {
            return JSON.parse(response.body());
        } else {
            console.log("API 응답 오류: " + response.statusCode());
            return null;
        }
    } catch (e) {
        console.log("API 호출 실패: " + e.message);
        return null;
    }
}

function handleOfflineResponse(msg, sender, replier) {
    // API가 안될 때 기본 응답들
    const offlineResponses = {
        "크하학": "KHH",
        "KHH": "크하학",
        "안녕": "안녕하세요!",
        "학식": "서버 연결이 안 된다. 나중에 다시 시도해라.",
        "날씨": "서버 연결이 안 된다. 나중에 다시 시도해라.",
        "봇": "오프라인 모드로 작동 중이다."
    };

    // 친구 이름 기본 응답
    const friends = {
        "하리": "허리 조심해라",
        "김예준": "바보",
        "줄리엔": "많이 먹는다",
        "요시": "엄요시다"
    };

    // 기본 응답 체크
    if (offlineResponses[msg]) {
        replier.reply(offlineResponses[msg]);
        return;
    }

    // 친구 이름 체크
    for (let friend in friends) {
        if (msg.includes(friend)) {
            replier.reply(friends[friend]);
            return;
        }
    }

    // 감정 응답
    if (msg.includes("ㅠ") || msg.includes("ㅜ")) {
        replier.reply("왜 우냐");
        return;
    }

    if (msg.includes("ㅋ") && msg.length > 5) {
        replier.reply("뭘 웃어");
        return;
    }
}

function checkRateLimit(sender) {
    const now = Date.now();
    const lastTime = botState.lastRequestTime[sender] || 0;
    
    // 1초에 한 번만 처리
    if (now - lastTime < 1000) {
        return false;
    }
    
    botState.lastRequestTime[sender] = now;
    return true;
}

// 헬스체크용 함수
function checkAPIHealth() {
    try {
        const response = org.jsoup.Jsoup.connect(API_BASE_URL + "/")
            .timeout(3000)
            .ignoreContentType(true)
            .get();
        
        return response.statusCode() === 200;
    } catch (e) {
        return false;
    }
}