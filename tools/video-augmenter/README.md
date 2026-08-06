# Exercise Video Augmenter

A local utility for creating augmented copies of exercise videos before pose-data extraction or model training.

## Install and run

```bash
cd tools/video-augmenter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python augment_gui.py
```

On macOS/Linux, `./run.sh` creates the virtual environment and launches the GUI. Use `./run.sh cli --help` for the command-line interface.

## Inputs and outputs

- Accepts MP4, MOV, AVI, and MKV files.
- Produces a separate MP4 for every selected augmentation.
- Includes flips, small rotations, noise, blur, compression, brightness/contrast/color changes, cropping, perspective warp, and speed changes.

Do not commit source videos or generated outputs. The repository `.gitignore` excludes common video formats plus the tool's local data/output directories by default.
