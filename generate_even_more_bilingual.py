import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, Line

# 1. Register fonts
try:
    pdfmetrics.registerFont(TTFont('MSJH', 'C:/Windows/Fonts/msjh.ttc'))
    pdfmetrics.registerFont(TTFont('MSJH-Bold', 'C:/Windows/Fonts/msjhbd.ttc'))
    FONT_REGULAR = 'MSJH'
    FONT_BOLD = 'MSJH-Bold'
except Exception as e:
    print(f"Error registering fonts: {e}. Falling back to default.")
    FONT_REGULAR = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'

def make_header_footer(canvas, doc, doc_title):
    canvas.saveState()
    
    # Header
    canvas.setFont(FONT_BOLD, 8)
    canvas.setFillColor(colors.HexColor('#4B5563'))
    canvas.drawString(54, 750, doc_title.upper())
    
    # Top rule line
    canvas.setStrokeColor(colors.HexColor('#E5E7EB'))
    canvas.setLineWidth(0.5)
    canvas.line(54, 742, 558, 742)
    
    # Footer
    canvas.setFont(FONT_REGULAR, 8)
    canvas.setFillColor(colors.HexColor('#9CA3AF'))
    canvas.drawString(54, 36, "由 Antigravity 雙語對照系統生成")
    canvas.drawRightString(558, 36, f"第 {doc.page} 頁")
    
    # Bottom rule line
    canvas.line(54, 48, 558, 48)
    
    canvas.restoreState()

def build_pdf(filename, doc_title, content_list):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Define styles
    style_main_title = ParagraphStyle(
        'MainTitle',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=1, # Center
        spaceAfter=10
    )
    
    style_main_subtitle = ParagraphStyle(
        'MainSubtitle',
        parent=styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#4B5563'),
        alignment=1,
        spaceAfter=25
    )
    
    style_section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    style_sub_section_title = ParagraphStyle(
        'SubSectionTitle',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#10B981'),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    style_en_para = ParagraphStyle(
        'EnPara',
        parent=styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=3
    )
    
    style_zh_para = ParagraphStyle(
        'ZhPara',
        parent=styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=12
    )
    
    style_en_list = ParagraphStyle(
        'EnList',
        parent=styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor('#1F2937'),
        leftIndent=15,
        spaceAfter=2
    )
    
    style_zh_list = ParagraphStyle(
        'ZhList',
        parent=styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=8.5,
        leading=13,
        textColor=colors.HexColor('#2563EB'),
        leftIndent=15,
        spaceAfter=8
    )

    story = []
    
    # Title & Subtitle for first page
    story.append(Paragraph(doc_title, style_main_title))
    story.append(Paragraph("詳細內容雙語對照 / Detailed Bilingual Content", style_main_subtitle))
    
    # Decorative line
    sep_draw = Drawing(504, 2)
    sep_draw.add(Line(0, 0, 504, 0, strokeColor=colors.HexColor('#E5E7EB'), strokeWidth=1))
    story.append(sep_draw)
    story.append(Spacer(1, 15))
    
    for item in content_list:
        item_type = item[0]
        
        if item_type == 'section':
            en_title, zh_title = item[1], item[2]
            story.append(Paragraph(f"{en_title} / {zh_title}", style_section_title))
            
        elif item_type == 'subsection':
            en_title, zh_title = item[1], item[2]
            story.append(Paragraph(f"{en_title} / {zh_title}", style_sub_section_title))
            
        elif item_type == 'paragraph':
            en_text, zh_text = item[1], item[2]
            story.append(Paragraph(en_text, style_en_para))
            story.append(Paragraph(zh_text, style_zh_para))
            
        elif item_type == 'listitem':
            en_text, zh_text = item[1], item[2]
            story.append(Paragraph(en_text, style_en_list))
            story.append(Paragraph(zh_text, style_zh_list))
            
        elif item_type == 'pagebreak':
            story.append(PageBreak())
            
        elif item_type == 'spacer':
            story.append(Spacer(1, item[1]))

    def page_cb(canvas, doc):
        make_header_footer(canvas, doc, doc_title)

    doc.build(story, onFirstPage=page_cb, onLaterPages=page_cb)
    print(f"Generated PDF: {filename}")


