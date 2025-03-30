// CLI: k6 run --out json=result.json --insecure-skip-tls-verify scripts/k6/session.js
import http from "k6/http";
import { sleep, check } from "k6";

export let options = {
    // 가상 사용자
    vus: 50,
    // 테스트 시간
    duration: "30s",
    // 테스트 통과 기준
    thresholds: {
        // 응답 시간
        'http_req_duration': ['p(95)<500'],  // 95%의 요청이 500ms 이하로 응답
    },
};

// 테스트 시나리오
export default function () {
    // 세션 생성 요청
    let res = http.post("https://localhost/session/create");

    // 응답 코드 체크
    check(res, {
        "status is 201": (r) => r.status === 201,
    });

    // 대기
    sleep(1);
}
