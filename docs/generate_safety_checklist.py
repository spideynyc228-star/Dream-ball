"""Generate the downloadable Dream Ball student safety checklist."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "Digital_Safety_Checklist.pdf"


def checklist_row(text, style):
    return [Paragraph("[ ]", style), Paragraph(text, style)]


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=22 * mm, leftMargin=22 * mm, topMargin=20 * mm, bottomMargin=18 * mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=29, leading=34, textColor=colors.HexColor("#172143"), spaceAfter=7)
    subtitle = ParagraphStyle("subtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=10, leading=15, textColor=colors.HexColor("#65708B"), spaceAfter=18)
    heading = ParagraphStyle("heading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#493B75"), spaceBefore=12, spaceAfter=7)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontName="Helvetica", fontSize=10, leading=15, textColor=colors.HexColor("#35415E"))
    small = ParagraphStyle("small", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#66728D"))
    story = [Paragraph("DREAM BALL", ParagraphStyle("brand", parent=small, fontName="Helvetica-Bold", textColor=colors.HexColor("#A47C3C"), tracking=1.5, spaceAfter=8)), Paragraph("Student Safety Checklist", title), Paragraph("A calm, practical guide for preparing for an official school event with respect, privacy and care for one another.", subtitle)]
    sections = [
        ("Before you send a partnership request", ["I have read the student profile carefully and will write a respectful, pressure-free request.", "I understand that a classmate can decline or take time to respond, and I will respect that decision.", "I will keep messages focused on Dream Ball preparation and school-event planning."]),
        ("Before a rehearsal or meeting", ["We have agreed on a familiar, appropriate location and a clear time to meet.", "A parent, guardian or trusted adult knows the plan when appropriate.", "I know how I will arrive, return home and contact someone if plans change."]),
        ("Privacy and digital respect", ["I will not share another student's profile, photo or personal information without permission.", "I will not ask for information that is unrelated to the event or preparation.", "I will use the report tool or speak to a teacher if something feels uncomfortable or unsafe."]),
        ("On the event day", ["I know the event arrival time, venue and school contact information.", "I will follow event rules and help make every classmate feel welcome.", "I will check in with a trusted adult if I need support at any point."]),
    ]
    for heading_text, items in sections:
        story.append(Paragraph(heading_text, heading))
        table = Table([checklist_row(item, body) for item in items], colWidths=[8 * mm, 156 * mm], hAlign="LEFT")
        table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 2), ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#A47C3C"))]))
        story.append(table)
    story += [Spacer(1, 10), Table([[Paragraph("Need support?", ParagraphStyle("callout-title", parent=body, fontName="Helvetica-Bold", textColor=colors.HexColor("#1F2D62"))), Paragraph("Use Dream Ball's report feature or speak with a trusted teacher, school counsellor, parent or guardian.", body)]], colWidths=[38 * mm, 126 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2F0F8")), ("BOX", (0, 0), (-1, -1), .5, colors.HexColor("#DED9EA")), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10), ("VALIGN", (0, 0), (-1, -1), "TOP")]))]
    document.build(story)


if __name__ == "__main__":
    build()
