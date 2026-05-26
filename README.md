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

## 🚀 깃허브 페이지(GitHub Pages) 초간단 배포 방법

터미널을 실행하고 **이 `web_deploy` 폴더 안으로 이동한 뒤** 아래의 명령어를 입력하면 10초 만에 나만의 공식 웹사이트가 배포됩니다.

```bash
# 1. 깃 초기화 및 커밋
git init
git add .
git commit -m "deploy: Premium AI PT Studio web release"

# 2. 브랜치명 설정 및 본인의 원격 깃허브 저장소 주소 추가
git branch -M main
git remote add origin https://github.com/<본인의-깃허브-ID>/<저장소-이름>.git

# 3. 깃허브 원격 서버로 전송
git push -u origin main
```

### ⚙️ 깃허브 웹 서비스 활성화 절차 (마지막 단계)
1. 생성하신 깃허브 레포지토리 웹사이트로 이동합니다.
2. 상단 메뉴의 **`Settings` (설정)** ➡ 좌측의 **`Pages` (페이지)** 메뉴를 클릭합니다.
3. `Build and deployment` 아래의 **`Branch`** 설정을 **`main`** 브랜치 및 **`/ (root)`** 경로로 선택한 뒤 **`Save` (저장)** 버튼을 누릅니다.
4. 약 1분 후 생성되는 **`https://<깃허브-ID>.github.io/<저장소-이름>/`** 공식 주소로 언제 어디서나 AI PT 서비스를 즐기실 수 있습니다!