# ================= 1. ELECTRA AND OEDIPUS COMPLEXES DATA =================
electra_oedipus_content = [
    ('section', 'Lead-in Questions', '導入問題'),
    ('paragraph',
     '1. The girl is attached to her father and shows jealousy and hatred toward her mother, which can be seen as Electra complex.',
     '1. 女孩依戀她的父親，並對她的母親表現出嫉妒和仇恨，這可以被視為「戀父情結」（愛莉克托拉情結）。'),
    ('paragraph',
     '2. Freudian psychoanalysis explained his trouble as Oedipus complex.',
     '2. 佛洛伊德的精神分析學將他的困擾解釋為「戀母情結」（伊底帕斯情結）。'),
    
    ('section', 'Scientific Meaning', '學術定義'),
    ('paragraph',
     'The positive libidinal feelings of a child toward the parent of the opposite sex and hostile or jealous feelings toward the parent of the same sex. It was used in the psychosexual stages of development theory by Sigmund Freud. (Dictionary by Merriam-Webster)',
     '兒童對異性父母的積極力比多情感，以及對同性父母的敵對或嫉妒情感。它被西格蒙德·佛洛伊德用於性心理發展階段理論中。（美利安-韋伯斯特詞典）'),
     
    ('section', 'Origins in Greek Mythology', '神話起源'),
    ('subsection', 'Electra Complex', '愛莉克托拉情結'),
    ('paragraph',
     '“Electra Complex” derives from the story of Electra by Sophocles of Greek mythology. It based on the revenge Electra and her brother Orestes who took on their mother Clytemnestra and stepfather Aegisthus for the murder of their father, King Agamemnon. The King was killed by his wife Clytemnestra after returning from Trojan War, and Clytemnestra believed the murder was justified, since Agamemnon had sacrificed their daughter Iphigenia before the war. Besides, Clytemnestra had taken Agamemnon’s cousin, Aegisthus as her lover when Agamemnon was away for the war. After knowing the death of Agamemnon, Electra mourned at his tomb and then together with Orestes, slain Clytemnestra and Aegisthus as a vengeance on their father’s death.',
     '「愛莉克托拉情結」源於希臘神話中索福克勒斯的《愛莉克托拉》的故事。它基於愛莉克托拉和她的哥哥奧瑞斯特斯對他們的母親克呂泰涅斯特拉和繼父埃癸斯托斯進行的復仇，因為後者殺害了他們的父親阿加曼農國王。國王在特洛伊戰爭歸來後被妻子克呂泰涅斯特拉殺害，而克呂泰涅斯特拉認為這場謀殺是合理的，因為阿加曼農在戰前犧牲了他們的女兒伊菲革涅亞。此外，在阿加曼農外出打仗時，克呂泰涅斯特拉已將阿加曼農的堂兄弟埃癸斯托斯納為情人。得知阿加曼農的死訊後，愛莉克托拉在父親的墓前哀悼，隨後與奧瑞斯特斯一起殺死了克呂泰涅斯特拉和埃癸斯托斯，以此為父親的死復仇。'),
     
    ('subsection', 'Oedipus Complex', '伊底帕斯情結'),
    ('paragraph',
     '“Oedipus Complex” by Sophocles also derives from Greek mythology, in the story of “Oedipus the King”. Oedipus became the king of Thebes and marry the dowager Jocasta after defeating the Sphinx, a creature with the head of a woman, the body of a lion and the wings of an eagle by answering its riddle.',
     '索福克勒斯的「伊底帕斯情結」也源於希臘神話中《伊底帕斯王》的故事。伊底帕斯在回答出人首獅身、長有鷹翼的怪獸斯芬克斯的謎題並擊敗牠後，成為底比斯的國王，並娶了寡婦王后約卡斯塔。'),
    ('paragraph',
     'Thebes was a plague-ravaged city; therefore, Oedipus sent his brother-in-law Creon to the oracle for solution. On his return, Creon announced that the oracle instructed them to find the murderer of Laius, the king who ruled Thebes before Oedipus. Summoned by Oedipus, a blind prophet Tiresias accused that it’s Oedipus who kill Laius. Oedipus rejected the prophet angrily, and after that, he tried to gain advice from his wife Jocasta; she comforted him to ignore the prophecy since she was told before that Laius would be killed by their son; so, their son was killed and abandoned, and Laius’ death was because of a band of robbers at crossroads.',
     '底比斯是一個飽受瘟疫蹂躪的城市；因此，伊底帕斯派他的小舅子克里昂去神諭處尋求解決方案。克里昂回來後宣佈，神諭指示他們尋找在伊底帕斯之前統治底比斯的國王萊優斯的謀殺者。伊底帕斯召來盲人預言家提瑞西阿斯，後者指控殺死萊優斯的人正是伊底帕斯。伊底帕斯憤怒地拒絕了預言家的說法，之後，他試圖從妻子約卡斯塔那裡獲得建議；約卡斯塔安慰他忽略預言，因為她以前被告知萊優斯會被他們的兒子殺死；但他們的兒子早已被殺害並遺棄，而萊優斯的死是由於十字路口的一夥強盜造成的。'),
    ('paragraph',
     'Nevertheless, Oedipus became distressed because he killed a man who resembled Laius at crossroads just before he came to Thebes. When he was a young man, a prophet said he was fated to kill his father and marry his mother. The fear of the prophecy made him leave his home in Corinth and brought him to Thebes. However, told by a shepherd who knew his true identity, Oedipus realized that the King and Queen of Corinth were not his real parents, and he was the son of Laius and Jocasta. Agonized by the fate, Jocasta killed herself, and Oedipus took the pin from her gown, gouged out his eyes and begged Creon to deport him.',
     '然而，伊底帕斯變得很痛苦，因為他在來到底比斯之前，剛好在十字路口殺死了一個長得很像萊優斯的人。當他年輕時，一個預言家說他命中注定要殺父娶母。對預言的恐懼使他離開了在哥林斯的家來到底比斯。然而，一個知道他真實身份的牧羊人告訴他，哥林斯的國王和王后並不是他的親生父母，他其實是萊優斯和約卡斯塔的兒子。約卡斯塔為命運所折磨而自殺，伊底帕斯拔下她禮服上的胸針，刺瞎了自己的雙眼，並乞求克里昂將他驅逐出境。'),
     
    ('pagebreak',),
    
    ('section', 'English Expressions from Greek Mythology', '源自希臘神話的英文表達'),
    ('subsection', 'Prometheus', '普羅米修斯'),
    ('paragraph',
     'There was a great battle between the Greek gods and a race of giants called Titan before the creation of humanity. The Titan Prometheus whose name means foresight fought with his brother Epimetheus on the side of the Greek gods. Winning the great battle, Zeus entrusted them with the task of creating all living things. Epimetheus was responsible for distributing the gifts of the gods among the creatures; meanwhile, Prometheus shaped the first humans out of mud. Prometheus refused to see humans who were denied to use fire, so he scaled Mount Olympus to steal fire. The flames gave them the power to harness nature for their own benefit and acted as a catalyst to accelerate progression of civilization.',
     '在人類被創造之前，希臘眾神與被稱為泰坦的巨人族之間發生了一場大戰。名字意為「先見之明」的泰坦巨人普羅米修斯與他的弟弟伊皮米修斯站在希臘眾神一邊戰鬥。贏得大戰後，宙斯委託他們完成創造所有生物的任務。伊皮米修斯負責在生物中分配眾神的禮物；與此同時，普羅米修斯用泥土塑造了第一批人類。普羅米修斯拒絕看到人類被剝奪使用火的權利，於是攀登奧林匹斯山竊取了火種。火焰給了人類利用自然謀求自身利益的力量，並作為加速文明進程的催化劑。'),
     
    ('subsection', 'Pandora’s box', '潘朵拉的盒子'),
    ('paragraph',
     'According to legend, Pandora was the first mortal woman and she received gifts from goddess, such as the capacity for deep emotion, mastery over language, fine craftsmanship, and attention to detail. At last, Zeus bestowed the trait of curiosity and a heavy box on Pandora. Zeus warned her not to open the box under any circumstance for the content was not for mortal eyes. However, her mind often wandered to the content of the sealed box because she was full of curiosity. One day, Pandora could not bear any longer. When the box was opened, all the forces of evil and suffering which Zeus had created were suddenly released. As Pandora wept, she became aware of a sound echoing from the box and felt a warm beam of light which could ease her pain. After that, she realized opening the box was irreversible, but alongside the strife, there was still a hope to temper its effects.',
     '根據傳說，潘朵拉是第一個凡人女性，她從女神那裡獲得了禮物，例如深刻的情感能力、對語言的掌握、精湛的手藝和對細節的關注。最後，宙斯賜予了潘朵拉好奇心的特質和一個沉重的盒子。宙斯警告她，在任何情況下都不要打開盒子，因為裡面的內容物不是凡人的眼睛可以看的。然而，由於她充滿了好奇心，她的思想經常游移到密封盒子的內容上。有一天，潘朵拉再也無法忍受了。當盒子被打開時，宙斯創造的所有邪惡與痛苦的力量突然被釋放出來。當潘朵拉哭泣時，她意識到盒子裡迴盪著一個聲音，並感覺到一束溫暖的光線，可以減輕她的痛苦。在那之後，她意識到打開盒子是不可逆轉的，但在衝突的同時，仍然有一份希望可以緩和其影響。'),
     
    ('subsection', 'Narcissus and Echo', '納西瑟斯與艾可 (水仙花與回音)'),
    ('paragraph',
     'A mountain nymph named Echo was punished by Hera, queen of the gods. From then on, Echo could only repeat the last words another said. One day, Echo met a stunningly beautiful man named Narcissus, but he refused to stay. With a broken heart, Echo wandered to a cave and gradually her body became weak until all that was left of her was her voice, which the wind carried to vast, empty places. The tragedy happened to Echo was not the first heart break over Narcissus. Nemesis, the goddess of revenge, decided to mete out a punishment which made Narcissus fall in love with himself when he saw his reflection in a glassy pool. Gazing at the reflection without eating and drinking, Narcissus finally wasted away and his body gradually became a white and yellow flower bending towards its reflection. From then on, it was known as narcissus.',
     '山林仙女艾可受到了眾神之后赫拉的懲罰。從那時起，艾可只能重複別人說的最後幾個字。有一天，艾可遇到了一個極其美麗的男子，名叫納西瑟斯，但他拒絕留下來。艾可心碎地在山洞裡遊蕩，她的身體逐漸虛弱，直到她只剩下了聲音，風將她的聲音帶到了遼闊而空曠的地方。發生在艾可身上的悲劇並不是納西瑟斯造成的第一次心碎。復仇女神涅墨西斯決定給予懲罰，讓納西瑟斯在清澈的池塘裡看到自己的倒影時愛上自己。納西瑟斯不吃不喝地凝視著倒影，最終憔悴逝去，他的身體逐漸變成了一朵向倒影彎曲的白色和黃色的花。從那時起，它就被稱為水仙花（narcissus）。'),
     
    ('subsection', 'Midas Touch', '點石成金 (邁達斯之手)'),
    ('paragraph',
     'Midas, king of Phrygia, spent his days in a stupor of splendor, spoiling himself and his beloved daughter and gorging himself on feasts and wine. One day, Midas discovered a satyr dozing in his garden and drunk. Midas recognized the satyr as one of Dionysus’ followers and brought him to the palace to nurse hangover. Pleased with Midas’ hospitality, Dionysus, god of wine, carnival, and performance, offered to grant him one wish. Despite the luxury in which he lived, Midas asked the god for the power which could turn anything he touched to gold. Soon after turning each item in the palace to gold, Midas realized that he could not eat or drink by himself anymore because everything he touched would become gold. Horrified by the fear that he might have turned his daughter into a golden statue, Midas begged the god to rid him of the power.',
     '弗里吉亞國王邁達斯在金碧輝煌的麻木中度日，溺愛自己和心愛的女兒，並沉溺於宴席和美酒中。有一天，邁達斯在花園裡發現了一個正在打瞌睡且喝醉的薩堤爾。邁達斯認出這個薩堤爾是戴奧尼索斯的追隨者之一，並將他帶到宮殿中照顧。酒神、狂歡與表演之神戴奧尼索斯對邁達斯的熱情款待感到高興，提出滿足他一個願望。儘管生活奢華，邁達斯還是請求神賜予他能將他所觸摸的任何東西變成黃金的力量。在將宮殿裡的每件物品變成黃金後不久，邁達斯意實到自己無法再獨自吃喝，因為他觸摸的一切都會變成黃金。邁達斯對自己可能已將女兒變成黃金雕像的恐懼感到震驚，懇求神收回這項力量。')
]


