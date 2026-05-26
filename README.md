# 🏋️‍♂️ Premium Edge AI PT Studio — Web Production Release

이 폴더는 **100% 클라이언트 사이드 온디바이스(Client-Side Edge AI) 웹 서비스** 배포용 패키지입니다. 
파이썬 백엔드 서버 없이, 오직 이 폴더에 있는 정적 파일들만 업로드하여 무료로 웹캠 AI 트래킹 사이트를 개설할 수 있습니다.

---

## 📁 파일 구성 정보

* **`index.html`**: 메인 UI 디자인 및 AI 오케스트레이션 코드
* **`coi-serviceworker.js`**: 브라우저 보안 헤더 우회용 서비스 워커 스크립트 (WASM 멀티스레드 활성화 목적)
* **`pose_landmarker_full.task`**: 구글 미디어파이프 신체 트래킹 모델 파일 (~9.4 MB)
* **`static/`**: 포즈 감지 및 ONNX Web Assembly 런타임 코어 바이너리 폴더
* **`models/`**: 학습이 완비된 스쿼트, 푸시업, 풀업 GRU 신경망 ONNX 가중치 폴더

---