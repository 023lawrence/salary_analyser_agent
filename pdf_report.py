# pdf_report.py
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import textwrap
import re
import os
import logging

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Preformatted,
    ListFlowable,
    ListItem,
)
from reportlab.lib.units import mm

# Font registration imports
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Configure logging for helpful debug info
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- Font registration ----------------------------------------------------
# Place your TTF files in a 'fonts' folder beside this file:
# fonts/DejaVuSans.ttf
# fonts/DejaVuSans-Bold.ttf
# fonts/DejaVuSans-Oblique.ttf
# fonts/DejaVuSans-BoldOblique.ttf
# fonts/DejaVuSansMono.ttf

FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_font_family_registered = False
_mono_registered = False

def _register_fonts():
    global _font_family_registered, _mono_registered
    try:
        # Normal family
        pdfmetrics.registerFont(TTFont("DejaVuSans", os.path.join(FONTS_DIR, "DejaVuSans.ttf")))
        pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")))
        pdfmetrics.registerFont(TTFont("DejaVuSans-Oblique", os.path.join(FONTS_DIR, "DejaVuSans-Oblique.ttf")))
        pdfmetrics.registerFont(TTFont("DejaVuSans-BoldOblique", os.path.join(FONTS_DIR, "DejaVuSans-BoldOblique.ttf")))

        pdfmetrics.registerFontFamily(
            "DejaVuSans",
            normal="DejaVuSans",
            bold="DejaVuSans-Bold",
            italic="DejaVuSans-Oblique",
            boldItalic="DejaVuSans-BoldOblique"
        )
        _font_family_registered = True
        logger.info("Registered DejaVuSans font family.")

    except Exception as e:
        _font_family_registered = False
        logger.warning(f"Could not register DejaVuSans family from {FONTS_DIR}: {e}")

    # Mono font (may not have bold/italic variants; that's okay for monospace blocks)
    try:
        pdfmetrics.registerFont(TTFont("DejaVuSansMono", os.path.join(FONTS_DIR, "DejaVuSansMono.ttf")))
        _mono_registered = True
        logger.info("Registered DejaVuSansMono font.")
    except Exception as e:
        _mono_registered = False
        logger.warning(f"Could not register DejaVuSansMono from {FONTS_DIR}: {e}")

# Attempt registration at import time (safe; internal flags used later)
_register_fonts()

# --- Helpers --------------------------------------------------------------

def _sanitize_text(s: str) -> str:
    """Basic cleanup: remove weird glyphs, normalize whitespace."""
    if not s:
        return ""
    # Remove odd LLM bullet characters and zero-width spaces
    s = s.replace("■", "").replace("\u200b", "")
    # Normalize line endings
    s = re.sub(r"\r\n?", "\n", s)
    # Collapse excessive blank lines
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def _simple_md_to_html(text: str) -> str:
    """
    Convert a few markdown markers to HTML tags safe for ReportLab Paragraph:
    - **bold** -> <b>bold</b>
    - *italic* -> <i>italic</i>
    """
    # Replace bold **text**
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Replace italics *text* (avoid replacing inside bold)
    text = re.sub(r"(?<!<b>)\*(.+?)\*(?!</b>)", r"<i>\1</i>", text)
    # Minimal escaping for angle brackets that could confuse parser
    # (note: ReportLab accepts a subset of HTML-like tags)
    text = text.replace("< ", "&lt; ").replace(" >", " &gt;")
    return text

def _wrap_text(text: str, width: int = 95) -> str:
    """Wrap long lines to avoid horizontal overflow in Preformatted blocks."""
    paragraphs = text.split("\n\n")
    wrapped = []
    for p in paragraphs:
        if "\n" in p or len(p) <= width:
            wrapped.append(p.strip())
        else:
            wrapped.append(textwrap.fill(p.strip(), width=width))
    return "\n\n".join(wrapped)

def _markdown_to_flowables(md: str, styles):
    """
    Convert a markdown-like string into a list of ReportLab flowables.
    Supports:
      - '#', '##', '###' headings
      - bullet lists starting with '- '
      - paragraphs with **bold** and *italic*
    """
    md = _sanitize_text(md)
    lines = md.splitlines()
    flowables = []
    bullets = []

    def flush_bullets():
        nonlocal bullets
        if not bullets:
            return
        items = [ListItem(Paragraph(_simple_md_to_html(b), styles["Normal"]), leftIndent=6) for b in bullets]
        flowables.append(ListFlowable(items, bulletType="bullet", start=None, leftIndent=12))
        flowables.append(Spacer(1, 6))
        bullets = []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            flush_bullets()
            i += 1
            continue

        if line.startswith("### "):
            flush_bullets()
            flowables.append(Paragraph(_simple_md_to_html(line[4:]), styles["Heading3Custom"]))
            flowables.append(Spacer(1, 6))
        elif line.startswith("## "):
            flush_bullets()
            flowables.append(Paragraph(_simple_md_to_html(line[3:]), styles["Heading2Custom"]))
            flowables.append(Spacer(1, 6))
        elif line.startswith("# "):
            flush_bullets()
            flowables.append(Paragraph(_simple_md_to_html(line[2:]), styles["Heading1Custom"]))
            flowables.append(Spacer(1, 8))
        elif line.lstrip().startswith("- "):
            bullets.append(line.lstrip()[2:].strip())
        else:
            flush_bullets()
            para_lines = [line]
            j = i + 1
            while j < len(lines) and lines[j].strip() and not lines[j].startswith(("### ", "## ", "# ", "- ")):
                para_lines.append(lines[j])
                j += 1
            para_text = " ".join([ln.strip() for ln in para_lines])
            flowables.append(Paragraph(_simple_md_to_html(para_text), styles["Normal"]))
            flowables.append(Spacer(1, 6))
            i = j - 1
        i += 1

    flush_bullets()
    return flowables

