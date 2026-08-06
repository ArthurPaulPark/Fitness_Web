#!/usr/bin/env python3
"""
Exercise Video Augmentation Tool
운동 영상 데이터 증강 도구 - MediaPipe + GRU 학습 데이터 생성용

입력: 영상 1개 (또는 폴더)
출력: 증강 종류별로 각각 독립된 MP4 파일 N개
  ex) squat.mp4 + 17가지 증강 → squat_flip_h.mp4, squat_noise_gauss.mp4, ... (17개)
"""

import cv2
import numpy as np
import os
import json
import random
from pathlib import Path


# ──────────────────────────────────────────────────────────────────
# 프레임 단위 증강 함수
# ──────────────────────────────────────────────────────────────────

def add_gaussian_noise(frame: np.ndarray, intensity: float = 0.04) -> np.ndarray:
    sigma = intensity * 255
    noise = np.random.normal(0, sigma, frame.shape).astype(np.float32)
    return np.clip(frame.astype(np.float32) + noise, 0, 255).astype(np.uint8)

def add_salt_pepper_noise(frame: np.ndarray, amount: float = 0.015) -> np.ndarray:
    out = frame.copy()
    total = frame.shape[0] * frame.shape[1]
    n = int(total * amount / 2)
    for val in [255, 0]:
        coords = [np.random.randint(0, d - 1, n) for d in frame.shape[:2]]
        out[coords[0], coords[1]] = val
    return out

def add_motion_blur(frame: np.ndarray, kernel_size: int = 11, angle: float = 0) -> np.ndarray:
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[kernel_size // 2, :] = np.ones(kernel_size) / kernel_size
    M = cv2.getRotationMatrix2D((kernel_size / 2, kernel_size / 2), angle, 1)
    kernel = cv2.warpAffine(kernel, M, (kernel_size, kernel_size))
    return cv2.filter2D(frame, -1, kernel)

def add_compression_artifacts(frame: np.ndarray, quality: int = 25) -> np.ndarray:
    _, enc = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    return cv2.imdecode(enc, cv2.IMREAD_COLOR)

def add_brightness_variation(frame: np.ndarray, factor: float = 0.25) -> np.ndarray:
    delta = random.uniform(-factor, factor) * 255
    return np.clip(frame.astype(np.float32) + delta, 0, 255).astype(np.uint8)

def add_contrast_variation(frame: np.ndarray, factor: float = 0.4) -> np.ndarray:
    alpha = random.uniform(1 - factor, 1 + factor)
    return np.clip(frame.astype(np.float32) * alpha, 0, 255).astype(np.uint8)

def flip_horizontal(frame: np.ndarray) -> np.ndarray:
    return cv2.flip(frame, 1)

def flip_vertical(frame: np.ndarray) -> np.ndarray:
    return cv2.flip(frame, 0)

def flip_both(frame: np.ndarray) -> np.ndarray:
    return cv2.flip(frame, -1)

def rotate_frame(frame: np.ndarray, angle: float) -> np.ndarray:
    h, w = frame.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)

def random_crop_resize(frame: np.ndarray, ratio: float = 0.88) -> np.ndarray:
    h, w = frame.shape[:2]
    ch, cw = int(h * ratio), int(w * ratio)
    y = random.randint(0, h - ch)
    x = random.randint(0, w - cw)
    return cv2.resize(frame[y:y+ch, x:x+cw], (w, h))

def perspective_warp(frame: np.ndarray, strength: float = 0.04) -> np.ndarray:
    h, w = frame.shape[:2]
    d = int(min(h, w) * strength)
    src = np.float32([[0,0],[w,0],[0,h],[w,h]])
    dst = np.float32([
        [random.randint(0,d), random.randint(0,d)],
        [w-random.randint(0,d), random.randint(0,d)],
        [random.randint(0,d), h-random.randint(0,d)],
        [w-random.randint(0,d), h-random.randint(0,d)],
    ])
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)

