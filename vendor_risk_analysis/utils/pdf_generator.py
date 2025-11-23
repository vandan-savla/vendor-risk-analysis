from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import textwrap
import uuid
import os

def generate_pdf(report_text: str) -> str:
    """
    Takes the AI-generated risk report text and creates a PDF.
    Returns local file path to the PDF.
    """
    file_name = f"vendor_risk_report_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join("generated_reports", file_name)

    os.makedirs("generated_reports", exist_ok=True)

    c = canvas.Canvas(file_path, pagesize=LETTER)
    width, height = LETTER

    # Margins
    x_margin = 50
    y = height - 50

    # Wrap text
    wrapped_lines = []
    for paragraph in report_text.split("\n"):
        lines = textwrap.wrap(paragraph, width=95)
        wrapped_lines.extend(lines if lines else [""])

    # Write to PDF
    for line in wrapped_lines:
        if y < 50:  # new page
            c.showPage()
            y = height - 50

        c.drawString(x_margin, y, line)
        y -= 15

    c.save()
    return file_path
