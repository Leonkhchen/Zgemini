import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Force UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Register Kaiu (標楷體) and Microsoft JhengHei
font_kaiu = r"C:\Windows\Fonts\kaiu.ttf"
font_msjh = r"C:\Windows\Fonts\msjh.ttc"

pdfmetrics.registerFont(TTFont("Kaiu", font_kaiu))
pdfmetrics.registerFont(TTFont("MSJH", font_msjh))

def create_exam_pdf(output_path, is_solution=False):
    """
    Generates a professional 2-page A4 exam paper.
    Page 1: 填充題 (56%)
    Page 2: 計算題 (44%)
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )
    
    usable_width = A4[0] - 30 * mm  # ~180mm
    story = []
    
    # Styles
    title_style = ParagraphStyle(
        'ExamTitle',
        fontName='Kaiu',
        fontSize=17,
        leading=22,
        alignment=1, # Center
        textColor=colors.black
    )
    
    sub_title_style = ParagraphStyle(
        'ExamSubTitle',
        fontName='Kaiu',
        fontSize=11,
        leading=15,
        alignment=1,
        textColor=colors.HexColor('#222222')
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        fontName='Kaiu',
        fontSize=12,
        leading=16,
        fontStyle='BOLD',
        textColor=colors.black,
        spaceBefore=4,
        spaceAfter=4
    )
    
    q_style = ParagraphStyle(
        'QuestionText',
        fontName='Kaiu',
        fontSize=10.5,
        leading=15,
        textColor=colors.black
    )
    
    sol_style = ParagraphStyle(
        'SolutionText',
        fontName='MSJH',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#990000')
    )

    # -------------------------------------------------------------
    # HEADER SECTION
    # -------------------------------------------------------------
    title_text = "國一數學測驗卷：整數的加減法、乘除法"
    if is_solution:
        title_text += "【教師詳解與評分卷】"
        
    story.append(Paragraph("<b>臺師補習班</b> <font size=9>（孩子的一步 臺師細心呵護）</font>", sub_title_style))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(f"<b>{title_text}</b>", title_style))
    story.append(Spacer(1, 2.5 * mm))
    
    # Header Info Table (學府/日期/班級/姓名/得分)
    if not is_solution:
        header_data = [
            [
                Paragraph("<b>學府 / 班別：</b>＿＿＿＿＿＿", q_style),
                Paragraph("<b>測驗日期：</b> 2026 年 ___ 月 ___ 日", q_style),
                Paragraph("<b>姓名：</b>＿＿＿＿＿＿", q_style),
                Paragraph("<b>得分：</b>", q_style)
            ]
        ]
        score_box_style = [
            ('BOX', (0,0), (-1,-1), 0.8, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BACKGROUND', (3,0), (3,0), colors.HexColor('#F8F8F8'))
        ]
    else:
        header_data = [
            [
                Paragraph("<b>學府：</b> 國中部", q_style),
                Paragraph("<b>範圍：</b> 國一上 第一章 整數運算", q_style),
                Paragraph("<b>總分：</b> 100 分（填充 56 分 + 計算 44 分）", q_style),
                Paragraph("<b>版本：</b> 標準解答", q_style)
            ]
        ]
        score_box_style = [
            ('BOX', (0,0), (-1,-1), 0.8, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFF3F3'))
        ]
        
    t_header = Table(header_data, colWidths=[45*mm, 52*mm, 45*mm, 38*mm])
    t_header.setStyle(TableStyle(score_box_style))
    story.append(t_header)
    story.append(Spacer(1, 3.5 * mm))

    # -------------------------------------------------------------
    # SECTION 1: 填充題 (56%)
    # -------------------------------------------------------------
    story.append(Paragraph("<b>一、填充題：（每格 4 分，共 56 分）</b>", section_style))
    
    # 1. 計算下列各式的值
    q1_header = Paragraph("<b>1. 計算下列各式的值：</b>", q_style)
    story.append(q1_header)
    
    q1_sub = [
        ("(1) 36 ÷ (-3) = ", "-12" if is_solution else ""),
        ("(2) (-5) × [6 × (-12)] = ", "360" if is_solution else ""),
        ("(3) [19 × (-25)] × 4 = ", "-1900" if is_solution else ""),
        ("(4) (-54) ÷ 6 ÷ (-3) = ", "3" if is_solution else ""),
        ("(5) 96 ÷ [(-8) ÷ (-2)] = ", "24" if is_solution else ""),
        ("(6) (-18) ÷ [(-3) × 6] = ", "1" if is_solution else "")
    ]
    
    q1_table_data = []
    for i in range(0, 6, 2):
        left_txt = f"{q1_sub[i][0]} 【 <b>{q1_sub[i][1]}</b> 】"
        right_txt = f"{q1_sub[i+1][0]} 【 <b>{q1_sub[i+1][1]}</b> 】"
        q1_table_data.append([
            Paragraph(left_txt, q_style),
            Paragraph(right_txt, q_style)
        ])
        
    t_q1 = Table(q1_table_data, colWidths=[usable_width/2.0, usable_width/2.0])
    t_q1.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_q1)
    story.append(Spacer(1, 2 * mm))
    
    # 2. 請填入 > 或 = 或 <
    q2_header = Paragraph("<b>2. 請填入 ＞ 或 ＝ 或 ＜ ：</b>", q_style)
    story.append(q2_header)
    
    q2_ans1 = "=" if is_solution else "　"
    q2_ans2 = "<" if is_solution else "　"
    q2_data = [
        [
            Paragraph(f"(1) (-54) ÷ (-6) ÷ (-7) &nbsp;【 <b>{q2_ans1}</b> 】&nbsp; (-54) ÷ [(-6) × (-7)]", q_style),
        ],
        [
            Paragraph(f"(2) (-720) ÷ (-8) × (-2) &nbsp;【 <b>{q2_ans2}</b> 】&nbsp; (-720) ÷ [(-8) × (-2)]", q_style),
        ]
    ]
    t_q2 = Table(q2_data, colWidths=[usable_width])
    t_q2.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_q2)
    story.append(Spacer(1, 2 * mm))

    # 3. 數線題
    q3_ans1 = "28" if is_solution else "　"
    q3_ans2 = "3" if is_solution else "　"
    q3_header = Paragraph("<b>3. 數線上有 A(-3)、B(9)、C(11)、D(-5) 四點，求：</b>", q_style)
    story.append(q3_header)
    q3_data = [
        [
            Paragraph(f"(1) <u>AC</u> + <u>BD</u> = 【 <b>{q3_ans1}</b> 】。", q_style),
            Paragraph(f"(2) C、D 的中點坐標為 【 <b>{q3_ans2}</b> 】。", q_style)
        ]
    ]
    t_q3 = Table(q3_data, colWidths=[usable_width/2.0, usable_width/2.0])
    t_q3.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_q3)
    story.append(Spacer(1, 2 * mm))

    # 4. 如果 a 是比 -8 大 5 的數...
    q4_ans = "57" if is_solution else "　"
    q4_text = f"<b>4.</b> 如果 <i>a</i> 是比 -8 大 5 的數，<i>b</i> 是比 -14 小 5 的數，那麼 <i>a</i> × <i>b</i> = 【 <b>{q4_ans}</b> 】。"
    story.append(Paragraph(q4_text, q_style))
    if is_solution:
        story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;[解析] a = -8 + 5 = -3，b = -14 - 5 = -19，a × b = (-3) × (-19) = 57。", sol_style))
    story.append(Spacer(1, 2 * mm))

    # 5. 欲使「32÷4-8□(-2)=12」成立...
    q5_ans = "÷" if is_solution else "　"
    q5_text = f"<b>5.</b> 欲使「32 ÷ 4 - 8 □ (-2) = 12」成立，則 □ 應填入哪一個運算符號？【 <b>{q5_ans}</b> 】"
    story.append(Paragraph(q5_text, q_style))
    if is_solution:
        story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;[解析] 8 - 8 □ (-2) = 12 ⇒ 8 □ (-2) = -4 ⇒ □ 填入 ÷ (除號)。", sol_style))
    story.append(Spacer(1, 2 * mm))

    # 6. 甲乙丙丁正負號判定
    q6_ans_pos = "乙、丙" if is_solution else "　　"
    q6_ans_neg = "丁" if is_solution else "　"
    q6_text = (
        "<b>6.</b> 已知：<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;甲數 = 33 × 999 × 55 × 0 × 5<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;乙數 = [(-23) × (-99)] × (-35) ÷ (-5)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;丙數 = 15625 ÷ (-25) ÷ (-15)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;丁數 = (-1525) ÷ (-12) × 18 ÷ (-20)<br/>"
        f"&nbsp;&nbsp;&nbsp;&nbsp;上列各數中，計算結果為<b>正數</b>的是【 <b>{q6_ans_pos}</b> 】，為<b>負數</b>的是【 <b>{q6_ans_neg}</b> 】。"
    )
    story.append(Paragraph(q6_text, q_style))
    if is_solution:
        story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;[解析] 甲=0(非正非負)；乙有4個負號為正；丙有2個負號為正；丁有3個負號為負。", sol_style))
        
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.black, spaceBefore=2, spaceAfter=2))
    story.append(Paragraph("<font size=8 color='#666666'>（第 1 頁，請翻面繼續作答）</font>", sub_title_style))

    # -------------------------------------------------------------
    # PAGE BREAK -> PAGE 2: 計算題 (44%)
    # -------------------------------------------------------------
    story.append(PageBreak())
    
    # Page 2 Header
    story.append(Paragraph(f"<b>{title_text}（第 2 頁）</b>", title_style))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("<b>二、計算題：（每題 4 分，共 44 分）</b> <i>※請寫出完整的計算過程與最後答案</i>", section_style))
    story.append(Spacer(1, 1.5 * mm))

    calc_questions = [
        (1, "(-2 - 3) - (-5 - 8) = ?", 
         "原式 = (-5) - (-13)\n= -5 + 13\n= 8", "8"),
         
        (2, "267 - 456 - (-33) + 156 = ?", 
         "原式 = 267 + 33 + 156 - 456\n= 456 - 456\n= 0", "0"),
         
        (3, "(-36) + 49 - (-15) - 61 = ?", 
         "原式 = -36 + 49 + 15 - 61\n= (49 + 15) - (36 + 61)\n= 64 - 97 = -33", "-33"),
         
        (4, "-15 - 95 - 995 - 9995 = ?", 
         "原式 = -(15 + 95 + 995 + 9995)\n= -(20-5 + 100-5 + 1000-5 + 10000-5)\n= -(11120 - 20) = -11100", "-11100"),
         
        (5, "(-6) × 7 + (-8) × (-5) = ?", 
         "原式 = (-42) + 40\n= -2", "-2"),
         
        (6, "4 × (-15) - (-21) ÷ 3 = ?", 
         "原式 = (-60) - (-7)\n= -60 + 7\n= -53", "-53"),
         
        (7, "(-7) × (-4) + (12 - 18) ÷ 3 = ?", 
         "原式 = 28 + (-6) ÷ 3\n= 28 + (-2)\n= 26", "26"),
         
        (8, "(-12) + 3 × [(-5) - (-3)] = ?", 
         "原式 = (-12) + 3 × [-5 + 3]\n= (-12) + 3 × (-2)\n= -12 - 6 = -18", "-18"),
         
        (9, "[24 - 2 × (-3)] ÷ 3 - (-3) = ?", 
         "原式 = [24 - (-6)] ÷ 3 + 3\n= [24 + 6] ÷ 3 + 3\n= 30 ÷ 3 + 3 = 10 + 3 = 13", "13"),
         
        (10, "26 ÷ [28 ÷ 7 - (-3) × 3] + 7 = ?", 
         "原式 = 26 ÷ [4 - (-9)] + 7\n= 26 ÷ [4 + 9] + 7\n= 26 ÷ 13 + 7 = 2 + 7 = 9", "9"),
         
        (11, "9 + (-2) × [18 - (-5) × 3] ÷ 3 = ?", 
         "原式 = 9 + (-2) × [18 - (-15)] ÷ 3\n= 9 + (-2) × [18 + 15] ÷ 3\n= 9 + (-2) × 33 ÷ 3\n= 9 + (-2) × 11 = 9 - 22 = -13", "-13")
    ]

    calc_table_rows = []
    # Display in 2-column layout (Left: Q1,3,5,7,9,11; Right: Q2,4,6,8,10)
    # Total 6 rows
    for r in range(6):
        left_idx = r * 2
        right_idx = r * 2 + 1
        
        # Left item
        if left_idx < len(calc_questions):
            q_num, q_stmt, q_steps, q_ans = calc_questions[left_idx]
            if not is_solution:
                left_cell = [
                    Paragraph(f"<b>{q_num}.</b> {q_stmt}", q_style),
                    Spacer(1, 16 * mm), # Space for student handwriting
                    Paragraph("<font color='#888888'>答：＿＿＿＿＿＿</font>", q_style)
                ]
            else:
                steps_formatted = q_steps.replace('\n', '<br/>')
                left_cell = [
                    Paragraph(f"<b>{q_num}.</b> {q_stmt}", q_style),
                    Spacer(1, 1 * mm),
                    Paragraph(f"<font color='#004488'><b>【計算過程】</b><br/>{steps_formatted}</font>", sol_style),
                    Paragraph(f"<b>答：<font color='#CC0000'>{q_ans}</font></b>", q_style)
                ]
        else:
            left_cell = [Paragraph("", q_style)]
            
        # Right item
        if right_idx < len(calc_questions):
            q_num, q_stmt, q_steps, q_ans = calc_questions[right_idx]
            if not is_solution:
                right_cell = [
                    Paragraph(f"<b>{q_num}.</b> {q_stmt}", q_style),
                    Spacer(1, 16 * mm),
                    Paragraph("<font color='#888888'>答：＿＿＿＿＿＿</font>", q_style)
                ]
            else:
                steps_formatted = q_steps.replace('\n', '<br/>')
                right_cell = [
                    Paragraph(f"<b>{q_num}.</b> {q_stmt}", q_style),
                    Spacer(1, 1 * mm),
                    Paragraph(f"<font color='#004488'><b>【計算過程】</b><br/>{steps_formatted}</font>", sol_style),
                    Paragraph(f"<b>答：<font color='#CC0000'>{q_ans}</font></b>", q_style)
                ]
        else:
            right_cell = [Paragraph("", q_style)]
            
        calc_table_rows.append([left_cell, right_cell])
        
    t_calc = Table(calc_table_rows, colWidths=[usable_width/2.0, usable_width/2.0])
    t_calc.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.8, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_calc)
    
    # Build Document
    doc.build(story)
    print(f"Generated PDF: {output_path}")

if __name__ == '__main__':
    exam_dir = r"C:\Zgemini\exam"
    out_dir = os.path.join(exam_dir, "重新排版_乾淨試卷")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Generate Blank Exam for Student Retesting
    student_pdf = os.path.join(out_dir, "國一數學_整數四則運算_空白重測試卷.pdf")
    create_exam_pdf(student_pdf, is_solution=False)
    
    # 2. Generate Teacher Solution Key
    teacher_pdf = os.path.join(out_dir, "國一數學_整數四則運算_教師詳解卷.pdf")
    create_exam_pdf(teacher_pdf, is_solution=True)
    
    # Also copy student pdf to exam root for convenience
    root_student_pdf = os.path.join(exam_dir, "國一數學_整數四則運算_空白重測試卷.pdf")
    create_exam_pdf(root_student_pdf, is_solution=False)
    
    print("\n==========================================")
    print("SUCCESS: 試卷已完成智慧理解、公式校準與標準考卷排版！")
    print(f"學生空白重測試卷: {student_pdf}")
    print(f"教師完整詳解卷: {teacher_pdf}")
    print("==========================================")
