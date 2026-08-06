#!/usr/bin/env python3
"""
운동 영상 증강 도구 - GUI
입력 영상 1개(또는 폴더) → 증강별 독립 MP4 파일 N개 출력
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading, os, time
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, os.path.dirname(__file__))
from augment_video import AUGMENTATION_PRESETS, CATEGORY_ORDER, augment_video, augment_folder

BG_DARK  = "#0f1117"; BG_CARD  = "#1a1d27"; BG_INPUT = "#242736"
ACCENT   = "#6c63ff"; ACCENT2  = "#ff6584"; SUCCESS  = "#43d9a2"
WARNING  = "#ffc75f"; TEXT_PRI = "#e8eaf0"; TEXT_SEC = "#8b8fa8"
BORDER   = "#2e3148"


class AugmentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🏋️  Exercise Video Augmentor")
        self.geometry("980x800")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        self.input_path  = tk.StringVar()
        self.output_dir  = tk.StringVar()
        self.mode        = tk.StringVar(value="single")  # single / folder
        self.is_running  = False
        self._stop_flag  = False

        self.aug_vars = {k: tk.BooleanVar(value=True) for k in AUGMENTATION_PRESETS}

        self._apply_style()
        self._build_ui()

    def _apply_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame",       background=BG_DARK)
        s.configure("Card.TFrame",  background=BG_CARD)
        s.configure("TLabel",       background=BG_DARK,  foreground=TEXT_PRI, font=("SF Pro Display", 12))
        s.configure("Card.TLabel",  background=BG_CARD,  foreground=TEXT_PRI, font=("SF Pro Display", 12))
        s.configure("Dim.TLabel",   background=BG_CARD,  foreground=TEXT_SEC, font=("SF Pro Display", 10))
        s.configure("Head.TLabel",  background=BG_DARK,  foreground=TEXT_PRI, font=("SF Pro Display", 18, "bold"))
        s.configure("Sub.TLabel",   background=BG_DARK,  foreground=TEXT_SEC, font=("SF Pro Display", 11))
        s.configure("TCheckbutton", background=BG_CARD,  foreground=TEXT_PRI, font=("SF Pro Display", 11))
        s.configure("TRadiobutton", background=BG_DARK,  foreground=TEXT_PRI, font=("SF Pro Display", 11))
        s.configure("TProgressbar", troughcolor=BG_INPUT, background=ACCENT, thickness=6, borderwidth=0)

    def _build_ui(self):
        hdr = ttk.Frame(self)
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        ttk.Label(hdr, text="Exercise Video Augmentor", style="Head.TLabel").pack(side="left")
        ttk.Label(hdr, text="영상 1개 → 증강별 MP4 N개 출력", style="Sub.TLabel").pack(side="left", padx=12, pady=4)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=28, pady=12)

        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=28)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        self._build_left(main)
        self._build_right(main)
        self._build_bottom()

    def _card(self, parent, title, **grid_kw):
        outer = ttk.Frame(parent, style="Card.TFrame")
        outer.grid(**grid_kw, sticky="nsew", padx=(0,6), pady=4)
        ttk.Label(outer, text=title, background=BG_CARD,
                  foreground=ACCENT, font=("SF Pro Display", 10, "bold")).pack(anchor="w", padx=14, pady=(10,4))
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", padx=14)
        return outer

    def _flat_btn(self, parent, text, cmd, bg=BG_INPUT, fg=TEXT_SEC, **pack_kw):
        b = tk.Button(parent, text=text, bg=bg, fg=fg,
                      activebackground=ACCENT, activeforeground="#fff",
                      relief="flat", bd=0, padx=10, pady=4,
                      font=("SF Pro Display", 10), cursor="hand2", command=cmd)
        b.pack(**pack_kw)
        return b

    def _build_left(self, parent):
        left = ttk.Frame(parent)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # 경로 카드
        pc = self._card(left, "📁  경로 설정", row=0, column=0)
        pi = ttk.Frame(pc, style="Card.TFrame")
        pi.pack(fill="x", padx=14, pady=10)

        # 모드 선택
        mr = ttk.Frame(pi, style="Card.TFrame")
        mr.pack(fill="x", pady=(0, 8))
        ttk.Label(mr, text="처리 모드 :", style="Dim.TLabel", width=9).pack(side="left")
        ttk.Radiobutton(mr, text="단일 파일", variable=self.mode, value="single",
                        style="TRadiobutton",
                        command=self._on_mode).pack(side="left", padx=(8,6))
        ttk.Radiobutton(mr, text="폴더 전체", variable=self.mode, value="folder",
                        style="TRadiobutton",
                        command=self._on_mode).pack(side="left")

        self._path_row(pi, "입력",   self.input_path, self._browse_input)
        self._path_row(pi, "출력 폴더", self.output_dir, self._browse_output)

        # 예상 출력 설명
        self.expect_lbl = ttk.Label(pi,
            text="※ 선택한 증강 수만큼 MP4 파일이 생성됩니다",
            style="Dim.TLabel")
        self.expect_lbl.pack(anchor="w", pady=(6,0))

        # 증강 선택 카드
        ac = self._card(left, "🎛  증강 옵션 선택", row=1, column=0)
        br = ttk.Frame(ac, style="Card.TFrame")
        br.pack(fill="x", padx=14, pady=6)
        for label, fn in [("전체 선택", self._sel_all), ("전체 해제", self._desel_all),
                           ("반전만", self._sel_flip), ("노이즈만", self._sel_noise)]:
            self._flat_btn(br, label, fn, side="left", padx=(0,6))

        inner = self._scrollable(ac)
        self._build_aug_checks(inner)

    def _path_row(self, parent, label, var, cmd):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=f"{label} :", style="Dim.TLabel", width=9).pack(side="left")
        tk.Entry(row, textvariable=var, bg=BG_INPUT, fg=TEXT_PRI,
                 insertbackground=TEXT_PRI, relief="flat",
                 font=("SF Mono", 10), bd=0).pack(side="left", fill="x", expand=True, ipady=6, padx=6)
        self._flat_btn(row, "찾기", cmd, bg=ACCENT, fg="#fff", side="right")

    def _scrollable(self, parent):
        canvas = tk.Canvas(parent, bg=BG_CARD, highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas, style="Card.TFrame")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=14, pady=6)
        sb.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
        return inner

    def _build_aug_checks(self, parent):
        cur_cat = None
        for key, preset in AUGMENTATION_PRESETS.items():
            cat = preset["cat"]
            if cat != cur_cat:
                cur_cat = cat
                ttk.Label(parent, text=cat, background=BG_CARD,
                          foreground=ACCENT2, font=("SF Pro Display", 10, "bold")).pack(anchor="w", pady=(10,2))
            ttk.Checkbutton(parent, text=f"  {preset['name']}",
                            variable=self.aug_vars[key],
                            style="TCheckbutton").pack(anchor="w", padx=8)

    def _build_right(self, parent):
        right = ttk.Frame(parent)
        right.grid(row=0, column=1, sticky="nsew", padx=(6,0))
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # 출력 파일 미리보기
        pc = self._card(right, "📂  생성될 파일 목록", row=0, column=0)
        self.preview_text = tk.Text(pc, bg=BG_INPUT, fg=TEXT_PRI,
                                    font=("SF Mono", 9), relief="flat", bd=0,
                                    wrap="word", state="disabled", height=10)
        self.preview_text.pack(fill="both", padx=14, pady=8)

        # 로그
        lc = self._card(right, "📋  처리 로그", row=1, column=0)
        lc.rowconfigure(1, weight=1)
        lc.columnconfigure(0, weight=1)
        self.log_text = tk.Text(lc, bg=BG_INPUT, fg=TEXT_PRI,
                                font=("SF Mono", 9), relief="flat", bd=0,
                                wrap="word", state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=14, pady=8)

    def _build_bottom(self):
        bot = ttk.Frame(self)
        bot.pack(fill="x", padx=28, pady=12)

        pf = ttk.Frame(bot)
        pf.pack(fill="x", pady=(0,8))
        self.progress = ttk.Progressbar(pf, style="TProgressbar", mode="determinate", maximum=100)
        self.progress.pack(fill="x")
        self.prog_label = ttk.Label(pf, text="대기 중", style="Sub.TLabel")
        self.prog_label.pack(anchor="e")

        br = ttk.Frame(bot)
        br.pack(fill="x")
        self.run_btn = tk.Button(br, text="▶  증강 시작",
                                 bg=ACCENT, fg="#fff", activebackground="#7c74ff",
                                 relief="flat", bd=0, padx=24, pady=10,
                                 font=("SF Pro Display", 13, "bold"), cursor="hand2",
                                 command=self._start)
        self.run_btn.pack(side="left")
        self.stop_btn = tk.Button(br, text="■  중지",
                                  bg=BG_INPUT, fg=TEXT_SEC,
                                  relief="flat", bd=0, padx=16, pady=10,
                                  font=("SF Pro Display", 12), cursor="hand2",
                                  state="disabled", command=self._stop)
        self.stop_btn.pack(side="left", padx=10)
        self.status_lbl = ttk.Label(br, text="", style="Sub.TLabel")
        self.status_lbl.pack(side="right", pady=4)

    # ──────────────────────── 이벤트 ────────────────────────

    def _on_mode(self):
        self._update_preview()

    def _browse_input(self):
        if self.mode.get() == "folder":
            path = filedialog.askdirectory(title="입력 폴더 선택")
        else:
            path = filedialog.askopenfilename(
                title="입력 영상 선택",
                filetypes=[("영상 파일", "*.mp4 *.mov *.avi *.mkv"), ("전체", "*.*")]
            )
        if path:
            self.input_path.set(path)
            if not self.output_dir.get():
                p = Path(path)
                base = p if p.is_dir() else p.parent
                self.output_dir.set(str(base / "augmented"))
            self._update_preview()

    def _browse_output(self):
        path = filedialog.askdirectory(title="출력 폴더 선택")
        if path:
            self.output_dir.set(path)

    def _sel_all(self):
        [v.set(True) for v in self.aug_vars.values()]
        self._update_preview()

    def _desel_all(self):
        [v.set(False) for v in self.aug_vars.values()]
        self._update_preview()

    def _sel_flip(self):
        self._desel_all()
        for k in ["flip_h", "flip_v", "flip_both"]:
            self.aug_vars[k].set(True)
        self._update_preview()

    def _sel_noise(self):
        self._desel_all()
        for k in ["noise_gauss", "noise_sp", "motion_blur", "compress"]:
            self.aug_vars[k].set(True)
        self._update_preview()

    def _update_preview(self):
        selected = [k for k, v in self.aug_vars.items() if v.get()]
        inp = self.input_path.get()
        stem = Path(inp).stem if inp else "video"

        lines = [f"총 {len(selected)}개 파일 생성 예정\n"]
        for k in selected:
            lines.append(f"  {stem}_{k}.mp4")

        self.expect_lbl.configure(
            text=f"※ 증강 {len(selected)}개 선택 → MP4 {len(selected)}개 생성"
        )
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("end", "\n".join(lines) if lines else "(없음)")
        self.preview_text.configure(state="disabled")

    def _log(self, msg: str):
        self.log_text.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{ts}] {msg}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # ──────────────────────── 실행 ────────────────────────

    def _start(self):
        if self.is_running:
            return
        selected = [k for k, v in self.aug_vars.items() if v.get()]
        if not selected:
            messagebox.showwarning("경고", "증강 옵션을 하나 이상 선택하세요.")
            return
        inp = self.input_path.get().strip()
        out = self.output_dir.get().strip()
        if not inp:
            messagebox.showwarning("경고", "입력 경로를 지정하세요.")
            return
        if not out:
            messagebox.showwarning("경고", "출력 폴더를 지정하세요.")
            return

        self.is_running = True
        self._stop_flag = False
        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.progress["value"] = 0
        self._log(f"시작  입력: {inp}")
        self._log(f"      출력 폴더: {out}")
        self._log(f"      증강 {len(selected)}종 → MP4 {len(selected)}개 생성")

        threading.Thread(target=self._worker, args=(inp, out, selected), daemon=True).start()

    def _stop(self):
        self._stop_flag = True
        self._log("⚠️  중지 요청됨...")

    def _worker(self, inp, out, selected):
        try:
            start = time.time()

            def prog(ratio, msg):
                if self._stop_flag:
                    raise InterruptedError()
                val = ratio * 100
                self.after(0, lambda: [
                    self.progress.__setitem__("value", val),
                    self.prog_label.configure(text=f"{val:.0f}%  —  {msg}"),
                    self._log(msg),
                ])

            if self.mode.get() == "folder" or Path(inp).is_dir():
                results = augment_folder(inp, out, selected, progress_callback=prog)
                total_files = sum(len(v) for v in results.values())
                self.after(0, lambda: self._on_done(total_files, out, time.time()-start))
            else:
                saved = augment_video(inp, out, selected, progress_callback=prog)
                self.after(0, lambda: self._on_done(len(saved), out, time.time()-start))

        except InterruptedError:
            self.after(0, self._on_stopped)
        except Exception as e:
            self.after(0, lambda: self._on_error(str(e)))

    def _on_done(self, n_files, out_dir, elapsed):
        self.is_running = False
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress["value"] = 100
        self.prog_label.configure(text="완료!")
        self.status_lbl.configure(text=f"완료 ✓  ({elapsed:.1f}s)", foreground=SUCCESS)
        self._log(f"✅ 완료! MP4 {n_files}개 생성  ({elapsed:.1f}초 소요)")
        self._log(f"   저장 위치: {out_dir}")
        messagebox.showinfo("완료",
            f"증강 완료!\n\nMP4 {n_files}개 생성\n저장 위치: {out_dir}\n소요 시간: {elapsed:.1f}초")

    def _on_stopped(self):
        self.is_running = False
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_lbl.configure(text="중지됨", foreground=WARNING)

    def _on_error(self, msg):
        self.is_running = False
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self._log(f"❌ 오류: {msg}")
        messagebox.showerror("오류", msg)


def main():
    app = AugmentApp()
    for v in app.aug_vars.values():
        v.trace_add("write", lambda *_: app._update_preview())
    app._update_preview()
    app.mainloop()


if __name__ == "__main__":
    main()