def color_jitter(frame: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:,:,0] = (hsv[:,:,0] + random.randint(-10, 10)) % 180
    hsv[:,:,1] = np.clip(hsv[:,:,1] * random.uniform(0.7, 1.3), 0, 255)
    hsv[:,:,2] = np.clip(hsv[:,:,2] * random.uniform(0.8, 1.2), 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def grayscale_3ch(frame: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)


# ── 속도 변환 (프레임 리스트 전체에 적용) ─────────────────────────

def change_speed(frames: list, factor: float) -> list:
    if factor == 1.0:
        return frames
    if factor > 1.0:
        indices = [min(int(i * factor), len(frames)-1) for i in range(int(len(frames)/factor))]
        return [frames[i] for i in indices]
    new_count = int(len(frames) / factor)
    result = []
    for i in range(new_count):
        src = i * factor
        lo = int(src)
        hi = min(lo + 1, len(frames) - 1)
        a = src - lo
        blended = cv2.addWeighted(
            frames[lo].astype(np.float32), 1 - a,
            frames[hi].astype(np.float32), a, 0
        ).astype(np.uint8)
        result.append(blended)
    return result


# ──────────────────────────────────────────────────────────────────
# 증강 프리셋
# ──────────────────────────────────────────────────────────────────

AUGMENTATION_PRESETS = {
    "flip_h":       {"cat": "반전/회전", "name": "좌우 반전",      "frame_fn": flip_horizontal},
    "flip_v":       {"cat": "반전/회전", "name": "상하 반전",      "frame_fn": flip_vertical},
    "flip_both":    {"cat": "반전/회전", "name": "상하좌우 반전",  "frame_fn": flip_both},
    "rotate_5":     {"cat": "반전/회전", "name": "회전 +5°",       "frame_fn": lambda f: rotate_frame(f, 5)},
    "rotate_neg5":  {"cat": "반전/회전", "name": "회전 -5°",       "frame_fn": lambda f: rotate_frame(f, -5)},
    "noise_gauss":  {"cat": "노이즈",   "name": "가우시안 노이즈", "frame_fn": add_gaussian_noise},
    "noise_sp":     {"cat": "노이즈",   "name": "소금-후추 노이즈","frame_fn": add_salt_pepper_noise},
    "motion_blur":  {"cat": "노이즈",   "name": "모션 블러",       "frame_fn": lambda f: add_motion_blur(f, 11, random.uniform(0,180))},
    "compress":     {"cat": "노이즈",   "name": "압축 아티팩트",   "frame_fn": add_compression_artifacts},
    "brightness":   {"cat": "색상/밝기","name": "밝기 변화",       "frame_fn": add_brightness_variation},
    "contrast":     {"cat": "색상/밝기","name": "대비 변화",       "frame_fn": add_contrast_variation},
    "color_jitter": {"cat": "색상/밝기","name": "색상 지터",       "frame_fn": color_jitter},
    "grayscale":    {"cat": "색상/밝기","name": "그레이스케일",    "frame_fn": grayscale_3ch},
    "crop_resize":  {"cat": "기하변환", "name": "랜덤 크롭",       "frame_fn": random_crop_resize},
    "perspective":  {"cat": "기하변환", "name": "원근 왜곡",       "frame_fn": perspective_warp},
    "speed_fast":   {"cat": "속도",     "name": "1.5x 빠르게",     "speed_factor": 1.5},
    "speed_slow":   {"cat": "속도",     "name": "0.75x 느리게",    "speed_factor": 0.75},
}

CATEGORY_ORDER = ["반전/회전", "노이즈", "색상/밝기", "기하변환", "속도"]


# ──────────────────────────────────────────────────────────────────
# 핵심 함수: 영상 1개 → 증강 N개 → MP4 N개 저장
# ──────────────────────────────────────────────────────────────────

def read_video(path: str):
    """영상 읽기 → (프레임 리스트, fps, (w, h))"""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise IOError(f"영상을 열 수 없습니다: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    if not frames:
        raise ValueError(f"프레임 없음: {path}")
    return frames, fps, (w, h)


def augment_video(
    input_path: str,
    output_dir: str,
    selected_augs: list,
    progress_callback=None,   # fn(ratio: float, msg: str)
) -> list:
    """
    영상 1개를 읽어서 선택한 증강 각각을 독립 MP4로 저장.

    결과:
      output_dir/
        {stem}_flip_h.mp4
        {stem}_noise_gauss.mp4
        ...

    Returns: 저장된 파일 경로 리스트
    """
    frames, fps, (w, h) = read_video(input_path)
    stem = Path(input_path).stem
    os.makedirs(output_dir, exist_ok=True)

    saved = []
    total = len(selected_augs)

    for i, aug_key in enumerate(selected_augs):
        preset = AUGMENTATION_PRESETS[aug_key]
        out_path = os.path.join(output_dir, f"{stem}_{aug_key}.mp4")

        # 속도 변환 (프레임 수 바뀜)
        if "speed_factor" in preset:
            aug_frames = change_speed(frames, preset["speed_factor"])
        else:
            aug_frames = frames

        # 프레임별 증강 적용
        fn = preset.get("frame_fn")
        out_frames = [fn(f.copy()) if fn else f.copy() for f in aug_frames]

        # 저장
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))
        for f in out_frames:
            writer.write(f)
        writer.release()

        saved.append(out_path)

        if progress_callback:
            progress_callback(
                (i + 1) / total,
                f"[{i+1}/{total}] {preset['name']} → {Path(out_path).name}"
            )

    return saved


def augment_folder(
    input_dir: str,
    output_dir: str,
    selected_augs: list,
    extensions=('.mp4','.mov','.avi','.mkv','.MP4','.MOV','.AVI','.MKV'),
    progress_callback=None,
) -> dict:
    """
    폴더 안의 모든 영상에 대해 augment_video 실행.

    Returns: {영상파일명: [저장된 파일 경로 리스트]}
    """
    video_files = []
    for ext in extensions:
        video_files.extend(sorted(Path(input_dir).glob(f"*{ext}")))
    if not video_files:
        raise FileNotFoundError(f"영상 파일이 없습니다: {input_dir}")

    results = {}
    total = len(video_files)

    for i, vf in enumerate(video_files):
        def prog(ratio, msg, i=i):
            overall = (i + ratio) / total
            if progress_callback:
                progress_callback(overall, msg)

        saved = augment_video(str(vf), output_dir, selected_augs, progress_callback=prog)
        results[vf.name] = saved

    return results
