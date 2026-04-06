from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime

def export_chat_to_pdf(filename, session_title, subject, messages, notes=None):
    """Export chat conversation to PDF"""
    doc = SimpleDocTemplate(filename, pagesize=letter,
                          rightMargin=0.5*inch, leftMargin=0.5*inch,
                          topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1976d2'),
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph(f"📚 {session_title}", title_style))
    
    # Subject and Date
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20
    )
    story.append(Paragraph(f"<b>Subject:</b> {subject if subject else 'General'}", info_style))
    story.append(Paragraph(f"<b>Exported:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", info_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Messages
    story.append(Paragraph("<b>Conversation</b>", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    msg_style = ParagraphStyle(
        'Message',
        parent=styles['Normal'],
        fontSize=10,
        leftMargin=20,
        spaceAfter=12
    )
    
    for msg in messages:
        if msg['role'] == 'user':
            text = f"<b>You:</b> {msg['content']}"
            color = colors.HexColor('#f5f5f5')
        else:
            text = f"<b>Teacher:</b> {msg['content']}"
            color = colors.HexColor('#e3f2fd')
        
        story.append(Paragraph(text, msg_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Notes section
    if notes:
        story.append(PageBreak())
        story.append(Paragraph("<b>📝 Notes</b>", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        for note in notes:
            story.append(Paragraph(f"• {note[1]}", msg_style))
            story.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(story)
    return filename
