import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line

def create_bilingual_pdf(filename="output.pdf"):
    # 1. Register fonts
    try:
        pdfmetrics.registerFont(TTFont('MSJH', 'C:/Windows/Fonts/msjh.ttc'))
        pdfmetrics.registerFont(TTFont('MSJH-Bold', 'C:/Windows/Fonts/msjhbd.ttc'))
        font_regular = 'MSJH'
        font_bold = 'MSJH-Bold'
    except Exception as e:
        print(f"Error registering MSJH fonts: {e}. Falling back to default.")
        font_regular = 'Helvetica'
        font_bold = 'Helvetica-Bold'

    # 2. Setup document
    # Set page margins (0.75 inch / 54 points)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Define custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName=font_regular,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#4B5563'),
        alignment=1,
        spaceAfter=20
    )
    
    unit_title_style = ParagraphStyle(
        'UnitTitle',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=10,
        spaceAfter=10
    )
    
    zh_text_style = ParagraphStyle(
        'ZHText',
        parent=styles['Normal'],
        fontName=font_regular,
        fontSize=10.5,
        leading=16,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=8
    )
    
    en_text_style = ParagraphStyle(
        'ENText',
        parent=styles['Normal'],
        fontName=font_regular,
        fontSize=10,
        leading=14.5,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=4
    )

    footer_style = ParagraphStyle(
        'FooterText',
        parent=styles['Normal'],
        fontName=font_regular,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#9CA3AF'),
        alignment=1
    )

    # Decorative header banner (Drawing)
    header_draw = Drawing(504, 6)
    header_draw.add(Rect(0, 0, 504, 4, fillColor=colors.HexColor('#1E3A8A'), strokeColor=None))
    story.append(header_draw)
    story.append(Spacer(1, 15))

    # Title & Subtitle
    story.append(Paragraph("課程單元雙語摘要", title_style))
    story.append(Paragraph("Bilingual Summary of Course Units", subtitle_style))
    
    # Decorative line
    sep_draw = Drawing(504, 2)
    sep_draw.add(Line(0, 0, 504, 0, strokeColor=colors.HexColor('#E5E7EB'), strokeWidth=1))
    story.append(sep_draw)
    story.append(Spacer(1, 15))

    # Unit 1 Content Block
    u1_title = Paragraph("單元一：經典歌曲學英文 / Unit 1: Songs and Singers", unit_title_style)
    u1_zh = Paragraph("這份教材介紹了五首經典英文歌曲，包括歌詞、背景故事及相關影片連結，以輕鬆愉快的方式引導學生學習英文。", zh_text_style)
    u1_en = Paragraph("This unit guides students in learning English in a relaxing and pleasant way by introducing five classic English songs, including their lyrics, background stories, and video links.", en_text_style)
    
    # Pack into a single cell table with a light gray background and left accent bar
    u1_cell_content = [
        u1_title,
        Spacer(1, 4),
        Paragraph("<b>中文摘要：</b>", ParagraphStyle('ZhLabel', parent=zh_text_style, fontName=font_bold, textColor=colors.HexColor('#2563EB'))),
        u1_zh,
        Paragraph("<b>English Summary:</b>", ParagraphStyle('EnLabel', parent=en_text_style, fontName=font_bold, textColor=colors.HexColor('#2563EB'))),
        u1_en,
        Spacer(1, 4)
    ]
    
    u1_table = Table([[u1_cell_content]], colWidths=[504])
    u1_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('LINELEFT', (0, 0), (0, -1), 4, colors.HexColor('#2563EB')),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
    ]))
    story.append(u1_table)
    story.append(Spacer(1, 20))

    # Unit 2 Content Block
    u2_title = Paragraph("單元二：福爾摩斯的多重文化與時代改編 / Unit 2: Sherlock Holmes", unit_title_style)
    u2_zh = Paragraph("本單元探討了傳奇偵探夏洛克·福爾摩斯的文學起源，以及他在不同媒介、文化和時代背景下的多樣化角色改編。", zh_text_style)
    u2_en = Paragraph("This unit explores the literary origins of the legendary detective Sherlock Holmes and his diverse character adaptations across different media, cultures, and time periods.", en_text_style)
    
    u2_cell_content = [
        u2_title,
        Spacer(1, 4),
        Paragraph("<b>中文摘要：</b>", ParagraphStyle('ZhLabel2', parent=zh_text_style, fontName=font_bold, textColor=colors.HexColor('#16A34A'))),
        u2_zh,
        Paragraph("<b>English Summary:</b>", ParagraphStyle('EnLabel2', parent=en_text_style, fontName=font_bold, textColor=colors.HexColor('#16A34A'))),
        u2_en,
        Spacer(1, 4)
    ]
    
    u2_table = Table([[u2_cell_content]], colWidths=[504])
    u2_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('LINELEFT', (0, 0), (0, -1), 4, colors.HexColor('#16A34A')),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
    ]))
    story.append(u2_table)
    story.append(Spacer(1, 40))
    
    # Footer area
    footer_draw = Drawing(504, 20)
    footer_draw.add(Line(0, 15, 504, 15, strokeColor=colors.HexColor('#E5E7EB'), strokeWidth=0.5))
    story.append(footer_draw)
    
    story.append(Paragraph("由 Antigravity 智慧生成助理製作 • 2026", footer_style))

    # Build PDF
    doc.build(story)
    print(f"Successfully generated bilingual PDF at {filename}")

if __name__ == "__main__":
    create_bilingual_pdf()
