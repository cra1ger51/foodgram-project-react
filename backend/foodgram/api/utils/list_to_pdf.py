import io

from django.http import FileResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def list_to_pdf(data):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    pdfmetrics.registerFont(TTFont('Arial', './arial.ttf'))
    p.setFont("Arial", 20)
    p.drawString(250, 800, "Список покупок:")
    height = 760
    for i, (name, data) in enumerate(data.items(), 1):
        p.drawString(100, height, (f'{i}) {name} - {data["amount"]}, '
                                   f'{data["measurement_unit"]}'))
        height -= 25
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True,
                        filename="Shopping_list.pdf")