# --- Main PDF builder -----------------------------------------------------

def generate_pdf_report(confirmed_data: dict, final_report: str, payslip_text: str | None,
                        country: str, tax_year: str, title: str = "Salary Analyzer & Tax Opportunity Report") -> bytes:
    """
    Build a readable PDF bytes object containing: header, payslip, parsed JSON and AI report.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=18*mm, bottomMargin=18*mm)

    styles = getSampleStyleSheet()

    # Apply Unicode font family if registered; otherwise keep defaults but avoid using <b> tags in header
    if _font_family_registered:
        try:
            styles["Normal"].fontName = "DejaVuSans"
        except Exception:
            pass

    # Heading and monospace styles
    styles.add(ParagraphStyle(
        name="Heading1Custom",
        parent=styles["Heading1"],
        fontSize=14,
        leading=16,
        spaceAfter=6,
        fontName="DejaVuSans" if _font_family_registered else styles["Heading1"].fontName
    ))
    styles.add(ParagraphStyle(
        name="Heading2Custom",
        parent=styles["Heading2"],
        fontSize=12,
        leading=14,
        spaceAfter=4,
        fontName="DejaVuSans" if _font_family_registered else styles["Heading2"].fontName
    ))
    styles.add(ParagraphStyle(
        name="Heading3Custom",
        parent=styles["Heading3"],
        fontSize=11,
        leading=13,
        spaceAfter=3,
        fontName="DejaVuSans" if _font_family_registered else styles["Heading3"].fontName
    ))

    mono_font_name = "DejaVuSansMono" if _mono_registered else (styles["Code"].fontName if "Code" in styles else None)
    styles.add(ParagraphStyle(
        name="Monospace",
        parent=styles.get("Code", styles["Normal"]),
        fontName=mono_font_name,
        fontSize=9,
        leading=12
    ))

    flowables = []

    # Header / metadata
    try:
        tz = ZoneInfo("Asia/Kolkata")
        timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # If font family is registered, it's safe to use <b> (ReportLab will map to bold TTF).
    # Otherwise, use plain text header to avoid mapping errors.
    if _font_family_registered:
        header_text = f"<b>{title}</b><br/>{country} \u2014 {tax_year} <br/>Generated: {timestamp}"
    else:
        header_text = f"{title}\n{country} — {tax_year}\nGenerated: {timestamp}"

    flowables.append(Paragraph(header_text, styles["Heading1Custom"]))
    flowables.append(Spacer(1, 6))

    # Original Payslip (if present)
    if payslip_text:
        flowables.append(Paragraph("Original Payslip Text (as pasted):", styles["Heading2Custom"]))
        sanitized = _sanitize_text(payslip_text)
        wrapped = _wrap_text(sanitized, width=95)
        # Use Preformatted to preserve basic structure but wrapped to avoid cutoff
        flowables.append(Preformatted(wrapped, styles["Monospace"]))
        flowables.append(Spacer(1, 8))

    # Confirmed Parsed JSON
    flowables.append(Paragraph("Parsed / Confirmed Monthly Data (JSON):", styles["Heading2Custom"]))
    pretty_json = json.dumps(confirmed_data or {}, indent=2, ensure_ascii=False)
    wrapped_json = _wrap_text(pretty_json, width=95)
    flowables.append(Preformatted(wrapped_json, styles["Monospace"]))
    flowables.append(Spacer(1, 8))

    # AI Report - convert markdown-like to flowables
    flowables.append(Paragraph("AI Analysis Report:", styles["Heading2Custom"]))
    sanitized_report = _sanitize_text(final_report or "")
    sanitized_report = re.sub(r"\n{3,}", "\n\n", sanitized_report)
    md_flowables = _markdown_to_flowables(sanitized_report, styles)
    flowables.extend(md_flowables)
    flowables.append(Spacer(1, 8))

    # AI disclaimer
    disclaimer = (
        "Disclaimer: This report was automatically generated by an AI agent for informational and educational "
        "purposes only. It does not constitute professional tax, legal, or financial advice. "
        "Please consult a qualified tax or financial professional before making any decisions based on this report."
    )
    flowables.append(Paragraph(disclaimer, ParagraphStyle(
        name="Disclaimer",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        italic=True,
        textColor="#333333",
        fontName="DejaVuSans" if _font_family_registered else styles["Normal"].fontName
    )))
    flowables.append(Spacer(1, 4))

    # Build PDF
    doc.build(flowables)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
