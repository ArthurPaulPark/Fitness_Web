# Third-party notices

This repository packages the following third-party runtime assets so the web application can run as a static site.

| Component | Files | License / source |
| --- | --- | --- |
| ONNX Runtime Web | `static/ort.min.js`, `static/ort-wasm-*.wasm` | [MIT License](https://github.com/microsoft/onnxruntime/blob/main/LICENSE) |
| MediaPipe Tasks Vision | `static/vision_bundle.*`, `static/wasm/**` | [Apache License 2.0](https://github.com/google-ai-edge/mediapipe/blob/master/LICENSE) |
| MediaPipe Pose Landmarker model | `pose_landmarker_full.task` | [MediaPipe model license](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker) |
| COI Service Worker | `coi-serviceworker.js` | [MIT License](https://github.com/gzuidhof/coi-serviceworker) |

The exercise-specific ONNX files in `models/` are project model weights. They are distributed under this repository's MIT license unless a later notice imposes additional restrictions.

When redistributing this project, retain the applicable upstream notices and review the linked licenses for your intended use.
