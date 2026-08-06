#!/bin/bash
# ──────────────────────────────────────────────────────────────
# 운동 영상 증강 도구 - macOS M5 설치 & 실행 스크립트
# ──────────────────────────────────────────────────────────────
set -e

VENV_DIR="$(dirname "$0")/.venv"
SCRIPT_DIR="$(dirname "$0")"

echo "🏋️  Exercise Video Augmentor"
echo "─────────────────────────────────────────"

# Python 확인
if ! command -v python3 &>/dev/null; then
    echo "❌ python3가 없습니다. https://brew.sh 로 Homebrew 설치 후"
    echo "   brew install python3  를 실행하세요."
    exit 1
fi

echo "✓ Python: $(python3 --version)"

# 가상환경 생성 (없으면)
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 가상환경 생성 중..."
    python3 -m venv "$VENV_DIR"
fi

# 활성화
source "$VENV_DIR/bin/activate"

# 의존 패키지 설치
echo "📥 패키지 확인/설치 중..."
pip install --upgrade pip -q
pip install -r "$SCRIPT_DIR/requirements.txt" -q

echo ""
echo "─────────────────────────────────────────"

# 실행 모드 결정
if [ "$1" = "cli" ]; then
    # CLI 모드
    shift
    python3 "$SCRIPT_DIR/augment_video.py" "$@"
else
    # GUI 모드 (기본)
    echo "🖥  GUI 실행 중..."
    python3 "$SCRIPT_DIR/augment_gui.py"
fi