# ================= 2. CARPE DIEM DATA =================
carpe_diem_content = [
    ('section', 'Setting', '場景說明'),
    ('paragraph',
     '[Setting] All students sat in the classroom and were going to take a class. Keating, teaching the course of English literature, did not say any words and left the classroom whistling. Confused by the unusual start, all students looked around at each other. Keating poked his head back in the doorway and said “Well, come on.” Some of the students said while laughing “Is he kidding?” After a slight hesitation, the students took the textbook and followed Keating out into the main entranceway. Until all students arrived, Keating started the first class with the poems.',
     '［場景］所有學生都坐在教室裡準備上課。教授英文文學的基廷老師一句話也沒說，吹著口哨離開了教室。這不同尋常的開始讓學生們困惑地互相張望。基廷探頭回到門口說：「好啦，跟上。」有些學生笑著說：「他是在開玩笑嗎？」稍微猶豫後，學生們拿著教科書跟著基廷走到了主入口處。直到所有學生都到達，基廷以詩歌開始了第一堂課。'),
     
    ('section', 'Lead-in Dialogue', '導入對話'),
    ('listitem', 'Keating: Thank you, Mr. Pitts. "Gather ye rosebuds while ye may." The Latin term for that sentiment is Carpe Diem. Now who knows what that means?', '基廷：謝謝你，皮茨先生。「及時採折玫瑰花苞。」這份情感的拉丁文術語是 Carpe Diem。現在誰知道那是什麼意思？'),
    ('listitem', 'Meeks: Carpe Diem. That\'s "seize the day."', '麥克斯：Carpe Diem。那就是「把握光陰」（及時行樂）。'),
    ('listitem', 'Keating: Very good, Mr.-', '基廷：非常好，你是——'),
    ('listitem', 'Meeks: Meeks.', '麥克斯：麥克斯。'),
    ('listitem', 'Keating: Meeks. Another unusual name. Seize the day. Gather ye rosebuds while ye may. Why does the writer use these lines?', '基廷：麥克斯。又一個不同尋常的名字。把握光陰。及時採折玫瑰花苞。為什麼作者會使用這些詩句？'),
    ('listitem', 'Charlie: Because he\'s in a hurry.', '查理：因為他很趕時間。'),
    ('listitem', 'Keating: No, ding! Thank you for playing anyway. Because we are food for worms lads. Because, believe it or not, each and every one of us in this room is one day going to stop breathing, turn cold, and die.', '基廷：不，叮！但還是謝謝你參與。因為小夥子們，我們是蟲子的食物。因為信不信由你，這間教室裡的我們每一個人，總有一天會停止呼吸，變得冰冷並死去。'),
    ('listitem', 'Keating: Now I would like you to step forward over here and peruse some of the faces from the past. You\'ve walked past them many times. I don\'t think you\'ve really looked at them.', '基廷：現在我希望你們上前到這裡，仔細端詳一些來自過去的面孔。你們已經走過他們身邊很多次了。我不認為你們真的注視過他們。'),
    ('listitem', 'Keating: They’re not that different from you, are they? Same haircuts. Full of hormones, just like you. Invincible, just like you feel. The world is their oyster. They believe they’re destined for great things, just like many of you. Their eyes are full of hope, just like you. Did they wait until it was too late to make from their lives even one iota of what they were capable? Because you see, gentleman, these boys are now fertilizing daffodils. But if you listen real close, you can hear them whisper their legacy to you. Go on, lean in. Listen, you hear it? Carpe. Hear it? Carpe. Carpe diem. Seize the day, boys. Make your lives extraordinary.', '基廷：他們和你們沒有那麼大的不同，不是嗎？相同的髮型。充滿了荷爾蒙，就像你們一樣。不可戰勝，就像你們感覺到的那樣。世界在他們的手中。他們相信自己注定要成就偉大的事業，就像你們中的許多人一樣。他們的眼睛裡充滿了希望，就像你們一樣。他們是否等到為時已晚，才讓自己的生命發揮出哪怕是一丁點的才能？因為你看，紳士們，這些男孩現在正在為水仙花施肥。但是如果你們貼近傾聽，你們可以聽到他們向你們低語他們的遺志。去吧，湊近點。聽，你聽到了嗎？Carpe。聽到了嗎？Carpe. Carpe diem。把握光陰，孩子們。讓你們的生命變得非凡。'),
    
    ('section', 'Analysis of the Text', '文本解析'),
    ('paragraph',
     'The above text is from the movie “Dead Poets Society”, which demonstrates the essence of a great educator who inspires his students through poetry teaching. “Carpe diem”, the emphasis of the scene, is a Latin expression meaning “seize the day”. It is used for saying that people should enjoy the present rather than worrying about the future, according to the definition of Cambridge Online Dictionary. Many English words originated from foreign languages, such as Latin and many other languages.',
     '上述文本來自電影《春風化雨》（Dead Poets Society），它展示了一位通過詩歌教學啟發學生的偉大教育家的精髓。「Carpe diem」是一個拉丁文詞彙，意為「把握光陰」（seize the day）。根據《劍橋線上詞典》的定義，它用於表示人們應該享受當下，而不是擔心未來。許多英文單字起源於外來語，例如拉丁語和許多其他語言。'),
    ('paragraph',
     'Over 60 percent of English words we use today are Latin based. How did this happen? There may be a number of reasons: 1) It had something to do with the Roman Empire. Latin was the main language in the realm of Roman Empire. It plays an important role in the development of French, Romanian, Italian, Spanish, and many others. That is why it is often referred as a Mother Tongue. On the contrary, Old English, descended from West Germanic, was seen as a lowly, crude and barbaric language with little literacy or artistic value and was often spoken by the lower class. By the Middle Ages, Anglo-Norman French had a huge influence on Old English. With simplified grammatical features and Adapted Norman or Latin vocabulary, Middle English was arising as the dominant language in the late 14th century.',
     '我們今天使用的英文單字中有超過 60% 是以拉丁語為基礎的。這是如何發生的？可能有很多原因： 1) 這與羅馬帝國有關。拉丁語是羅馬帝國版圖內的主要語言。它在法語、羅馬尼亞語、義大利語、西班牙語和許多其他語言的發展中起著重要作用。這就是為什麼它經常被稱為「母語」。相反，源自西日耳曼語的古英語被視為一種低俗、粗糙和野蠻的語言，幾乎沒有文學或藝術價值，且通常由下層階級使用。到了中世紀，諾曼法語對古英語產生了巨大影響。伴隨著簡化的語法特徵和改編的諾曼或拉丁字彙，中古英語在 14 世紀末開始作為主導語言出現。'),
    ('paragraph',
     '2) Bible translation. John Wycliffe, a highly educated Englishman, tried to translate the Bible into Middle English. However, he faced a lot of opposition from the Church and the government because they thought English was an inappropriate language. Nevertheless, the views about English were changed progressively in the efforts to translate Bible.',
     '2) 聖經翻譯。約翰·威克里夫（John Wycliffe）是一位接受過高等教育的英國人，他試圖將聖經翻譯成中古英語。然而，他面臨來自教會和政府的極大反對，因為他們認為英語是一種不合適的語言。然而，在翻譯聖經的努力中，人們對英語的看法逐漸發生了變化。'),
    ('paragraph',
     '3) English Renaissance. From around 1500-1650, classical literature and music attracted a lot of attention. Therefore, some 10,000 to 12,000 words entered the English lexicon and many of these words were borrowed directly from Latin.',
     '3) 英國文藝復興。在 1500 至 1650 年左右，古典文學和音樂吸引了大量關注。因此，大約有 10,000 到 12,000 個單字進入了英文詞彙庫，其中許多單字直接借自拉丁語。'),
    ('paragraph',
     'Here are a few common Latins words used in English: Et cetera, pro bono, vice versa and mater in ‘alma mater’. Do you know the definition of them? Many languages left their traces in English. That is, English borrowed many foreign words from other languages, such as mi casa su casa, plaza and patio, cafeteria, savvy from Spanish, Bon appetite, Bon voyage from French, Emoji, Haiku, Yakuza, Origami, Anime from Japanese, and chop chop, feng shui, mahjong, chop suey, and dim sum from Chinese. Word borrowing is an universal phenomenon in language development, especially on vocabulary.',
     '這裡有一些英語中常用的拉丁詞：Et cetera (等等), pro bono (公益的), vice versa (反之亦然) 以及 alma mater (母校) 中的 mater。你知道它們的定義嗎？許多語言在英語中留下了痕跡。也就是說，英語借用了許多外來語，例如來自西班牙語的 mi casa su casa (我的家就是你的家), plaza (廣場) 和 patio (露台), cafeteria (自助餐廳), savvy (理解)；來自法語的 Bon appetit (祝胃口好), Bon voyage (一路順風)；來自日語的 Emoji (表情符號), Haiku (俳句), Yakuza (極道), Origami (摺紙), Anime (動漫)；以及來自漢語的 chop chop (快點), feng shui (風水), mahjong (麻將), chop suey (炒雜碎) 和 dim sum (點心)。詞彙借用是語言發展中的普遍現象，特別是在詞彙方面。'),
     
    ('pagebreak',),
    
    ('section', 'Summary & Extended Content', '電影摘要與延伸內容'),
    ('subsection', 'Movie Summary: Dead Poets Society', '電影大綱'),
    ('paragraph',
     'John Keating, graduated from Welton Academy, was introduced to teach English literature at his alma mater. In the first class, Keating started with a term in Latin, Carpe Diem, to encourage his students to seize the day. Neil Perry, who was inspired, restarted the club called the Dead Poets Society. There were seven participants and they regularly read poetry and verse in secret. Growing with Keating’s unusual teaching methods and involvement of the club, they realized living life on their own terms. As an organizer, Neil decided to pursue his love of acting despite his father furiously forbade him from performing. It was tragic that Neil committed suicide after he failed to persuade his father how passionate he was about acting. After that, the headmaster put the blame for Neil’s suicide on Keating, saying that Keating corrupting students with talk of freedom and individuality. Due to this, Keating was fired from Welton. In the final chapter, those who were inspired stood up on their desk to show respect and solidarity with the words “O Captain! My Captain!” while Keating was leaving the classroom. Keating smiled, nodded and proudly said “Thank you, boys.”',
     '約約翰·基廷畢業於威爾頓預備學校，被引薦到他的母校教授英文文學。在第一堂課上，基廷以拉丁文詞彙 Carpe Diem 開始，以鼓勵他的學生把握光陰。受到啟發的尼爾·佩里重新創辦了名為「死亡詩社」的社團。共有七名參與者，他們經常秘密地閱讀詩歌和詩句。隨著基廷獨特的教學方法和社團的參與，他們意識到要按自己的方式生活。作為組織者，尼爾決定追求他對演戲的熱愛，儘管他的父親極力禁止他演出。悲劇的是，在尼爾未能說服父親自己對演戲是多麼熱愛之後，他自殺身亡。在此之後，校長將尼爾的自殺歸咎於基廷，稱基廷用自由和個性的言論腐蝕了學生。因此，基廷被威爾頓開除。在最後一章中，那些受到啟發的人站在桌子上，在基廷離開教室時用「噢，船長！我的船長！」這句話來表示尊敬和團結。基廷微笑著、點了點頭，自豪地說：「謝謝你們，孩子們。」'),
     
    ('subsection', 'Actor Profile: Robin Williams', '演員介紹：羅賓·威廉斯'),
    ('paragraph',
     'Robin Williams, an American actor and comedian, was well-known for his improvisational skills. Acting John Keating in Dead Poets Society, he was nominated for the Academy Award for Best Actor. In his career, he was nominated for four Academy Awards, winning Best Supporting Actor for Good Will Hunting in 1998. He also received two Primetime Emmy Awards, six Golden Globe Awards, two Screen Actors Guild Awards, and five Grammy Awards. No doubt he is one of the greatest actors of all time. Sadly, on August 11, 2014, he committed suicide at his home. An autopsy revealed that Williams had had diffuse Lewy Body Dementia which had been misdiagnosed as Parkinson\'s. This may have contributed to his depression.',
     '羅賓·威廉斯，美國演員兼喜劇演員，以其即興表演天賦而聞名。在《春風化雨》中飾演約約翰·基廷，他獲得了奧斯卡最佳男主角獎提名。在他的職業生涯中，他獲得了四次奧斯卡獎提名，並於 1998 年憑藉《心靈捕手》獲得最佳男配角獎。他還獲得了兩次黃金時段艾美獎、六次金球獎、兩次美國演員工會獎和五次葛萊美獎。毫無疑問，他是歷史上最偉大的演員之一。遺憾的是，2014年8月11日，他在家中自殺身亡。屍檢顯示威廉斯患有瀰漫性路易氏體失智症，這曾被誤診為帕金森氏症。這可能導致了他的憂鬱症。'),
    ('paragraph',
     'Barack Obama, former President of United States, released a statement upon Williams\' death: “Robin Williams was an airman, a doctor, a genie, a nanny, a president, a professor, a bangarang Peter Pan, and everything in between ... He arrived in our lives as an alien—but he ended up touching every element of the human spirit. He made us laugh. He made us cry. He gave his immeasurable talent freely and generously to those who needed it most—from our troops stationed abroad to the marginalized on our own streets.”',
     '美國前總統巴拉克·歐巴馬在威廉斯逝世後發表聲明：「羅賓·威廉斯曾是飛行員、醫生、精靈、保姆、總統、教授、彼得潘，以及這兩者之間的一切……他像外星人一樣來到我們的生活中，但最終觸動了人類精神的每一個元素。他讓我們笑。他讓我們哭。他將自己無量的人才自由而慷慨地奉獻給了那些最需要它的人——從駐紮在國外的我們的軍隊，到我們自己街道上的邊緣人群。」')
]


