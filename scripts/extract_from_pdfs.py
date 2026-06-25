"""AICA L2 예시문항 PDF → quiz/data/questions.json 변환"""
from __future__ import annotations

import json
import re
from pathlib import Path

import fitz
import numpy as np
from rapidocr_onnxruntime import RapidOCR

BASE = Path(__file__).resolve().parents[2]
PDF_DIR = BASE
OUT = Path(__file__).resolve().parents[1] / "data" / "questions.json"
CACHE = Path(__file__).resolve().parent / "ocr_cache.json"

CIRCLED = {"①": 0, "②": 1, "③": 2, "④": 3, "⑤": 4}
ANS_PAT = re.compile(r"\[:\s*([①②③④⑤@①②③④⑤]|\d+)\]")
OPT_PAT = re.compile(r"^([①②③④⑤])\s*(.+)")
NUM_PAT = re.compile(r"^(\d{1,3})\s*[\.\)]\s*(.+)")


def pdf_label(path: Path) -> str:
    name = path.stem
    m = re.search(r"\((\d+)\)", name)
    num = m.group(1) if m else "?"
    level = "초급" if "초급" in name else "중급" if "중급" in name else ""
    return f"예시문항({num}) {level}".strip()


def ocr_page(page, ocr: RapidOCR) -> list[str]:
    pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5))
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n >= 3:
        img = img[:, :, :3]
    result, _ = ocr(img)
    return [r[1].strip() for r in result] if result else []


def parse_answer_token(tok: str) -> int | None:
    tok = tok.strip()
    if tok in CIRCLED:
        return CIRCLED[tok]
    if tok == "@":
        return 1
    if tok.isdigit():
        n = int(tok)
        return n - 1 if n > 0 else None
    for ch, idx in CIRCLED.items():
        if ch in tok:
            return idx
    return None


def parse_page_lines(lines: list[str], source: str, page_no: int) -> list[dict]:
    items = []
    i = 0
    while i < len(lines):
        block_start = i
        answer_idx = None
        options: list[str] = []
        question_parts: list[str] = []

        while i < len(lines):
            line = lines[i]
            m_ans = ANS_PAT.search(line)
            if m_ans:
                answer_idx = parse_answer_token(m_ans.group(1))
                i += 1
                break

            m_opt = OPT_PAT.match(line)
            if m_opt:
                options.append(m_opt.group(2).strip())
                i += 1
                continue

            if line.startswith("[:") and "@" in line:
                answer_idx = 1
                i += 1
                break

            if not options and line and not line.startswith("AICA"):
                nm = NUM_PAT.match(line)
                if nm:
                    question_parts.append(nm.group(2).strip())
                elif not line.startswith("==="):
                    question_parts.append(line)
            i += 1

        if answer_idx is None or len(options) < 2:
            continue

        qtext = " ".join(question_parts).strip()
        if len(qtext) < 4:
            qtext = f"[{source} p.{page_no}] 다음 중 옳은 것은?"

        if answer_idx >= len(options):
            continue

        choices = 5 if len(options) >= 5 else 4
        opts = options[:choices]
        if len(opts) < 4:
            continue

        items.append(
            {
                "question": qtext,
                "options": opts,
                "correct": answer_idx,
                "choices": len(opts),
                "category": source,
                "explanation": f"출처: {source}, 페이지 {page_no}",
            }
        )

    return items


def load_cache() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def save_cache(data: dict) -> None:
    CACHE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    ocr = RapidOCR()
    cache = load_cache()
    pdfs = sorted(PDF_DIR.glob("AICA L2 예시문항*.pdf"))
    if not pdfs:
        pdfs = sorted(PDF_DIR.glob("AICA L2*.pdf"))

    all_q: list[dict] = []
    qid = 1

    for pdf in pdfs:
        key = pdf.name
        if key not in cache:
            doc = fitz.open(pdf)
            pages = []
            for pi in range(doc.page_count):
                pages.append(ocr_page(doc[pi], ocr))
            cache[key] = pages
            save_cache(cache)
            print(f"OCR done: {key} ({len(pages)} pages)")

        source = pdf_label(pdf)
        for pi, lines in enumerate(cache[key], start=1):
            parsed = parse_page_lines(lines, source, pi)
            for p in parsed:
                all_q.append(
                    {
                        "id": f"pdf{qid:04d}",
                        "type": "mcq",
                        "choices": p["choices"],
                        "category": p["category"],
                        "question": p["question"],
                        "options": p["options"],
                        "correct": p["correct"],
                        "explanation": p["explanation"],
                    }
                )
                qid += 1

    # 중복 제거 (질문+옵션 동일)
    seen = set()
    unique = []
    for q in all_q:
        sig = (q["question"], tuple(q["options"]))
        if sig in seen:
            continue
        seen.add(sig)
        unique.append(q)

    for i, q in enumerate(unique, 1):
        q["id"] = f"pdf{i:04d}"

    data = {
        "examTitle": "AICA L2 예시문항 전체",
        "description": f"PDF 예시문항 {len(pdfs)}개 파일에서 추출 ({len(unique)}문항). 이미지 PDF OCR 기반 — 오인식 있을 수 있음.",
        "sources": {},
        "questions": unique,
    }
    from collections import Counter

    data["sources"] = dict(Counter(q["category"] for q in unique))

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(unique)} questions → {OUT}")


if __name__ == "__main__":
    main()
