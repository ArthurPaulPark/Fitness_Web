# GRU Fitness

> A privacy-first, browser-based AI fitness assistant that counts repetitions and offers real-time form feedback for squats, push-ups, and pull-ups.

GRU Fitness runs entirely in the browser. It combines MediaPipe pose landmarks with exercise-specific GRU models exported to ONNX, so webcam frames, inferred pose data, and session statistics stay on the device. No backend, account, or API key is required.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Runtime](https://img.shields.io/badge/runtime-static%20web%20app-2ea44f)
![Inference](https://img.shields.io/badge/inference-MediaPipe%20%2B%20ONNX%20Runtime-7c3aed)

## Features

- Real-time webcam pose tracking with a visible skeleton overlay
- Separate GRU posture classifiers for squat, push-up, and pull-up
- Rep counting driven by exercise-specific joint-angle state machines
- Form score, stability score, corrective feedback, and optional Korean voice guidance
- Fully static deployment: works on GitHub Pages and any HTTPS static host
- Optional local video augmentation utility for private dataset preparation

## How it works

```text
Webcam → MediaPipe Pose Landmarker → 33 landmarks × (x, y, z, visibility)
       → 30-frame sequence (132 features/frame) → 2-layer GRU (64 hidden units/layer)
       → ONNX Runtime Web → Good / Bad posture signal
       → angle rules + state machine → reps, score, feedback
```

The bundled models are exercise-specific ONNX files with a `[batch, 30, 132]` input and a two-class output. The rule-based layer uses knee angle for squats, elbow angle for push-ups, and both elbow angles for pull-ups. A rep is only accepted after the sequence receives a `Good` posture signal during its measuring phase.

## Quick start

### Run locally

A browser needs a secure origin (or `localhost`) to grant camera access. Do not open `index.html` directly with `file://`.

```bash
python3 -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000), allow camera access, and wait for the models to load. Any other static web server is fine.

### Deploy to GitHub Pages

1. Create a GitHub repository and upload the contents of this directory.
2. In **Settings → Pages**, choose **Deploy from a branch**, then select `main` and `/ (root)`.
3. Open the published HTTPS URL and grant camera permission.

All application asset paths are relative, so the site works both at a custom domain and at `https://<user>.github.io/<repository>/`.

## Camera setup

| Exercise | Recommended camera view | Frame guidance |
| --- | --- | --- |
| Squat | Side view | Include feet through head. |
| Push-up | Side view | Keep wrists through ankles visible. |
| Pull-up | Rear view | Keep both shoulders and elbows visible. |

Good lighting, a stable camera, and full-body framing improve pose tracking. The thresholds and feedback rules are heuristics, not a substitute for coaching or professional assessment.

## Repository layout

```text
.
├── index.html                    # Application UI, tracking, inference, and feedback logic
├── models/                       # Bundled GRU ONNX weights (squat, push-up, pull-up)
├── pose_landmarker_full.task     # MediaPipe pose model
├── static/                       # Bundled ONNX Runtime Web and MediaPipe WASM assets
├── coi-serviceworker.js          # Enables cross-origin isolation where supported
├── tools/video-augmenter/        # Local dataset video augmentation utility
├── THIRD_PARTY_NOTICES.md        # Licenses for bundled dependencies
└── LICENSE
```

## Development notes

The deployment application is deliberately dependency-free: its code lives in `index.html` and loads its pinned runtime assets from `static/`. This makes it easy to host but means the model and UI logic are not split into a build system.

`tools/video-augmenter/` is optional and is not used by the web application at runtime. See its [README](tools/video-augmenter/README.md) for setup and usage.

### Model scope and reproducibility

The release includes inference-ready ONNX model weights. **No training data, source footage, augmented footage, landmark CSV files, or labels are included in this repository.** The original workspace also did not include a GRU training/export script, so this repository intentionally does not claim full training reproducibility. If you contribute retraining code, document the data source, consent/license, label definition, preprocessing, evaluation split, and ONNX export command.

## Privacy and safety

- Camera frames are processed locally in the browser; this app has no server endpoint or telemetry.
- The browser may cache model and runtime files as normal site assets. Clear site data if you want to remove those caches.
- Never commit videos, datasets, `.env` files, or credentials without checking consent and licensing. The included `.gitignore` excludes common local and generated files.
- This project is for educational and fitness-assistance purposes only. It is not medical advice, a diagnosis tool, or a guarantee of exercise safety. Stop if you feel pain and seek qualified guidance when appropriate.

## Third-party software

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the notices and licenses for MediaPipe, ONNX Runtime Web, and the service worker.

## Contributing

Issues and pull requests are welcome. For changes that affect inference, please include the exercise, camera view, browser/device tested, and a short before/after description. Do not add identifiable training footage without explicit permission and a redistribution license.

## License

This project is released under the [MIT License](LICENSE). Third-party runtime assets remain subject to their own licenses.

---

# 한국어 안내

> 스쿼트·푸시업·풀업의 반복 횟수를 세고 실시간 자세 피드백을 제공하는, 브라우저 기반 AI 피트니스 어시스턴트입니다.

GRU Fitness는 브라우저 안에서만 실행됩니다. MediaPipe 포즈 랜드마크와 운동별 GRU ONNX 모델을 결합하며, 웹캠 영상·추론된 포즈 정보·세션 기록을 서버로 전송하지 않습니다. 백엔드, 계정, API 키가 필요 없습니다.

## 주요 기능

- 웹캠 기반 실시간 포즈 추적 및 스켈레톤 오버레이
- 스쿼트·푸시업·풀업별 GRU 자세 분류 모델
- 관절 각도 상태 머신 기반의 반복 횟수 카운트
- 자세 점수, 안정성 점수, 교정 피드백, 선택형 한국어 음성 안내
- GitHub Pages 등 HTTPS 정적 호스팅에 바로 배포 가능
- 비공개 데이터셋 준비에 사용할 수 있는 선택형 로컬 영상 증강 도구

## 동작 방식

```text
웹캠 → MediaPipe Pose Landmarker → 33개 랜드마크 × (x, y, z, visibility)
     → 30프레임 시퀀스(프레임당 132개 특성) → 2계층 GRU(계층당 hidden unit 64개)
     → ONNX Runtime Web → Good / Bad 자세 신호
     → 관절 각도 규칙 + 상태 머신 → 횟수, 점수, 피드백
```

포함된 모델은 운동별 ONNX 파일이며 입력 형태는 `[batch, 30, 132]`, 출력은 2개 클래스입니다. 스쿼트는 무릎 각도, 푸시업은 팔꿈치 각도, 풀업은 양쪽 팔꿈치 각도를 이용해 반복 동작을 판정합니다. 측정 구간에서 `Good` 자세 신호가 확인되어야 반복 횟수가 인정됩니다.

## 빠른 시작

### 로컬에서 실행하기

브라우저가 카메라 권한을 받으려면 보안 연결 또는 `localhost`가 필요합니다. `index.html`을 `file://`로 직접 열지 마세요.

```bash
python3 -m http.server 8000
```

[http://localhost:8000](http://localhost:8000)을 열고 카메라 접근을 허용한 뒤 모델 로딩이 끝날 때까지 기다리면 됩니다. 다른 정적 웹 서버를 사용해도 됩니다.

### GitHub Pages 배포

1. GitHub 저장소를 만들고 이 폴더의 내용을 업로드합니다.
2. **Settings → Pages**에서 **Deploy from a branch**를 선택한 뒤 `main` 브랜치와 `/ (root)`를 지정합니다.
3. 배포된 HTTPS 주소를 열고 카메라 접근을 허용합니다.

앱 내부 자산은 모두 상대 경로를 사용하므로 사용자 도메인뿐 아니라 `https://<user>.github.io/<repository>/` 형태에서도 동작합니다.

## 카메라 설치 가이드

| 운동 | 권장 카메라 방향 | 화면 구성 |
| --- | --- | --- |
| 스쿼트 | 측면 | 발부터 머리까지 전신이 보이게 합니다. |
| 푸시업 | 측면 | 손목부터 발목까지 보이게 합니다. |
| 풀업 | 후면 | 양쪽 어깨와 팔꿈치가 모두 보이게 합니다. |

밝은 환경, 흔들리지 않는 카메라, 전신이 들어오는 구도가 포즈 추적 정확도에 도움이 됩니다. 임계값과 피드백 규칙은 휴리스틱이며 전문 코칭이나 평가를 대체하지 않습니다.

## 프로젝트 구성

```text
.
├── index.html                    # UI, 추적, 추론, 피드백 로직
├── models/                       # GRU ONNX 모델 가중치
├── pose_landmarker_full.task     # MediaPipe 포즈 모델
├── static/                       # ONNX Runtime Web 및 MediaPipe WASM 자산
├── coi-serviceworker.js          # 지원 브라우저에서 cross-origin isolation 활성화
├── tools/video-augmenter/        # 로컬 영상 증강 도구
├── THIRD_PARTY_NOTICES.md        # 번들된 외부 의존성 라이선스
└── LICENSE
```

## 개발 및 모델 범위

배포 앱은 의존성 설치나 빌드 단계 없이 `index.html`과 `static/`의 고정 런타임 자산만으로 동작합니다. `tools/video-augmenter/`는 선택 도구이며 웹 앱 실행에는 사용되지 않습니다. 설정 방법은 해당 폴더의 [README](tools/video-augmenter/README.md)를 참고하세요.

이 저장소에는 추론 가능한 ONNX 모델 가중치만 포함됩니다. **학습 데이터, 원본 영상, 증강 영상, 랜드마크 CSV, 라벨 데이터는 포함하지 않으며 공개하지 않습니다.** 원본 작업 공간에는 GRU 학습·ONNX 내보내기 스크립트가 없었으므로, 이 저장소는 전체 학습 재현성을 주장하지 않습니다. 재학습 코드를 기여할 경우 데이터 출처, 동의 및 라이선스, 라벨 정의, 전처리, 평가 분할, ONNX 내보내기 명령을 문서화해 주세요.

## 개인정보 및 안전

- 카메라 프레임은 브라우저 내부에서 처리되며 서버 엔드포인트나 텔레메트리가 없습니다.
- 브라우저는 일반적인 사이트 자산처럼 모델과 런타임 파일을 캐시할 수 있습니다. 캐시를 지우려면 사이트 데이터를 삭제하세요.
- 동의와 재배포 권한이 없는 영상·데이터셋·`.env` 파일·자격 증명은 커밋하지 마세요. `.gitignore`가 일반적인 로컬·생성 파일을 제외합니다.
- 이 프로젝트는 교육 및 운동 보조 목적이며 의료 조언, 진단 도구, 운동 안전 보장이 아닙니다. 통증이 느껴지면 운동을 중단하고 자격을 갖춘 전문가의 안내를 받으세요.

## 외부 소프트웨어 및 라이선스

MediaPipe, ONNX Runtime Web, 서비스 워커의 고지와 라이선스는 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 정리되어 있습니다. 프로젝트 코드는 [MIT License](LICENSE)로 제공되며, 외부 런타임 자산에는 각자의 라이선스가 적용됩니다.

## 기여하기

이슈와 Pull Request를 환영합니다. 추론 동작에 영향을 주는 변경은 운동 종류, 카메라 방향, 테스트한 브라우저/기기, 변경 전후 설명을 함께 적어 주세요. 명시적인 동의와 재배포 라이선스가 없는 식별 가능한 학습 영상은 추가하지 마세요.
