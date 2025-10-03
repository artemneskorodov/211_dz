from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color
import io
import sys
from pathlib import Path

def create_overlay(watermark_text,
                   link_text,
                   url,
                   pagesize):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=pagesize)
    width, height = pagesize

    # Watermark
    c.setFont("PlayFont", 300)
    c.setFillColor(Color(0, 0, 0, alpha=0.2))
    c.saveState()
    c.translate(width / 2, height / 2)
    c.drawCentredString(0, 0, watermark_text)
    c.restoreState()

    # Donation link
    c.setFont("PlayFont", 30)
    c.setFillColor(Color(0, 0, 1, alpha=0.2))
    link_y = 30  # отступ от низа
    link_x = width / 2

    # Drawing text
    c.drawCentredString(link_x, link_y, link_text)

    # Adding ling
    text_width = c.stringWidth(link_text, "PlayFont", 30)
    left = link_x - text_width / 2 - 2
    right = link_x + text_width / 2 + 2
    bottom = link_y - 2
    top = link_y + 20

    c.linkURL(url, (left, bottom, right, top), relative=1)

    c.save()
    packet.seek(0)
    return packet

def add_watermark_and_link_to_pdf(input_path,
                                  output_path,
                                  watermark_text,
                                  link_text,
                                  url):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        # Определяем размер текущей страницы
        mb = page.get('/MediaBox', [0, 0, 612, 792])  # default = letter
        width    = float(mb[2])
        height   = float(mb[3])
        pagesize = (width, height)

        # Creating overlay
        overlay_pdf = create_overlay(
            watermark_text,
            link_text,
            url,
            pagesize)
        overlay_reader = PdfReader(overlay_pdf)
        overlay_page = overlay_reader.pages[0]

        # Накладываем поверх исходной страницы
        page.merge_page(overlay_page)
        writer.add_page(page)

    with open(output_path, "wb") as out_file:
        writer.write(out_file)

# === Пример использования ===
if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise RuntimeError("Unexpected amount of parameters")

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    base_dir = Path(__file__).parent

    pdfmetrics.registerFont(TTFont("PlayFont", base_dir / "font/Play-Bold.ttf"))

    add_watermark_and_link_to_pdf(
        input_path,
        output_path,
        "211",
        "Донатик",
        "https://www.donationalerts.com/r/phystech_211")
