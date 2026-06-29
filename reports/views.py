from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
import datetime
from dashboard.models import MedicineReminder

@login_required
def generate_report(request):
    user = request.user
    
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1))
    
    Story = []

    # Title
    title = Paragraph("<b>Prana AI Health Report</b>", styles['Title'])
    Story.append(title)
    
    # Date
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    date_p = Paragraph(f"<i>Date: {date_str}</i>", styles['Normal'])
    Story.append(date_p)
    Story.append(Spacer(1, 24))
    
    # Patient Info section
    Story.append(Paragraph("<b>Patient Information</b>", styles['Heading2']))
    Story.append(Spacer(1, 12))
    
    patient_info = [
        ["Name:", f"{user.first_name} {user.last_name}" if user.first_name else user.username],
        ["Email:", user.email],
        ["Phone:", getattr(user, 'phone_number', 'N/A')],
        ["DOB:", str(getattr(user, 'date_of_birth', 'N/A'))],
        ["Blood Group:", getattr(user, 'blood_group', 'N/A')],
        ["Address:", getattr(user, 'address', 'N/A')]
    ]
    
    info_table = Table(patient_info, colWidths=[100, 300])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    Story.append(info_table)
    Story.append(Spacer(1, 24))
    
    # Medication Section
    Story.append(Paragraph("<b>Current Medications (Reminders)</b>", styles['Heading2']))
    Story.append(Spacer(1, 12))
    
    reminders = MedicineReminder.objects.filter(user=user, is_active=True)
    
    if reminders.exists():
        med_data = [["Medicine", "Dosage", "Frequency", "Time"]]
        for rm in reminders:
            med_data.append([
                rm.medicine_name,
                rm.dosage,
                rm.frequency,
                rm.time.strftime("%I:%M %p")
            ])
            
        med_table = Table(med_data, colWidths=[120, 100, 100, 80])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.teal),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        Story.append(med_table)
    else:
        Story.append(Paragraph("No active medications found.", styles['Normal']))

    Story.append(Spacer(1, 48))
    Story.append(Paragraph("<i>This is a generated report from Prana AI. Consult your doctor for medical advice.</i>", styles['Italic']))

    def draw_bg(canvas, doc):
        canvas.saveState()
        # Draw Watermark
        canvas.setFont('Helvetica-Bold', 80)
        canvas.setFillGray(0.90)
        canvas.translate(letter[0]/2, letter[1]/2)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "Prana AI")
        canvas.restoreState()

        canvas.saveState()
        # Draw Border
        canvas.setStrokeColor(colors.teal)
        canvas.setLineWidth(3)
        margin = 36
        width = letter[0] - 2 * margin
        height = letter[1] - 2 * margin
        canvas.rect(margin, margin, width, height)
        canvas.restoreState()

    # Build the PDF
    doc.build(Story, onFirstPage=draw_bg, onLaterPages=draw_bg)
    
    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    filename = f"Health_Report_{user.username}_{datetime.date.today()}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)
    
    return response
