# Modelle und Lizenzen

`models/manifest.json` pinnt Herkunft, Version, SHA-256, Lizenz, Eingabeformat,
Runtime und erlaubten Status. Der Installationsbefehl lädt nur auf ausdrücklichen
Aufruf; der Dienst lädt niemals zur Laufzeit Modelle nach. Offline werden die
verifizierten Dateien samt Manifest in das Modellvolume übertragen.

- `yunet-sface-2023mar-2021dec`: bevorzugt, CPU/ONNX. YuNet
  `face_detection_yunet_2023mar.onnx`, SHA-256
  `8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4`,
  MIT; SFace `face_recognition_sface_2021dec.onnx`, SHA-256
  `0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79`,
  Apache-2.0. Herkunft ist das offizielle OpenCV-Zoo-Repository.
- `haar-lbph-baseline-v1`: OpenCV-Haar-Kaskade plus reproduzierbares lokales
  Binary-Pattern-Histogramm. Nur Legacy-Baseline, keine Produktivempfehlung.
- `insightface-scrfd-arcface-disabled`: Adapterstatus
  `model_not_licensed_or_installed`. Keine Gewichte, kein Download und keine
  Verarbeitung realer Fotos ohne schriftlichen Lizenznachweis, Modell-ID,
  Version und Prüfsumme. SCRFD und RetinaFace wären alternative Detektoren.

Embeddings tragen Pipeline und Modellversion; inkompatible Versionen werden
nicht verglichen. Schwellenwerte müssen später mit rechtmäßig freigegebenem
Material kalibriert werden. Grundmodelle werden nicht mit Klassenfotos trainiert.