# ================= 3. BEWARE OF GREEKS BEARING GIFTS DATA =================
greeks_gifts_content = [
    ('section', 'Lead-in Examples', '導入範例'),
    ('paragraph',
     '1. When Judy brought me cupcakes after our fight last week, my first impulse was to beware of Greeks bearing gifts.',
     '1. 當茱蒂在上週我們吵架後給我帶來杯子蛋糕時，我的第一反應是「無事獻殷勤，非奸即盜」（beware of Greeks bearing gifts，要小心帶來禮物的希臘人）。'),
    ('paragraph',
     '2. Beware of Greeks bearing gifts! Casandra, who has been spreading rumors to all my friends, suddenly tries to take me out to lunch.',
     '2. 要小心帶來禮物的希臘人！一直在向我所有朋友散布謠言的卡珊卓突然試圖請我吃午餐。'),
     
    ('section', 'Meaning & Origin', '語義與起源'),
    ('subsection', 'Meaning', '片語含義'),
    ('paragraph',
     'Be skeptical of a present or kindness from an enemy. (Farlex Dictionary of Idioms)',
     '對來自敵人的禮物或善意保持懷疑。（法雷克斯俚語詞典）'),
    ('subsection', 'Origin in the Trojan War', '特洛伊戰爭起源'),
    ('paragraph',
     'This is originally a Latin phrase, coming from the story of the Trojan War. Near the end of the ten-year long Trojan War, the Greeks constructed a large wooden horse to pose as a peace offering to the Trojans. Laocoon, the Trojans priest, suspected that some menace had been hidden in the horse, and warned the Trojans not to accept the gift, crying, “Do not trust the horse, Trojans! Whatever it is, I fear the Achaeans, even when bringing gifts.” However, after his warning, two sea serpents attacked Laocoon and his sons.',
     '這最初是一個拉丁片語，源於特洛伊戰爭的故事。在長達十年的特洛伊戰爭即將結束時，希臘人建造了一匹巨大的木馬，作為向特洛伊人提供的和平祭品。特洛伊人的祭司拉奧孔懷疑木馬中隱藏著某種威脅，並警告特洛伊人不要接受這份禮物，他喊道：「不要相信這匹馬，特洛伊人！不論那是什麼，我都害怕希臘人，即使是在他們帶來禮物的時候。」然而，在他的警告之後，兩條海蛇襲擊了拉奧孔和他的兒子們。'),
    ('paragraph',
     'The Trojans assumed it was a sign of Athena’s displeasure and opened the gates and wheeled the horse within their walls. A celebratory victory festival was held; however, little did they know that the Greek soldiers had been hidden inside the horse belly and the Greeks crept out to open the city gates at night. Tens of thousands of Greek army had flocked to the city; then Troy was destroyed.',
     '特洛伊人認為這是雅典娜不悅的象徵，於是打開城門，將木馬迎進了城牆之內。他們舉行了慶祝勝利的節日；然而，他們幾乎不知道希臘士兵已經隱藏在馬腹中，希臘人夜晚悄悄溜出來打開了城門。成千上萬的希臘軍隊湧入城市；隨後特洛伊被摧毀了。'),
     
    ('section', 'Extended Content & Adaptations', '延伸內容與改編作品'),
    ('subsection', 'Film: Troy (2004)', '電影：《特洛伊：木馬屠城》'),
    ('paragraph',
     'Troy, a film published in 2004, was based on the epic poem by Homer, The Iliad, which described activities in the last couple of weeks of the decade-long Trojan War. The war centered around the most beautiful woman in the world, Helen of Sparta. After the event of judgement of Paris, the goddess Aphrodite kept her promise to make Helen fall in love with Paris and run off with him. Raged for Helen’s leaving, Menelaus, king of Sparta, allied with his elder brother, Agamemnon, king of Mycenae. Making promise to get Helen back, they eventually grouped the Achaean army to invade Troy. The film ended with fall of Troy and a funeral held for Achilles (acted by Brad Pitt).',
     '2004 年發行的電影《特洛伊》改編自荷馬的史詩《伊利亞德》，該史詩描述了長達十年的特洛伊戰爭最後幾週的活動。戰爭圍繞著世界上最美麗的女性——斯巴達的海倫展開。在帕里斯的評判事件後，阿芙蘿黛蒂女神履行了她的諾言，讓海倫愛上帕里斯並與他私奔。為海倫的離開而憤怒的斯巴達國王墨涅拉俄斯與他的哥哥邁錫尼國王阿加曼農結盟。他們承諾要奪回海倫，最終集結了阿開亞軍隊入侵特洛伊。電影以特洛伊的陷落和為阿基里斯（布萊德·彼特飾）舉行的葬禮告終。'),
     
    ('subsection', 'BBC Comedy: Yes Minister', 'BBC 喜劇：《是，大臣》'),
    ('paragraph',
     'Yes Minister, a British political satire sitcom, was first broadcasted on BBC 2 from 1980 to 1984. The context was set in the private office of a British cabinet minister in the fictional Department of Administrative Affairs in Whitehall. Jim Hacker was the British Minister for Administrative Affairs, being responsible for policy development. As a Permanent Secretary of the Department, Sir Humphrey Appleby should support and give assistance to the Minister. As a senior public servant, Humphrey fully understood how government works and what kind of policy had good/bad influence on government or even on the Minster’s political career. In addition, the Principal Private Secretary Bernard Woolley always played a role in coordinating between political master and civil service boss. In short, the comedy centered around interaction among the three.',
     '《是，大臣》是一部英國政治諷刺情境喜劇，於 1980 年至 1984 年在 BBC 2 首次播出。故事背景設定在 Whitehall 虛構的行政事務部的一位英國內閣大臣的私人辦公室。吉姆·哈克是英國行政事務部大臣，負責政策制定。作為該部門的常務秘書，漢弗萊·阿普比爵士應該支持並為大臣提供協助。作為一名高級公務員，漢弗萊完全理解政府是如何運作的，以及什麼樣的政策對政府甚至對大臣的政治生涯有好的/壞的影響。此外，首席私人秘書伯納德·伍利總是在政治首腦和公務員首腦之間發揮協調作用。簡而言之，這部喜劇圍繞著這三者之間的互動展開。'),
    ('paragraph',
     'There was a plot quoting the phrases “Trojan horse” and “beware of Greeks bearing gifts” in season 3 episode 5, The Bed of Nails, in which Jim had been offered a job working on Transport issues and Sir Humphrey was explaining to him why it was a terrible idea.',
     '在第三季第五集《釘子床》中，有一個情節引用了「特洛伊木馬」和「小心帶來禮物的希臘人」這兩個片語，劇中吉姆被提供了一份負責運輸問題的工作，而漢弗萊爵士正在向他解釋為什麼這是一個糟糕透頂的主意。')
]


