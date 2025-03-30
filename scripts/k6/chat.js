// CLI: k6 run --out json=result.json --insecure-skip-tls-verify scripts/k6/session.js
import http from "k6/http";
import ws from "k6/ws";
import { check, sleep } from "k6";

export let options = {
    vus: 25,         // 각 VU가 한 쌍(2명)을 시뮬레이션 → 총 25쌍 = 50명
    duration: "30s", // 전체 테스트 30초 동안 진행
};

export default async function () {
    let startTime = Date.now();
    while (Date.now() - startTime < 30000) {
        // 1. 각 VU는 새로운 세션 생성 (REST API 호출)
        let res = http.post("https://localhost/session/create", null, {
            headers: { "Content-Type": "application/json" },
        });
        check(res, { "session created": (r) => r.status === 201 });
        let session_id = res.json().session_id;
        console.log(`VU ${__VU} created session: ${session_id}`);

        // 2. 생성된 세션 ID로 WebSocket URL 구성
        let url = `wss://localhost/chat/${session_id}`;

        // 3. 두 사용자를 동시에 시뮬레이션하기 위해 두 개의 WebSocket 연결을 Promise로 병렬 실행
        const user1Promise = new Promise((resolve, reject) => {
            ws.connect(url, {}, function (socket) {
                socket.on("open", function () {
                    console.log(`VU ${__VU} [User1] connected to session ${session_id}`);
                    // User1: 3초 후 메시지 전송
                    sleep(3);
                    socket.send(`Hello from User1 (VU ${__VU})`);
                    // User1: 1초 후 연결 종료 (세션 종료 시뮬레이션)
                    sleep(1);
                    socket.close();
                });
                socket.on("message", function (msg) {
                    console.log(`VU ${__VU} [User1] received: ${msg}`);
                    // 만약 "Peer disconnected" 메시지를 받으면 연결 종료
                    if (msg === "Peer disconnected") {
                        socket.close();
                    }
                });
                socket.on("close", function () {
                    console.log(`VU ${__VU} [User1] disconnected`);
                    resolve();
                });
                socket.on("error", function (e) {
                    console.log(`VU ${__VU} [User1] error: ${e.error()}`);
                    reject(e);
                });
            });
        });

        const user2Promise = new Promise((resolve, reject) => {
            ws.connect(url, {}, function (socket) {
                socket.on("open", function () {
                    console.log(`VU ${__VU} [User2] connected to session ${session_id}`);
                    // User2: 대기하여 User1의 메시지를 기다림
                });
                socket.on("message", function (msg) {
                    console.log(`VU ${__VU} [User2] received: ${msg}`);
                    // User2: 만약 "Peer disconnected" 메시지를 받으면 즉시 연결 종료
                    if (msg === "Peer disconnected") {
                        socket.close();
                    }
                    // 만약 일반 메시지를 받으면, 약간의 대기 후 응답 메시지 전송
                    else {
                        sleep(2);
                        socket.send(`Hello from User2 (VU ${__VU})`);
                    }
                });
                socket.on("close", function () {
                    console.log(`VU ${__VU} [User2] disconnected`);
                    resolve();
                });
                socket.on("error", function (e) {
                    console.log(`VU ${__VU} [User2] error: ${e.error()}`);
                    reject(e);
                });
                // User2: 최대 8초 대기 후, 연결 종료 (만약 아무 메시지도 오지 않으면)
                sleep(8);
                socket.close();
            });
        });

        // 4. 두 사용자의 연결이 모두 종료될 때까지 대기
        await Promise.all([user1Promise, user2Promise]);

        // 5. 다음 라운드 전에 짧은 대기
        sleep(2);
    }
}
