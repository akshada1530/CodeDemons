# Automated OMR Evaluation & Scoring System

An end-to-end automated system for evaluating OMR sheets for exams, built with Python and OpenCV. This project detects filled bubbles, evaluates answers against an answer key, generates per-subject and total scores, and produces overlay images and JSON reports.

---

## Features

* Detects filled bubbles from scanned or photographed OMR sheets.
* Supports multiple sheet versions and exam formats.
* Generates per-question, per-subject, and total scores.
* Saves overlay images with detected bubbles.
* Stores JSON results for audit and reporting.
* Fully configurable threshold for detection.

---

## Technologies Used

* Python
* OpenCV
* NumPy
* JSON
* Flask / FastAPI (optional for web interface)
* Streamlit (optional for evaluator dashboard)

---

## Project Structure

```
omr_mvp/
├─ data/
│   ├─ samples/        # Sample OMR sheet images
│   ├─ templates/      # JSON templates for bubble positions
│   └─ answer_keys/    # Answer key JSON files
├─ src/
│   ├─ template_builder.py
│   ├─ omr_pipeline.py
│   └─ process_cli.py
└─ output/             # Overlay images and results
```

---

## Usage

### 1. Build Template

```bash
python src/template_builder.py --img data/samples/clean_sheet.jpg --out data/templates/version_A_template.json
```

* Click all bubbles for all questions (1A–1D, 2A–2D … 100A–100D).
* Press any key when finished.

### 2. Create Answer Key

Example: `data/answer_keys/version_A_key.json`

```json
{
  "1": "B",
  "2": "D",
  "3": "A",
  ...
  "100": "C"
}
```

### 3. Run OMR Pipeline

```bash
python src/process_cli.py \
--img data/samples/IMG_001.jpg \
--template data/templates/version_A_template.json \
--key data/answer_keys/version_A_key.json \
--out output --thresh 180
```

* Outputs:

  * `output/IMG_001_overlay.png` → Shows detected bubbles
  * `output/IMG_001_results.json` → Detailed scores per question and total

---

## Future Enhancements

* Batch processing for multiple sheets at once.
* Web application for uploading sheets and viewing results.
* Machine learning model for ambiguous or partially filled bubbles.
* Automatic sheet version detection and adaptive thresholding.
* Analytics dashboard for class-wise results.