# ================= 4. BEEN THERE, DONE THAT! DATA =================
been_there_content = [
    ('section', 'Lead-in Dialogue', '導入對話'),
    ('listitem', '1. A: Why don\'t you join a book club?\nB: Been there, done that. I want to do something different.', '1. A：你為什麼不加入讀書俱樂部？\nB：我早就經歷過了（Been there, done that）。我想做些不同的事情。'),
    ('listitem', '2. A: It’s hard to ask the boss for a raise. I’m so nervous now.\nB: Yeah. Been there, done that.', '2. A：向老闆要求加薪很難。我現在好緊張。\nB：是啊，我早就經歷過了。'),
    
    ('section', 'Meaning & Origin', '語義與起源'),
    ('subsection', 'Meaning', '片語含義'),
    ('paragraph',
     'An exclamation expressing familiarity and boredom with a situation, experience, etc. (Collins English Dictionary)',
     '表達對某種情況、經歷等的熟悉與厭倦的感嘆詞。（柯林斯英語詞典）'),
    ('subsection', 'Origin', '片語來源'),
    ('paragraph',
     'The origin of this phrase could be traced back to 1970s. Carlito’s Way, an American crime novel, was written by Edwin Torres and published in 1975. Used in short form, the early example was “Money is only an object. I’ll get it. Got it, been there.” Ultimately, the phrase has become “been there, done that” and been commonly used in spoken English. Interestingly, there was an argument regarding where the expression “been there, done that” first arose. Some believed it arose in the United States, others considered it came from Australia. Wherever it was, the expression has spread worldwide.',
     '這個片語的起源可以追溯到 1970 年代。美國犯罪小說《角頭風雲》（Carlito\'s Way）由埃德溫·托雷斯撰寫，並於 1975 年出版。在縮寫形式中，早期的例子是：「錢只是一個對象。我會得到它。明白了，我早就經歷過了（been there）。」最終，這個片語演變成了「been there, done that」，並被廣泛用於英語口語中。有趣的是，關於「been there, done that」這句話最早起源於哪裡存在爭論。有些人認為它起源於美國，另一些人則認為它來自澳洲。不論起源於何處，這個表達已經傳播到世界各地。'),
     
    ('section', 'Grammar Concept', '文法概念'),
    ('listitem', '• The words “been” and “done” in this phrase are the form of past participle. (Base form: am/is/are -> Past: was/were -> Past Participle: been; do/does -> did -> done)', '• 這個片語中的單字「been」和「done」是過去分詞的形式。（原形 am/is/are -> 過去式 was/were -> 過去分詞 been；do/does -> did -> done）'),
    ('listitem', '• The phrase “been there, done that.” is used to express an experience or a situation which is familiar to us, so we use “the present perfect”, one of tenses in English.', '• 「been there, done that.」這個片語用於表達我們所熟悉的經歷或情況，所以我們使用英語時態中的「現在完成式」。'),
    ('listitem', '• The present perfect structure: subject + have / has + past participle.\nUsed in situations: 1) Things started in past and continued to present (e.g. A: How long have you lived in Taipei? B: I have lived here since 1997.) 2) Experiences up to present time (e.g. A: Have you ever been to Japan? B: No, I have never been there.)', '• 現在完成式結構：主詞 + have / has + 過去分詞。\n用於以下情況：1) 談論在過去開始並持續到現在的事情（例如：A: 你在台北住了多久？ B: 自 1997 年以來我就一直住在這裡。） 2) 談論我們直到現在的經歷（例如：A: 你去過日本嗎？ B: 沒有，我從來沒有去過那裡。）'),
    ('listitem', '• Omission: in order to emphasize a point or to avoid repeating the words that someone has already known, we sometimes omit several parts of a sentence. Omission is widely used in spoken English but it is an informal use in written words. In the case of this phrase, subject and auxiliary are omitted: (I have) been there, (I have) done that.', '• 省略：為了強調某一點或避免重複某人已經知道的單字，我們有時會省略句子的幾個部分。省略在英語口語中被廣泛使用，但在書面語中是一種非正式用法。在這個片語的情況下，主詞和助動詞被省略了：(I have) been there, (I have) done that。'),
    
    ('section', 'Extended Content & Variants', '延伸內容與變體'),
    ('paragraph',
     'As a well-known expression, the phrase has spawned a few variants. For instance, the phrase has been lengthened to “been there, done that, got the T-shirt” and been printed on the T-shirt that sold at touristic destinations. Basically, the role of added words in this phrase is for extra emphasis, so there is no real limit to how we use it. Depending on situation and showing creativity, there might be other variants.',
     '作為一個著名的表達方式，這個片語衍生出了幾個變體。例如，該片語被延長為「been there, done that, got the T-shirt」（去過那裡，做過那事，買了T恤），並被印在旅遊景點銷售的 T 恤上。基本上，添加的單字的作用是為了額外的強調，所以我們如何使用它並沒有真正的限制。根據情況並展現創意，可能還會有其他變體。'),
    ('paragraph',
     'BEEN THERE DONE THAT, founded by Satya Saya, is a series of interactive posters designed to inspire you to get out and do the things you love to do. There are 19 broad interests, from reading to entertainment, from travel to food, and from adults to kids. They built a formula that takes reviews and ratings from multiple sources to compile a more authentic 100 best list. Selecting a poster that complies with our passion, we scan where we want to go or what we want to do at first, then we scratch it and we will find the stunning artwork underneath. After we have been there or done that, we can put a mark and rate it a score with stickers. The poster is not only a decoration, but also a multitude of experiences in life.',
     '由 Satya Saya 創立的「BEEN THERE DONE THAT」是一系列互動式海報，旨在激發你走出戶外去做你熱愛的事情。有 19 個廣泛的興趣領域，從閱讀到娛樂，從旅行到食物，以及從成人到兒童。他們建立了一個公式，從多個來源收集評論和評分，以編制一份更真實的 100 個最佳清單。選擇符合我們熱情的海報，我們先掃描我們想去的地方或我們想做的事情，然後將其刮開，我們就會發現下面令人驚嘆的藝術品。在我們去過那裡或做過那事之後，我們可以用貼紙做一個標記並給它評分。海報不僅僅是一個裝飾品，更是人生中豐富多彩的經歷。')
]


