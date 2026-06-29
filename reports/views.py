from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import datetime
import os
from django.conf import settings
from dashboard.models import MedicineReminder

# Custom Colors matching the new Prana AI Theme
PRIMARY = HexColor('#14B8A6')
SECONDARY = HexColor('#0D9488')
DARK = HexColor('#115E59')
LIGHT = HexColor('#F0FDFA')
TEXT = HexColor('#334155')
MUTED = HexColor('#64748B')
WHITE = HexColor('#FFFFFF')
BORDER = HexColor('#E2E8F0')
LIGHT_TRANS = colors.Color(240/255.0, 253/255.0, 250/255.0, alpha=0.7)
WHITE_TRANS = colors.Color(1, 1, 1, alpha=0.7)

class LineDraw(Flowable):
    """Draws a horizontal line across the page."""
    def __init__(self, width, color=BORDER):
        Flowable.__init__(self)
        self.width = width
        self.color = color

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(1)
        self.canv.line(0, 0, self.width, 0)

@login_required
def generate_report(request):
    user = request.user
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    
    # Custom Premium Styles
    styles.add(ParagraphStyle(name='TitlePremium', fontName='Helvetica-Bold', fontSize=24, textColor=DARK, leading=28))
    styles.add(ParagraphStyle(name='HeadingPremium', fontName='Helvetica-Bold', fontSize=14, textColor=PRIMARY, spaceAfter=12, spaceBefore=24))
    styles.add(ParagraphStyle(name='NormalPremium', fontName='Helvetica', fontSize=10, textColor=TEXT, leading=14))
    styles.add(ParagraphStyle(name='FooterPremium', fontName='Helvetica-Oblique', fontSize=9, textColor=MUTED, alignment=1))
    
    Story = []

    # --- Header ---
    header_data = []
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    
    title_p = Paragraph("<b>Prana AI</b><br/><font size='12' color='#64748B'>Intelligent Health Report</font>", styles['TitlePremium'])
    
    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=50, height=50)
            header_data.append([logo, title_p])
        except Exception:
            header_data.append(["", title_p])
    else:
        header_data.append(["", title_p])
        
    header_table = Table(header_data, colWidths=[60, 400])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'LEFT'),
    ]))
    Story.append(header_table)
    Story.append(Spacer(1, 15))
    Story.append(LineDraw(width=doc.width, color=PRIMARY))
    Story.append(Spacer(1, 15))
    
    # --- Report Meta ---
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    Story.append(Paragraph(f"<b>Report Date:</b> {date_str}", styles['NormalPremium']))
    
    # --- Patient Profile ---
    Story.append(Paragraph("Patient Profile", styles['HeadingPremium']))
    
    patient_info = [
        ["Full Name", f"{user.first_name} {user.last_name}" if user.first_name else user.username],
        ["Email Address", user.email],
        ["Phone Number", getattr(user, 'phone_number', 'N/A')],
        ["Date of Birth", str(getattr(user, 'date_of_birth', 'N/A'))],
        ["Blood Group", getattr(user, 'blood_group', 'N/A')],
    ]
    
    info_table = Table(patient_info, colWidths=[150, 360])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,-1), MUTED),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('TEXTCOLOR', (1,0), (1,-1), TEXT),
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_TRANS),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, BORDER),
    ]))
    Story.append(info_table)
    
    # --- Medications ---
    Story.append(Paragraph("Active Prescriptions & Reminders", styles['HeadingPremium']))
    
    reminders = MedicineReminder.objects.filter(user=user, is_active=True)
    
    if reminders.exists():
        med_data = [["Medicine Name", "Dosage", "Frequency", "Time"]]
        for rm in reminders:
            med_data.append([
                rm.medicine_name,
                rm.dosage,
                rm.frequency,
                rm.time.strftime("%I:%M %p")
            ])
            
        med_table = Table(med_data, colWidths=[160, 110, 140, 100])
        
        # Base table style
        ts = [
            ('BACKGROUND', (0,0), (-1,0), DARK),
            ('TEXTCOLOR', (0,0), (-1,0), WHITE),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('TOPPADDING', (0,0), (-1,0), 12),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('TEXTCOLOR', (0,1), (-1,-1), TEXT),
            ('BOTTOMPADDING', (0,1), (-1,-1), 10),
            ('TOPPADDING', (0,1), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, BORDER),
        ]
        
        # Alternating row colors for glassmorphism/clean feel
        for i in range(1, len(med_data)):
            if i % 2 == 0:
                ts.append(('BACKGROUND', (0, i), (-1, i), LIGHT_TRANS))
            else:
                ts.append(('BACKGROUND', (0, i), (-1, i), WHITE_TRANS))
                
        med_table.setStyle(TableStyle(ts))
        Story.append(med_table)
    else:
        Story.append(Paragraph("No active medications found in your profile.", styles['NormalPremium']))

    # --- Footer ---
    Story.append(Spacer(1, 40))
    Story.append(LineDraw(width=doc.width, color=BORDER))
    Story.append(Spacer(1, 10))
    Story.append(Paragraph("This is an AI-generated health report by Prana AI. Please consult your physician for professional medical advice.", styles['FooterPremium']))

    def draw_bg(canvas, doc):
        canvas.saveState()
        
        # Draw Watermark Logo
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
        watermark_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_watermark.png')
        
        if os.path.exists(logo_path):
            try:
                if not os.path.exists(watermark_path):
                    from PIL import Image as PILImage
                    img = PILImage.open(logo_path).convert("RGBA")
                    data = img.getdata()
                    new_data = []
                    for item in data:
                        # Blend with white (85% white, 15% original) for a visible but soft watermark
                        r = int(item[0] * 0.15 + 255 * 0.85)
                        g = int(item[1] * 0.15 + 255 * 0.85)
                        b = int(item[2] * 0.15 + 255 * 0.85)
                        new_data.append((r, g, b, 255))
                    img.putdata(new_data)
                    img.save(watermark_path, "PNG")
                
                w, h = 450, 450
                x = (letter[0] - w) / 2
                y = (letter[1] - h) / 2
                canvas.drawImage(watermark_path, x, y, width=w, height=h, mask=None)
            except Exception as e:
                pass
        
        # Premium Border accents (Top & Bottom teal strips)
        canvas.setStrokeColor(PRIMARY)
        canvas.setLineWidth(6)
        canvas.line(0, letter[1], letter[0], letter[1])
        
        canvas.setStrokeColor(SECONDARY)
        canvas.setLineWidth(10)
        canvas.line(0, 0, letter[0], 0)
        
        canvas.restoreState()

    # Build the PDF
    doc.build(Story, onFirstPage=draw_bg, onLaterPages=draw_bg)
    
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    filename = f"PranaAI_Health_Report_{user.username}_{datetime.date.today()}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)
    
    return response