# ================= 5. ACHILLES’ HEEL DATA =================
achilles_heel_content = [
    ('section', 'Lead-in Examples', '導入範例'),
    ('paragraph',
     '1. Mathematics has always been my Achilles\' heel.',
     '1. 數學一直是我的致命傷（阿基里斯之踵）。'),
    ('paragraph',
     '2. The team\'s offense is their Achilles\' heel.',
     '2. 該隊的進攻是他們的致命弱點。'),
    ('paragraph',
     '3. Marketing traditionally has been an Achilles\' heel for phone companies because of their monopoly mind-set.',
     '3. 營銷傳統上一直是電話公司的致命弱點，因為他們的壟斷心態。'),
     
    ('section', 'Meaning & Origin', '語義與起源'),
    ('subsection', 'Meaning', '片語含義'),
    ('paragraph',
     'A small problem or weakness in a person or system that can result in failure. (Cambridge Online Dictionary)',
     '一個人或系統中可能導致失敗的小問題或弱點。（《劍橋線上詞典》）'),
    ('subsection', 'Origin in Greek Mythology', '神話起源'),
    ('paragraph',
     'The common phrase “Achilles’ heel” comes from ancient Greek mythology. Thetis, one of daughters of the sea god Nereus, was married to Peleus (King of the Thessaly) and gave birth to Achilles. Making Achilles invulnerable, intelligent and brave, Thetis dipped him into the River Styx as a baby. However, a part of his body did not immerse in the water, namely heel, because it was held by his mother. As a result, his heel remained unprotected. In Trojan war, Paris, prince of Troy, guided by Apollo and shot an arrow which pierced Achilles’ heel. After that, Achilles was mortally wounded and died in the war.',
     '常見片語「阿基里斯之踵」源於古希臘神話。海神涅柔斯的女兒之一忒提斯嫁給了佩琉斯（色薩利國王）並生下了阿基里斯。為了讓阿基里斯刀槍不入、聰明勇敢，忒提斯在他嬰兒時將他浸入冥河（River Styx）中。然而，他身體的一個部分沒有浸入水中，即腳踝（腳跟），因為它被他的母親握著。結果，他的腳跟仍然沒有受到保護。在特洛伊戰爭中，特洛伊王子帕里斯在阿波羅的指引下射出了一支箭，刺穿了阿基里斯的腳跟。在此之後，阿基里斯受了致命傷並在戰爭中死去。'),
    ('paragraph',
     'Actually, the phrase Achilles’ heel was not used in English until 19th century. It was used as a metaphor for vulnerability in an essay named The Friend; a literary, moral and political weekly paper, which was written by Samuel Taylor Coleridge in 1810. He wrote “Ireland, that vulnerable heel of the British Achilles!” That was how the connection was established. Furthermore, the tendon at the back of human heel was even named the Achilles\' tendon as a medical term. To sum up, Greek mythology has a great influence on English expressions.',
     '事實上，「阿基里斯之踵」這個片語直到 19 世紀才在英語中使用。它被用作脆弱性的隱喻，出現在山繆·泰勒·柯勒律治於 1810 年撰寫的散文《朋友；文學、道德和政治週刊》中。他寫道：「愛爾蘭，英國阿基里斯那脆弱的腳跟！」這就是這種聯繫的建立方式。此外，人體腳踝後面的肌腱甚至在醫學術語中被命名為「阿基里斯腱」。總之，希臘神話對英語表達有著巨大的影響。'),
     
    ('section', 'Extended Content', '延伸內容'),
    ('subsection', 'Achilles in Philosophy (Zeno’s Paradox)', '哲學中的阿基里斯 (芝諾悖論)'),
    ('paragraph',
     'Do you know Achilles also plays an interesting role in Philosophy? Have you heard of Zeno’s paradox? Even though Achilles is a hero and runs fast in Greek methodology, he could never outrun a tortoise. A paradox is a situation or statement that seems impossible or is difficult to understand because it contains two opposite facts or characteristics. (Cambridge Online Dictionary) This particular paradox about Achilles looks into the paradoxes of motion. Let us assume: Achilles is in a footrace with a tortoise and he allows the tortoise a run 100 meters before he starts. Since this is an English class, not philosophy, we are going to jump to the conclusion: Achilles will never catch up with the tortoise. Isn’t this fascinating? For those who are interested in how it came to this conclusion, please discuss this in the discussion forum. Meanwhile, if you take one of the new philosophical courses regarding paradoxes in the Department of Humanities, you will learn about this to a great extent.',
     '學長，你知道阿基里斯在哲學中也扮演著有趣的角色嗎？你聽說過芝諾悖論嗎？儘管阿基里斯是一位英雄，並且在希臘神話中跑得很快，但他永遠無法超越一隻烏龜。悖論是指一種看似不可能或難以理解的情況或陳述，因為它包含兩個相反的事實或特徵。（《劍橋線上詞典》）這個關於阿基里斯的特殊悖論研究了運動的悖論。讓我們假設：阿基里斯與烏龜進行一場跑步比賽，他在開始之前允許烏龜先跑 100 米。既然這是英語課，而不是哲學課，我們將跳到結論：阿基里斯永遠追不上烏龜。這不是很迷人嗎？對於那些對它是如何得出這個結論感興趣的人，請在討論區進行討論。同時，如果您選修人文學部關於悖論的新哲學課程之一，您將在很大程度上學習到這一點。'),
     
    ('subsection', 'The River Styx', '冥河'),
    ('paragraph',
     'According to Greek mythology, Styx was one of rivers that formed the boundary between Earth and the Underworld. There was a ferryman called Charon, who took responsibility for transporting souls of the newly dead to the Underworld. In order to cross the river, dead people must pay the fee to Charon, or they would be left to wander for one hundred years. Moreover, Styx was also known as a goddess in charge of the River Styx. The river had miraculous powers to make someone dipped into the river invulnerable. Achilles was the most famous one from mythology.',
     '根據希臘神話，冥河是形成地球與冥界邊界的河流之一。有一位叫卡倫的船夫，他負責將新死者的靈魂運送到冥界。為了過河，死者必須向卡倫支付費用，否則他們將被留下徘徊一百年。此外，Styx 也被稱為掌管冥河的女神。這條河具有神奇的力量，可以使浸入河中的人刀槍不入。阿基里斯是神話中最著名的一個。'),
     
    ('subsection', 'The Judgement of Paris', '帕里斯的評判'),
    ('paragraph',
     'Eris, a goodness of strife and discord, bore a grudge against Peleus and Thetis because she was not invited to attend their wedding reception. Therefore, she tossed a golden apple inscribed “for the most beautiful one” into the party. The goddesses Hera, Athena and Aphrodite had a bitter quarrel about the appropriate recipient, and they asked Zeus to make the decision. However, Zeus passed the buck to the prince of Troy, Paris. He was appointed to select a goodness who is the most beautiful. As a result, the goddesses was seeking the judgement of Paris through bribes, offering political power by Hera, promising infinite wisdom by Athena, and tempting with the most beautiful woman in the world by Aphrodite. After some consideration, he decided to award Aphrodite the golden apple, thereby causing Trojan war which centered around the most beautiful woman in the world, Helen. Thus, the judgement of Paris was considered to be the main event leading up to the war.',
     '紛爭與不和女神艾莉絲對佩琉斯和忒提斯心存怨恨，因為她沒有被邀請參加他們的婚禮。因此，她在派對上扔下了一個刻有「給最美麗的女性」的金蘋果。女神赫拉、雅典娜和阿芙蘿黛蒂為合適的接受者發生了激烈的爭吵，她們要求宙斯做出決定。然而，宙斯將這個責任推給了特洛伊王子帕里斯。他被任命選出一位最美麗的女神。結果，女神們通過賄賂尋求帕里斯的評判，赫拉提供政治權力，雅典娜承諾無限的智慧，而阿芙蘿黛蒂則以世界上最美麗的女性來誘惑他。經過一番考量，他決定將金蘋果授予阿芙蘿黛蒂，從而引發了圍繞世界上最美麗的女性海倫展開的特洛伊戰爭。因此，帕里斯的評判被認為是導致戰爭的主要事件。')
]

if __name__ == "__main__":
    # Generate the 5 detailed bilingual PDFs
    build_pdf("electra_oedipus_bilingual.pdf", "Unit: Electra Complex and Oedipus Complex", electra_oedipus_content)
    build_pdf("carpe_diem_bilingual.pdf", "Unit: Carpe Diem", carpe_diem_content)
    build_pdf("greeks_gifts_bilingual.pdf", "Unit: Beware of Greeks Bearing Gifts", greeks_gifts_content)
    build_pdf("been_there_bilingual.pdf", "Unit: Been There, Done That!", been_there_content)
    build_pdf("achilles_heel_bilingual.pdf", "Unit: Achilles' Heel", achilles_heel_content)
    print("Done generating all 5 newest detailed bilingual PDFs.")
