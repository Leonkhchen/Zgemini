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


# ================= 1. TO BE OR NOT TO BE DATA =================
to_be_content = [
    ('section', 'Unit Expressions', '單元核心表達'),
    ('paragraph',
     'We will look at five expressions and their meanings in this unit. They are:\n1. To be or not to be, that is the question.\n2. Talk to the hand\n3. Déjà vu\n4. Air quotation\n5. Too much information.',
     '在本單元中，我們將探討五個常用表達及其含義：\n1. 生存還是毀滅，這是個問題。\n2. 跟我的手說吧（不想聽你說）。\n3. 既視感（似曾相識）。\n4. 空中引號（表示諷刺或否定）。\n5. 訊息量太大（TMI）。'),
     
    ('section', 'Expression 1: To Be or Not to Be, That is the Question', '表達一：生存還是毀滅，這是個問題。'),
    ('subsection', 'Lead-in Questions', '導入問題'),
    ('paragraph',
     '1. Hamlet says \'To be or not to be\' because he is questioning the value of life and asking himself whether it\'s worthwhile hanging in there.',
     '1. 哈姆雷特說「生存還是毀滅」，因為他正在質疑生命的價值，並問自己是否值得堅持下去。'),
    ('paragraph',
     '2. To be, or not to be, that is the question:\nWhether \'tis nobler in the mind to suffer\nThe slings and arrows of outrageous fortune,\nOr to take arms against a sea of troubles\nAnd by opposing end them.',
     '2. 生存還是毀滅，這是個問題：\n是否在心靈中忍受狂暴命運的飛石和暗箭更顯高貴，\n還是挺身反抗無邊的苦難，\n並通過奮鬥將其掃除。'),
     
    ('subsection', 'Meaning', '含意'),
    ('paragraph',
     'To be or not to be, that is the question: It is used to express one\'s indecision or hesitation about doing something. It is derived from the famous line in Act 3, Scene 1 of William Shakespeare\'s Hamlet, "To be, or not to be, that is the question." (Farlex Dictionary of Idioms)',
     '「生存還是毀滅，這是個問題」：它用來表達一個人對做某事時的猶豫不決或遲疑。它源自威廉·莎士比亞的《哈姆雷特》第三幕第一場中的著名台詞：「生存還是毀滅，這是個問題。」（法雷克斯俚語詞典）'),
     
    ('subsection', 'Origin & Analysis', '起源與分析'),
    ('paragraph',
     'It originates from Hamlet, a tragedy written by William Shakespeare, about 1599–1601. As the play opens, Hamlet is mourning his father, who has been killed, and lamenting the behavior of his mother, Gertrude, who married his uncle Claudius within a month of his father’s death. The ghost of his father appears to Hamlet, informs him that he was poisoned by Claudius, and commands Hamlet to avenge his death.',
     '它源於威廉·莎士比亞大約在 1599 至 1601 年間創作的悲劇《哈姆雷特》。戲劇開場時，哈姆雷特正在哀悼被殺害的父親，並為他母親葛楚德在父親去世不到一個月內就嫁給他的叔叔克勞迪斯的行為感到哀傷。他父親的鬼魂向哈姆雷特顯現，告知他自己是被克勞迪斯毒死的，並命令哈姆雷特為他的死報仇。'),
    ('paragraph',
     'The soliloquy is essentially all about life and death: "To be or not to be" means "To live or not to live" (or "To live or to die"). Hamlet discusses how painful and miserable human life is, and how death (specifically suicide) would be preferable, would it not be for the fearful uncertainty of what comes after death.',
     '這段獨白本質上完全是關於生命與死亡的：「生存還是毀滅」意為「活著還是不活」（或「生存還是死亡」）。哈姆雷特討論了人類的生活是多麼痛苦和悲慘，如果不是因為對死後世界可怕的不確定性，死亡（特別是自殺）將是更可取的。'),
     
    ('pagebreak',),
    
    ('section', 'Extended Content: Expressions 2 to 5', '延伸內容：表達二至五'),
    ('subsection', 'Expression 2: Talk to the hand', '表達二：跟我的手說吧'),
    ('paragraph',
     'Talk to the hand: It is informal and used in spoken English. It is used to tell someone rudely that you do not want to listen to anything they are going to say. (Longman Dictionary of Contemporary English)\nYou can use the phrase before the person starts talking to you or use it during the conversation to cut them off. Typically, people that use “talk to the hand” will put their hand in front of the other person’s face that’s talking to them. It can have an ominous or a friendly tone, depending on the situation. Many people use the phrase to poke fun at someone or stop them from asking for money.',
     '跟我的手說吧（Talk to the hand）：這是一種口語和非正式的表達。它用於粗魯地告訴某人你不想聽他們要說的任何話。（《朗文當代英語辭典》）\n你可以在對方開始跟你說話之前使用這個片語，或者在對話中使用它來打斷對方。通常，使用這個表達的人會把手放在對他們說話的人的臉前。根據具體情況，它可以帶有威脅性或友好的語調。許多人用這個片語來取笑某人，或阻止他們要錢。'),
    ('paragraph',
     'Examples:\nJack: What do you mean you can’t help me out?\nAna: I’ve heard enough, Jack, talk to the hand.',
     '範例：\n傑克：你說你不能幫我忙是什麼意思？\n安娜：我聽夠了，傑克，跟我的手說吧。'),
     
    ('subsection', 'Expression 3: Déjà vu', '表達三：既視感 (似曾相識)'),
    ('paragraph',
     'Déjà vu: It is used to describe the feeling that what is happening now has happened before in exactly the same way. (Longman Dictionary of Contemporary English)\n“Déjà vu” is literally translated from French to mean “already seen.” It is a sense of having already seen something—coupled with knowing you haven’t actually seen it. When it is used in a sentence, it could be used to express a feeling that one has seen or heard something before.',
     '既視感（Déjà vu）：它用於描述一種感覺，即現在正在發生的事情以前曾以完全相同的方式發生過。（《朗文當代英語辭典》）\n「Déjà vu」字面意思從法語翻譯為「已經看見過」。這是一種已經見過某事的感覺，同時又清楚地知道自己實際上並沒有見過它。當在句子中使用時，它可以表示一個人以前曾看過或聽過某事的感覺。'),
    ('paragraph',
     'In 2006, the movie “Déjà vu”, an American science fiction action film starring Denzel Washington, involves an agent who travels back in time in an attempt to prevent a domestic terrorist attack and to save a woman with whom he falls in love. Olivia Rodrigo’s song “Déjà vu” became extreme popular while released in 2021, and the tune depicts Rodrigo as an ex-girlfriend who realizes that her former lover\'s new girlfriend is just like her.',
     '在2006年的電影《既視感》（Déjà vu）中，由丹佐·華盛頓主演的一部美國科幻動作片，講述了一名特工回到過去，試圖阻止一起國內恐怖襲擊並拯救他愛上的女人的故事。奧莉維亞·羅德里戈在 2021 年發行的歌曲《Déjà vu》變得非常受歡迎，曲調描述了羅德里戈作為一個前女友，意識到前任的新女友和她一模一樣。'),
    ('paragraph',
     'Examples:\nWhen I met her, I had a strange feeling of déjà vu.\nI entered the room and immediately felt a sense of déjà vu.',
     '範例：\n當我遇見她時，我有一種奇怪的既視感。\n我進入房間，立刻感到一種既視感。'),
     
    ('subsection', 'Expression 4: Air quotation', '表達四：空中引號'),
    ('paragraph',
     'Air quotation: It is a movement that someone makes in the air with their fingers to show that what they are saying should be in quotation marks, and that it should not be taken as their real opinion or their usual way of speaking. (Longman Dictionary of Contemporary English)\nThis sign means that you are quoting someone’s statements. However, it is often used altogether with tone to convey your sarcasm and satire about what is being quoted or highlight a word or a phrase when we speak and show disagreement of word choice.',
     '空中引號（Air quotation）：這是一個人用手指在空中做出的動作，表示他們所說的話應該加上引號，不應被視為他們的真實觀點或他們平常的說話方式。（《朗文當代英語辭典》）\n這個手勢意味著你正在引用某人的陳述。然而，它通常與語氣一起使用，以表達你對所引用內容的諷刺和挖苦，或者在我們說話時突出一個單字或片語，並表示對字詞選擇的不同意。'),
    ('paragraph',
     'Examples:\nDr. Steve’s misinformed statements on the dangers of vaccination seem to suggest that we should use air quotes when calling him ‘doctor\'.\nThe commercial said it was so “reasonable” and “affordable”, but really it’s just a rip-off.',
     '範例：\n史蒂夫博士關於接種疫苗危險的錯誤言論似乎表明，我們在稱他為『醫生』時應該使用空中引號。\n廣告上說它是如此的「合理」和「負擔得起」，但實際上它只是一個騙局。'),
     
    ('subsection', 'Expression 5: Too much information', '表達五：訊息量太大 / 說得太多了'),
    ('paragraph',
     'Too much information: It is informal and used in spoken English. It is used when someone has just told you details that you think are embarrassing or unpleasant, and you do not want to hear any more. (Longman Dictionary of Contemporary English)\nIt is an expression indicating that someone has revealed information that is too personal and made the listener or reader uncomfortable. It could be written as "TMI".',
     '訊息量太大（Too much information / TMI）：這是口語和非正式的表達。它用於當某人剛剛告訴你你認為尷尬或不愉快的細節，且你不想再聽下去時。（《朗文當代英語辭典》）\n這是一種表示某人透露了過於私人且讓聽眾或讀者感到不舒服的信息的表達。它可以寫成「TMI」。'),
    ('paragraph',
     'Examples:\nJack: I\'ve been to the toilet twice already.\nAna: Too much information!',
     '範例：\n傑克：我已經去過兩次廁所了。\n安娜：訊息量太大！')
]


# ================= 2. HOW DIFFICULT AND HOW MUCH SHOULD I READ DATA =================
difficulty_content = [
    ('section', 'Lead-in Questions', '導入問題'),
    ('paragraph',
     'Please answer these questions:\nDo you know how quick an average reader reads?\nHow do you choose your English reading materials?\nHow often do you read?',
     '請回答這些問題：\n你知道一個普通讀者的閱讀速度有多快嗎？\n你如何選擇你的英語閱讀材料？\n你多久閱讀一次？'),
     
    ('section', 'Difficulty Level of Reading Materials', '閱讀材料的難易度'),
    ('paragraph',
     'Reading or learning to read is hard work. When we read, we try to recognize words associated with pronunciation and meaning through letter and word knowledge, then we combine what we have with our own background knowledge and develop our own interpretation of what we read. Our brain processes various information at the same time. This is not an easy task for the first language learners, it is even harder for second or foreign language learners because of the limited learning time and environment. Second or foreign language learners inevitably face difficulty decoding (of words) frequently. In order to have a general reading comprehension, a vocabulary of 3,000 word families or 5,000 lexical items is needed, as this would cover 90-95% of any non-specialist text (Chiang, 2009). Below this threshold level, it is difficult for learners to use reading strategies (such as the commonly mentioned guessing the meaning of a particular word from the context) for decoding. According to Waring and Takaki (2003), even if a word is encountered more than 18 times in a text, there is only a 10-15% chance that a reader will be able to remember its meaning. This seems disappointing, doesn’t it?',
     '閱讀或學習閱讀是一項艱苦的工作。當我們閱讀時，我們試圖通過字母和單字知識來識別與發音和意義相關的字詞，然後將我們所擁有的與我們自己的背景知識相結合，並對我們所讀的內容發展出我們自己的解釋。我們的大腦同時處理各種信息。對於第一語言學習者來說，這不是一項簡單的任務，而對於第二語言或外語學習者來說，由於學習時間和環境的限制，這更是難上加難。第二語言或外語學習者不可避免地經常面臨解碼（字詞）的困難。為了獲得一般的閱讀理解能力，需要 3,000 個詞族或 5,000 個詞彙項目的詞彙量，因為這將覆蓋任何非專業文本的 90-95%（Chiang, 2009）。低於這個門檻水平，學習者很難使用閱讀策略（例如通常提到的根據上下文猜測特定單字的含義）進行解碼。根據 Waring 和 Takaki（2003年）的研究，即使一個單字在文本中出現超過 18 次，讀者也只有 10-15% 的機會能夠記住它的含義。這看起來令人失望，不是嗎？'),
    ('paragraph',
     'Don’t despair yet. The Extensive Reading Approach we learned in the previous unit seems to be a way out. We can expose ourselves to a lot of reading, in order to increase the encountering with the words in different texts and contexts. However, this kind of approach takes time, which many second language or foreign language learners do not have. Therefore, I am going to try to give some advice to save your time for reading.',
     '先不要絕望。我們在上一單元中學習的泛讀方法似乎是一條出路。我們可以讓自己接觸大量的閱讀，以便在不同的文本和語境中增加與字詞相遇的機會。然而，這種方法需要時間，而許多第二語言或外語學習者並沒有時間。因此，我將嘗試提供一些建議，以節省您的閱讀時間。'),
     
    ('subsection', 'Question: How difficult should I read?', '問題：我應該讀多難的書？'),
    ('paragraph',
     'Research has shown that a vocabulary size of 9,000 word families plus proper nouns covers over 98% of various texts (Nation, 2006; 2014). Therefore, setting 9,000 word families as your long-term goal is reasonable. With this vocabulary size, you could probably read unsimplified texts without assistance (Nation, 2014). For your information, an educated native speaker of English has a vocabulary size of around 20,000 words. Native speakers increase their vocabulary at the rate of around 1,000 word families per year (Nation, 2014). From my own research and experience, an undergraduate student in a leading university in Taiwan has a vocabulary size of approximately 8,000-10,000 words. To read without too many unfamiliar words becoming a burden while reading, no more than 2% of the running words should be beyond your knowledge (Nation, 2014). In other words, only two words in a 100-word text should be unknown. That is, 10 words in a 500-word text which is about one A4 single spaced page. Reading from the first paragraph and the above information, we can say that in principle, 2%-5% of unknown words in a text is acceptable for it does not cause comprehension difficulties. So, reading difficult materials which is way beyond our level is not always good, we should know our own levels first and then evaluate the materials based on the 95%-98% principle.',
     '研究表明，9,000 個詞族的詞彙量加上專有名詞可以覆蓋超過 98% 的各種文本（Nation, 2006; 2014）。因此，將 9,000 個詞族設定為您的長期目標是合理的。有了這個詞彙量，您可能可以在沒有協助的情況下閱讀未經簡化的文本（Nation, 2014）。供您參考，一個受過良好教育的英語母語者的詞彙量約為 20,000 個單字。母語者以每年大約 1,000 個詞族的速度增加他們的詞彙量（Nation, 2014）。根據我自己的研究和經驗，台灣頂尖大學的大學生的詞彙量大約在 8,000-10,000 個單字左右。為了在閱讀時不讓陌生單字成為負擔，文本中超出您知識範圍的字詞不應超過連續字詞的 2%（Nation, 2014）。換句話說，在一個 100 字的文本中，只有兩個單字應該是未知的。也就是說，在一個大約為一頁 A4 單倍行距的 500 字文本中，有 10 個未知單字。從第一段和上述信息來看，我們可以在原則上說，文本中 2%-5% 的未知單字是可接受的，因為它不會造成理解困難。因此，閱讀遠遠超出我們水平的困難材料並不總是好事，我們應該先了解自己的水平，然後根據 95%-98% 的原則評估材料。'),
    ('paragraph',
     'In addition, we generally select reading materials that are either slightly over our level or under our level, depending on the different purposes of learning. If the purpose is to build reading interest or confidence, or vocabulary review, then we can choose the materials that are slightly under our English level in order to increase the speed and fun of reading. If our reading purpose is to increase vocabulary size, then we would benefit more if we read materials that are slightly above our current level for they contain words we do not know yet (Chiang, 2018). Research also suggests that a combination of extensive reading and direct vocabulary instruction is a more efficient method for vocabulary expansion (Nation, 1997; Schmitt, 2000).',
     '此外，我們通常會根據不同的學習目的，選擇略高於我們水平或低於我們水平的閱讀材料。如果目的是建立閱讀興趣或信心，或者進行詞彙複習，那麼我們可以選擇略低於我們英語水平的材料，以提高閱讀速度和樂趣。如果我們的閱讀目的是增加詞彙量，那麼如果我們閱讀略高於我們當前水平的材料，我們將受益更多，因為它們包含我們還不認識的單字（Chiang, 2018）。研究還表明，泛讀與直接詞彙教學相結合是擴展詞彙量更有效的方法（Nation, 1997; Schmitt, 2000）。'),
     
    ('pagebreak',),
    
    ('subsection', 'Question: How much should I read?', '問題：我應該閱讀多少？'),
    ('paragraph',
     'Usually, when it comes to input for language learning, we would say the more the better. According to Nation (2014), a learner is assumed to meet a particular word 12 times before a learner can actually recognize the word, i.e. learn the word. This ‘twelve repetitions’ are “enough to allow the opportunity for several dictionary look-ups, several unassisted retrievals, and an opportunity to meet each word in a wide variety of contexts.” An average reader reads between 150-200 words per minute. Nation (2014) tried to use corpora data to work out how much reading a learner should read in terms of running word counts and reading time. He worked out that for a reader with a slower speed of 150 words per minute to increase from a vocabulary size of 2,000 to 3,000, s/he would need to read around 200,000 words, and it would probably take 33 minutes per week, which is 7 minutes per day. For a learner of 3,000 word vocabulary size, s/he would need to read 300,000 running words, and that will be about 50 minutes per week (10 minutes per day). Furthermore, from the 4,000 level on, the increase of the required reading amount would become 500,000 extra words per year, which would take a learner about 17 minutes per day to read. For a 7,000-level learner, over an hour a day, five days a week, 40 weeks of the year would need to be devoted to reading, according to Nation’s calculation. Therefore, my suggestion is to stay or at least maintain the minimum level of contact with English. That is, reading for 15-30 minutes a day. It is like doing exercise or playing the musical instrument, frequency of contact matters.',
     '通常，當談到語言學習的輸入時，我們會說越多越好。根據 Nation（2014年）的說法，一個學習者被假定要在遇見一個特定單字 12 次之後才能真正識別該單字，即學會該單字。這「十二次重複」是「足以讓讀者有機會進行幾次字典查詢、幾次無輔助檢索，以及在各種語境中遇到每個單字的機會。」一個普通讀者的閱讀速度在每分鐘 150-200 個單字之間。Nation（2014年）試圖利用語料庫數據計算出學習者在運行詞數和閱讀時間方面應該閱讀多少。他計算出，對於一個閱讀速度較慢、每分鐘 150 字的讀者來說，要將詞彙量從 2,000 擴展到 3,000，他需要閱讀大約 200,000 字，這大約需要每週 33 分鐘，即每天 7 分鐘。對於一個擁有 3,000 字詞彙量的學習者來說，他需要閱讀 300,000 字，大約是每週 50 分鐘（每天 10 分鐘）。此外，從 4,000 級開始，所需閱讀量的增加將變為每年 500,000 個額外的字，這將需要學習者每天花大約 17 分鐘進行閱讀。對於一個 7,000 級的學習者來說，根據 Nation 的計算，一年中有 40 週、每週五天、每天需要花一個多小時進行閱讀。因此，我的建議是保持或至少維持與英語接觸的最低水平。也就是說，每天閱讀 15-30 分鐘。這就像做運動或彈奏樂器一樣，接觸的頻率至關重要。'),
    ('paragraph',
     'Nation also pointed out an exciting result in one of his results. With his analysis of the corpora, it is better for learners to both read a lot (of magazines, newspapers and novels) and watch plenty of movies for vocabulary inclusion. Therefore, when you are tired of reading, watch a movie instead!!',
     'Nation 還指出了一個令人興奮的結果。通過他對語料庫的分析，對於學習者來說，最好是既大量閱讀（雜誌、報紙和小說），又觀看大量的電影以擴展詞彙量。因此，當你讀累了，就看部電影吧！'),
     
    ('subsection', 'Table 4: Word List Level and Reading Requirements', '表4：字詞等級與閱讀需求對照表'),
    ('listitem', '2nd 1000: 200,000 words | 33 mins/week (7 mins/day)', '第二個1000字：200,000字 | 每週33分鐘（每天7分鐘）'),
    ('listitem', '3rd 1000: 300,000 words | 50 mins/week (10 mins/day)', '第三個1000字：300,000字 | 每週50分鐘（每天10分鐘）'),
    ('listitem', '4th 1000: 500,000 words | 1 hr 23 mins/week (17 mins/day)', '第四個1000字：500,000字 | 每週1小時23分鐘（每天17分鐘）'),
    ('listitem', '5th 1000: 1,000,000 words | 2 hrs 47 mins/week (33 mins/day)', '第五個1000字：1,000,000字 | 每週2小時47分鐘（每天33分鐘）'),
    ('listitem', '6th 1000: 1,500,000 words | 4 hrs 10 mins/week (50 mins/day)', '第六個1000字：1,500,000字 | 每週4小時10分鐘（每天50分鐘）'),
    ('listitem', '7th 1000: 2,000,000 words | 5 hrs 33 mins/week (1 hr 7 mins/day)', '第七個1000字：2,000,000字 | 每週5小時33分鐘（每天1小時7分鐘）'),
    ('listitem', '8th 1000: 2,500,000 words | 6 hrs 57 mins/week (1 hr 23 mins/day)', '第八個1000字：2,500,000字 | 每週6小時57分鐘（每天1小時23分鐘）'),
    ('listitem', '9th 1000: 3,000,000 words | 8 hrs 20 mins/week (1 hr 40 mins/day)', '第九個1000字：3,000,000字 | 每週8小時20分鐘（每天1小時40分鐘）')
]


# ================= 3. READING CAN SERIOUSLY DAMAGE YOUR IGNORANCE DATA =================
damage_content = [
    ('section', 'Unit Introduction', '單元簡介'),
    ('paragraph',
     'This unit is composed of three sections: the benefits of reading, the extensive reading approach in language learning and the academic quotation.',
     '本單元由三個部分組成：閱讀的好處、語言學習中的泛讀方法以及學術引用。'),
    ('paragraph',
     '“Reading can seriously damage your ignorance.”',
     '「閱讀會嚴重損害你的無知。」'),
    ('paragraph',
     'Generally speaking, the words ‘ignore (verb) and ignorance (noun)’ have negative connotation. However, when I first learned the sentence “Reading can seriously damage your ignorance”, I fell in love with it, even with the word ‘ignorance’. This sentence contains two negative words, ‘damage’ and ‘ignorance’, but successfully the person who had created this sentence turned these two words into positive thoughts, which amazed me. So far, I still cannot find the origin of the sentence. (If sometime in the future you come across the information, please share it with me.) Reading is of paramount importance in our life, for we read both for information and pleasure. For instance, we read newspapers to know what happens in the world or websites for information for work. This is what I call ‘read for information’. We read for recreation as well, that is, we read for fun in our leisure time. We read comic books, magazines, novels, tweets of posts on our mobile devices etc. in our own free time. This is “reading for entertainment”, we do them to relax and for enjoyment. Some people are born natural readers; they enjoy reading so much that they are addicted to it, while others don’t, which is totally acceptable. This difference regarding the reading habits adds the variety of people.',
     '一般來說，『ignore（動詞）』和『ignorance（名詞）』這兩個詞具有負面含意。然而，當我第一次學到「閱讀會嚴重損害你的無知」這句話時，我愛上了它，即使裡面有『無知』這個詞。這句話包含了兩個負面單字，『損害』和『無知』，但創造這句話的人成功地將這兩個詞轉化為積極的想法，這讓我感到驚訝。到目前為止，我仍然找不到這句話的來源。（如果將來您遇到相關信息，請與我分享。）閱讀在我們的生活中至關重要，因為我們閱讀既是為了獲取信息，也是為了獲得樂趣。例如，我們閱讀報紙以了解世界上發生的事情，或者閱讀網站以獲取工作信息。這就是我所說的「為獲取信息而閱讀」。我們也為了消遣而閱讀，也就是在閒暇時間為了好玩而閱讀。我們在空閒時間閱讀漫畫書、雜誌、小說、行動裝置上的推文等。這就是「為娛樂而閱讀」，我們閱讀它們是為了放鬆和享受。有些人天生就是閱讀者，他們非常喜歡閱讀以至於上癮，而有些人則不喜歡，這完全是可以接受的。這種關於閱讀習慣的差異增加了人們的多樣性。'),
     
    ('section', 'Benefits of Reading', '閱讀的好處'),
    ('paragraph',
     'Nevertheless, I still would like to continue promoting reading by talking about its benefits and then introduce an enjoyable method for learning English through reading since this course is about learning culture knowledge through ‘reading’. Therefore, in this unit, we will learn the benefits of reading and extensive reading approach first, and in the next unit, we will discuss what we should read and how much we should read. Afterall, the reading culture is an important element of a culture, too.',
     '儘管如此，我仍然希望通過談論閱讀的好處來繼續推廣閱讀，然後介紹一種通過閱讀學習英語的愉快方法，因為本課程是關於通過『閱讀』來學習文化知識的。因此，在本單元中，我們將首先學習閱讀的好處和泛讀方法，在下一個單元中，我們將討論我們應該閱讀什麼以及我們應該閱讀多少。畢竟，閱讀文化也是一個文化的重要元素。'),
    ('paragraph',
     'Reading is a skill that we try to develop since childhood. We learned how to read Chinese first through picture books with few words, then gradually through textbooks which contain longer texts, such as proses, poems, classical literatures, and other genres. Reading English as your second language should probably follow the same path. Please recall the first time you read your ‘homerun book’ (Trelease, 2001), the first book you successfully finished in Chinese, you must have had the ‘sense of completion and satisfaction’. We need the same experience in English reading. This kind of initial successful reading experience resulted in positive attitudes toward reading, the growth of motivation to read, and fed back into later reading experiences, resulting in more gains in reading ability, positive attitudes, motivation and enjoyment (Chiang, 2009:56-57).',
     '閱讀是我們從小就努力培養的一項技能。我們首先通過字數很少的圖畫書學習如何閱讀中文，然後逐漸通過教科書閱讀更長的文本，例如散文、詩歌、古典文學和其他體裁。英語作為第二語言的閱讀可能也應該遵循同樣的路徑。請回想一下您第一次閱讀「全壘打書」（Trelease, 2001）時的經歷——這是您用中文成功讀完的第一本書，您一定有過『成就感和滿足感』。我們在英語閱讀中也需要同樣的體驗。這種最初的成功閱讀體驗帶來了對閱讀的積極態度、閱讀動機的增長，並回饋到後來的閱讀體驗中，從而帶來閱讀能力、積極態度、動機和樂趣的更多收穫（Chiang, 2009）。'),
     
    ('pagebreak',),
    
    ('section', 'The Extensive Reading Approach', '泛讀教學法'),
    ('paragraph',
     'The abovementioned experience of learning to read through reading is what we called ‘Extensive Reading Approach’. It is an approach in EFL in which learners read a lot of materials at their level in the new language. The learners should choose their own reading materials and read them, mainly, independently or sometimes with necessary help when needed. The learners will read for general and overall meaning, and they read for information and enjoyment. If the learners find the materials boring, difficult or uninteresting, they can stop reading that book immediately. Learners are also encouraged to expand their reading comfort zone once they find the materials they are reading rather easy (Bamford & Day, 2004). Many successful Extensive Reading programs have been carried out, thus it is an acknowledged approach worldwide.',
     '上述通過閱讀學習閱讀的體驗就是我們所說的「泛讀方法（Extensive Reading Approach）」。這是在英語作為外語（EFL）中的一種方法，學習者在該方法中閱讀大量適合其水平的新語言材料。學習者應該選擇自己的閱讀材料並進行閱讀，主要是在沒有輔助的情況下獨立閱讀，或者有時在需要時獲得必要的幫助。學習者將為了大意和整體含義而閱讀，他們為了信息和樂趣而閱讀。如果學習者覺得這些材料無聊、困難或無趣，他們可以立即停止閱讀那本書。學習者也被鼓勵一旦發現他們正在閱讀的材料相當簡單，就擴展他們的閱讀舒適區（Bamford & Day, 2004）。許多成功的泛讀項目已經開展，因此這是一項在全球範圍內獲得認可的方法。'),
    ('paragraph',
     'This approach is also mentioned in some of the English courses at National Open University. Therefore, I think it is better to include more information and clarify the spirit of this approach more clearly. Day and Bamrofd (1998; Chiang, 2009) list the characteristics found in successful extensive reading programs:',
     '此方法在國立空中大學的一些英語課程中也有提及。因此，我認為最好納入更多信息，並更清楚地闡明該方法的精神。Day 和 Bamford (1998; Chiang, 2009) 列出了成功泛讀計劃中發現的特徵：'),
     
    ('listitem', '1. Students read as much as possible, probably in and definitely ‘out’ of the classroom.', '1. 學生儘可能多地閱讀，可能在課堂內，但絕對在課堂外。'),
    ('listitem', '2. A variety of materials on a wide range of topics is available so as to encourage reading for different reasons and in different ways.', '2. 提供涵蓋廣泛主題的多種材料，以鼓勵出於不同原因和以不同方式進行閱讀。'),
    ('listitem', '3. Students select what they want to read and have the freedom to stop reading materials that fail to interest them.', '3. 學生選擇他們想讀的內容，並有自由停止閱讀無法吸引他們的材料。'),
    ('listitem', '4. The purposes of reading are usually related to pleasure, information, and general understanding. These purposes are determined by the nature of the materials and the interests of the learner.', '4. 閱讀的目的通常與樂趣、信息和一般理解有關。這些目的由材料的性質和學習者的興趣決定。'),
    ('listitem', '5. Reading is its own reward. There are few or no follow-up exercises after reading.', '5. 閱讀本身就是回報。閱讀後很少或沒有後續練習。'),
    ('listitem', '6. Reading materials are well within the linguistic competence of the students in terms of vocabulary and grammar. Dictionaries are rarely used while reading because the constant stopping to look up words makes fluent reading difficult.', '6. 閱讀材料在詞彙和語法方面完全在學生的語言能力範圍內。閱讀時很少使用字典，因為不斷停下來查字會使流利閱讀變得困難。'),
    ('listitem', '7. Reading is individual and silent, at the student’s own pace, and, outside classroom, done when and where the student chooses.', '7. 閱讀是獨立且無聲的，按照學生自己的節奏進行，並且在課堂外，在學生選擇的時間和地點進行。'),
    ('listitem', '8. Reading speed is usually faster rather than slower as students read books and other material they find easily understandable.', '8. 閱讀速度通常較快而非較慢，因為學生閱讀的是他們發現容易理解的書籍和其他材料。'),
    ('listitem', '9. Teacher/parents orient students to the goals of the program, explain methodology, keep track of what each student reads, and guide students in getting the most out of the program.', '9. 教師/家長引導學生了解該計畫的目標，解釋方法，追蹤每個學生的閱讀情況，並指導學生從該計畫中獲得最大收益。'),
    ('listitem', '10. The teacher/parent is a role model of a reader for students – an active member of the classroom reading community, demonstrating what it means to be a reader and the rewards of being a reader.', '10. 教師/家長是學生閱讀的榜樣——是課堂閱讀社群的活躍成員，展示了作為一名閱讀者的意義以及作為一名閱讀者的回報。'),
    
    ('paragraph',
     'Being able to read in English is necessary for we need to do it to access information, operate machines and computers as well as entertain … Reading brings many good things to people who read in large quantity in a new language (Chiang, 2009:43). Many good things happen to students who read a great deal in the new language. Research studies show that they become better and more confident readers, they write better, their listening and speaking abilities improve, and their vocabulary gets richer. In addition, they develop positive attitudes towards and increase motivation to studying the new language (Bamford & Day, 2004:1). We can only learn to read by reading (Smith, 1973) and only reading promotes reading – the more students read, the more their vocabulary grow, the more words they can read, the more reading they can do. There does not seem to be a shortcut to becoming a fluent reader, according to a large amount of studies.',
     '能夠閱讀英語是必要的，因為我們需要用它來獲取信息、操作機器和電腦以及娛樂……閱讀給以新語言進行大量閱讀的人帶來了許多好處（Chiang, 2009）。許多好事會發生在大量閱讀新語言材料的學生身上。研究表明，他們會成為更好、更自信的閱讀者，寫作能力提高，聽力和口語能力改善，詞彙量也變得更豐富。此外，他們會對學習新語言建立積極態度並增加動機（Bamford & Day, 2004）。根據大量研究，要成為流利的閱讀者似乎沒有捷徑。'),
    ('paragraph',
     'Reading a book should be similar to watching a good science fiction movie. It can take you to any time and space you want to be. It does not have to be like the Chinese saying ‘no pain, no gain’. Many of us knew the story about a scholar who studied bitterly and had to stick an awl in his calf to wake himself up in the middle of the night. If the book is right, then a reader is most likely to stay up in that ‘literal space and world’ until one finishes the book and knows the ending. Readers ought to love the books and read on without any bitterness.',
     '閱讀一本書應該類似於看一部好的科幻電影。它可以帶你去任何你想去的時空。它不需要像中國俗話說的『書山有路勤為徑，學海無涯苦作舟』。我們中許多人都知道關於一個學者苦讀、不得不在半夜將錐子刺入小腿（頭懸梁，錐刺股）以喚醒自己的故事。如果書選得對，那麼讀者極有可能在那個『字面空間和世界』中熬夜，直到讀完書並知道結局。讀者應該熱愛書籍並在沒有任何痛苦的情況下繼續閱讀。'),
     
    ('section', 'Academic Quotations', '學術引用規範'),
    ('paragraph',
     'Finally, let us learn about the ‘reference’ or ‘work cited’ in the text of this unit. You see many examples such as “(Trelease, 2001)” and then found the smaller number hanging on the upper right. This indicates the source of the information that I have used. So, at the bottom of the page, you will find the ‘footnote’ like this:\n1 Trelease, J. (2001). The read-aloud handbook (4th ed.). New York: Penguin.\nThis gives further detailed information about the piece of information I used, including the author, the year of publishing, the book title and edition, place and company of publication. The order or styles are regulated, but there are different styles academically, such as APA style, MLA style etc. Learning how to quote correctly is important for academic work; otherwise, you will violate plagiarism and it is a serious issue in the academic world. You must add the reference where you have used the citation (in-text citation), and then present the whole reference in the middle of the text, or at the end of the writing in the alphabetical order by the author’s last name.',
     '最後，讓我們來學習本單元文本中的「參考文獻」或「引用作品」。您會看到許多例子，例如「(Trelease, 2001)」，然後在右上角發現懸掛的小數字。這表明了我所使用的信息的來源。因此，在頁面底部，您會找到這樣的「腳註」：\n1 Trelease, J. (2001). 《朗讀手冊》（第四版）. 紐約：企鵝出版社。\n這提供了關於我所使用信息的進一步詳細信息，包括作者、出版年份、書名和版本、出版地點和公司。順序或樣式是受規律限制的，但學術上有不同的樣式，例如 APA 樣式、MLA 樣式等。正確引用對於學術工作非常重要；否則，您將違反剽竊，這在學術界是一個嚴肅的問題。您必須在使用了引用的地方添加參考文獻（文中引用），然後在文本中間或在寫作結束時按作者姓氏的字母順序呈現整個參考文獻。')
]


# ================= 4. LANGUAGE: POTATO, POTATO DATA =================
potato_content = [
    ('section', 'Lead-in Dialogue', '導入對話'),
    ('paragraph',
     'Are you assuming that this unit is about food like potato and vegetables? It is not. You will not believe me if I tell you my next sentence is ‘tomato, tomato’. You definitely will say: We know these words already. Tell us something we don’t know!! Of course I will, because this is exactly why this course is designed for.',
     '你是否認為本單元是關於馬鈴薯和蔬菜等食物的？它不是。如果我告訴你我的下一句話是『tomato, tomato（番茄，番茄 / 一回事）』，你一定不會相信我。你肯定會說：我們已經知道這些字了。告訴我們一些我們不知道的事吧！我當然會，因為這正是本課程設計的目的。'),
    ('paragraph',
     'Jane: Emma!!! I need some help!! Have you got a minute?\nEmma: I’m busy with my book report, but… ok, what’s the matter?\nJane: I’m going out with the guy Charles, you know from last week, tonight for dinner. I need your opinion on my top! Do you think I should wear this dark blue sweater which shows the color of my eyes more or this black one which makes me look thinner?\nEmma: What? That’s your problem? Are you crazy? Who cares? Potayto, potahto, it’s the same thing. Who cares? They look the same in the dark anyway. I can’t believe you interrupted me for this (sigh….)\nJane: Well, thank you very much for being so helpful. Your opinion really matters to me OK? Remember, we are BFF!!\nEmma: Ok, fine, the black one. It can never go wrong with the black.',
     '簡：艾瑪！！！我需要一些幫助！！你有空嗎？\n艾瑪：我正忙著寫讀書報告，不過……好吧，什麼事？\n簡：我今晚要和上週那個叫查爾斯的傢伙出去吃晚飯。我需要你對我的上衣提點意見！你覺得我應該穿這件顯得我眼睛顏色的深藍色毛衣，還是穿這件顯得我更瘦的黑色毛衣？\n艾瑪：什麼？那是你的問題？你瘋了嗎？誰在乎？Potayto, potahto（馬鈴薯，馬鈴薯 / 一回事），都是一樣的。誰在乎？反正暗處看起來都一樣。我不敢相信你為這事打斷我（嘆氣……）\n簡：好吧，非常感謝你這麼有幫助。你的意見對我很重要好嗎？記住，我們是死黨！！\n艾瑪：好吧，行了，黑色的那件。穿黑色永遠不會出錯。'),
     
    ('section', 'Linguistics & Language Change', '語言學與語言演變'),
    ('paragraph',
     'Many of us know that English, through history, has developed slightly in different parts of the world. In the study of Linguistics, we linguists study various languages, researching a language through phonology, morphology, syntax, semantics and applications. Phonology is the study of sounds, while morphology looks into the structure and root of a word. Syntax is the study of sentence pattern, i.e. grammar, whereas semantics is about the meaning of words in different levels, such as word, phrase and sentence, discourse analysis and pragmatics. Applied linguistics covers how a language is used from even wider perspectives, such as psycho-linguistics, socio-linguistics, language change, language acquisition, language learning and teaching etc. These proper terms seem difficult, but we do not need to learn everything now. We only need to learn what area they refer to for now.',
     '我們中許多人都知道，在歷史上，英語在世界不同地區的發展略有不同。在語言學研究中，我們語言學家研究各種語言，通過語音學、形態學、句法學、語意學和應用來研究一門語言。語音學是研究聲音的學科，而形態學則研究單字的結構和字根。句法學是研究句子模式的學科，即語法，而語意學是關於不同層次單字含義的學科，例如單字、片語和句子、語篇分析和語用學。應用語言學涵蓋了從更廣泛的角度如何使用語言，例如心理語言學、社會語言學、語言演變、語言習得、語言學習和教學等。這些專有名詞看起來很難，但我們現在不需要學習所有內容。我們現在只需要了解它們指的是什麼領域。'),
    ('paragraph',
     'Do you think languages change fast? Some might say ‘yes’ because quite often we need to learn new words or phrases in order to keep up with the world, such as ‘IG’ for “Instagram” and ‘KOL’ for “Key Opinion Leader” in recent years since the social media become our new normal. Nevertheless, if we think about this more carefully, these are just phrases. So, words come and go, but one thing remains relatively stable, which is the grammar of a language. Take English as an example, even though the grammar of English has changed to a certain extent from Middle English, the core of the grammar did not change much. That is, the structure of the grammar remains the same, while the vocabulary could change more easily, generally speaking. Back in the mid 1990s, the Internet has just started to become popular, which increased the use of email for correspondence. Since then, words like ‘download’, ‘broadband’, and ‘online’ were invented with the advancement of technology. These were the evidence of how vocabulary and slangs could change over time more easily than grammar.',
     '你認為語言變化快嗎？有些人可能會說『快』，因為我們經常需要學習新的單字或片語以跟上世界的腳步，例如近年來由於社群媒體成為我們的新常態，『IG』代表「Instagram」，『KOL』代表「關鍵意見領袖」。然而，如果我們更仔細地思考這一點，這些只是流行語。因此，單字來來去去，但有一件事保持相對穩定，那就是一門語言的語法。以英語為例，儘管英語語法從中古英語起發生了一定程度的變化，但語法的核心並沒有太大變化。也就是說，語法的結構保持不變，而一般來說，詞彙更容易發生變化。早在1990年代中期，網際網路剛剛開始流行，這增加了電子郵件用於通信的頻率。從那時起，隨著技術的進步，『下載（download）』、『寬頻（broadband）』和『線上（online）』等單字被發明出來。這些都是詞彙和俚語隨時間推移比語法更容易發生變化的證據。'),
     
    ('pagebreak',),
    
    ('section', 'Sounds of Language: US vs. UK Pronunciation', '語言的聲音：美式與英式發音'),
    ('paragraph',
     'Now, let’s get into the main topic of this unit, the sounds of language. We know that American English and British English sound different. (If you have not had any contact with British English, you could watch a movie of Harry Potter and listen to them carefully.) In fancier words, we can say the ‘pronunciations’ of them are different. Based on my English learning and teaching experience and to put things more simply, the main differences are the vowels and the curling tongue. In Taiwan, English learners often learn through KK phonetic symbols, which is an effective way to learn pronunciation. Once you master the symbols, you can pronounce the word rather correctly. KK phonetic symbols are adopted in American English and internationally. British English (or English English) usually takes the DJ phonetic symbols and includes some vowels that either do not exist or are pronounced differently, which leads to the different pronunciation of a word. For instance, the ~er sound /ɜ/ in KK phonetic symbol requires the curl up of the tongue, whereas in British English, the tongue is comparatively flat. In addition, the /r/ in the word ‘farm’ is less obvious than that in American English. Other differences regarding vowels or even diphthongs exist, such as the vowel in ‘hot’ and ‘water’ /ɒ/ and the diphthong /ɔɪ/. Due to the different phonetic systems, we have different pronunciations of the same words. In the end, the word ‘potato’ has two pronunciations in the English language, potayto and potahto, referring to the same word. So, in English, when we say ‘potayto, potahto’, we mean the two things under discussion are the same thing, with minor tiny unimportant differences between them.',
     '現在，讓我們進入本單元的主題，語言的聲音。我們知道美式英語和英式英語聽起來不同。（如果您還沒有接觸過英式英語，您可以觀看一部《哈利波特》的電影並仔細聆聽。）用更精緻的話來說，我們可以說它們的『發音』不同。根據我的英語學習和教學經驗，更簡單地說，主要的區別在於母音和捲舌音。在台灣，英語學習者經常通過 KK 音標進行學習，這是學習發音的有效方法。一旦您掌握了音標，您就可以相當正確地讀出單字。KK 音標在美式英語和國際上被採用。英式英語（或英國英語）通常採用 DJ 音標，並包括一些要麼不存在要麼發音不同的母音，這導致了單字的不同發音。例如，KK音標中的~er音 /ɜ/需要舌頭捲起，而在英式英語中，舌頭相對較平。此外，單字『farm』中的 /r/ 在美式英語中比在英式英語中更不明顯。還存在關於母音甚至雙母音的其他差異，例如『hot』和『water』中的母音 /ɒ/ 以及雙母音 /ɔɪ/。由於不同的語音系統，我們對相同的單字有不同的發音。最後，『potato』這個字在英語中有兩種發音，potayto 和 potahto，指的是同一個字。所以，在英語中，當我們說『potayto, potahto』時，我們是指所討論的兩件事是一回事，它們之間只有微不足道的不重要差異。'),
     
    ('section', 'Song: Let’s Call the Whole Thing Off', '經典歌曲：讓我們取消這一切（不分手了）'),
    ('paragraph',
     'This English idiom or we can say expression came from a song “Let’s call it off” (officially "Let\'s Call the Whole Thing Off") in the movie “Shall We Dance” long time ago in 1937. The song was sung by Ella Fitzgerald and Louis Armstrong. It was set in a duet style and the main characters of the song, a couple (yet-to-be couple) were arguing whether the relationship should go on over their different pronunciations of ‘words’, which for sure was not an appropriate reason to stop a relationship. However, the song pointed out if the two could not agree with each other on something this subtle, how they should continue the relationship in the future. Fortunately, we see in the end of the song, they decided to ‘call the whole thing off’, which meant that they decided to stay together! Hooray! What a relief! It’s a happy ending for everyone. You can find many different examples like the ‘potayto, potahto’, ‘tomayto, tomahto’, ‘either’, ‘neither’, ‘pajama’, ‘oyster’.',
     '這個英語成語或者我們可以說表達方式來自很久以前1937年電影《隨我起舞》（Shall We Dance）中的一首歌《Let’s Call the Whole Thing Off》。這首歌由艾拉·費茲潔拉（Ella Fitzgerald）和路易斯·阿姆斯壯（Louis Armstrong）以二重唱的形式演唱。歌曲的男女主角，一對即將成為戀人的情侶，正在為他們不同的單字『發音』爭論這段關係是否應該繼續下去，這無疑不是停止一段關係的合適理由。然而，這首歌指出，如果兩個人在如此微妙的事情上都無法達成一致，那麼他們未來應該如何繼續這段關係。幸運的是，我們在歌曲的結尾看到，他們決定『call the whole thing off（取消取消 / 不分手了）』，這意味著他們決定待在一起！萬歲！真令人鬆了一口氣！這對每個人來說都是一個快樂的結局。您可以找到許多不同的例子，如『potayto, potahto』、『tomayto, tomahto』、 『either』、 『neither』、 『pajama』、 『oyster』。'),
     
    ('subsection', 'Song Lyrics', '歌詞對照'),
    ('listitem', 'You say either and I say eye-ther\nYou say neither and I say n-eye-ther\nEither, eye-ther, neither, n-eye-ther\nLet’s call the whole thing off.', '你說 either，我說 eye-ther\n你說 neither，我說 n-eye-ther\nEither, eye-ther, neither, n-eye-ther\n讓我們把整件事取消吧。'),
    ('listitem', 'You like potato and I like pot-ah-to\nYou like tomato and I like tom-ah-to\nPotato, pot-ah-to, tomato, to-mah-to,\nLet’s call the whole thing off', '你喜歡 potato，我喜歡 pot-ah-to\n你喜歡 tomato，我喜歡 tom-ah-to\nPotato, pot-ah-to, tomato, to-mah-to,\n讓我們把整件事取消吧'),
    ('listitem', 'So if you like pyjamas and I like pyj-ah-mas\nI’ll wear pyjamas and give up py-jah-mas\nFor we know we need each other so we\nBetter call the calling off off\nLet’s call the whole thing off.', '如果你喜歡 pyjamas，而我喜歡 pyj-ah-mas\n我會穿 pyjamas，放棄 py-jah-mas\n因為我們知道彼此需要，所以我們\n最好不要取消這段感情\n讓我們把取消的事情取消吧（別分手了）。'),
     
    ('pagebreak',),
    
    ('section', 'American vs. British English Vocabulary', '美式與英式字彙對照'),
    ('listitem', 'French fries (American) -> chips (British) | 炸薯條', 'French fries (美式) -> chips (英式) | 炸薯條'),
    ('listitem', 'fall (American) -> autumn (British) | 秋天', 'fall (美式) -> autumn (英式) | 秋天'),
    ('listitem', 'attorney (American) -> solicitor (British) | 律師', 'attorney (美式) -> solicitor (英式) | 律師'),
    ('listitem', 'cookie (American) -> biscuit (British) | 餅乾', 'cookie (美式) -> biscuit (英式) | 餅乾'),
    ('listitem', 'janitor (American) -> caretaker (British) | 管理員/工友', 'janitor (美式) -> caretaker (英式) | 管理員/工友'),
    ('listitem', 'drugstore (American) -> chemist’s, pharmacist’s (British) | 藥局/藥妝店', 'drugstore (美式) -> chemist’s, pharmacist’s (英式) | 藥局/藥妝店'),
    ('listitem', 'apartment (American) -> flat (British) | 公寓', 'apartment (美式) -> flat (英式) | 公寓'),
    ('listitem', 'yard (American) -> garden (British) | 庭院/花園', 'yard (美式) -> garden (英式) | 庭院/花園'),
    ('listitem', 'vacation (American) -> holiday (British) | 假期', 'vacation (美式) -> holiday (英式) | 假期'),
    ('listitem', 'elevator (American) -> lift (British) | 電梯', 'elevator (美式) -> lift (英式) | 電梯'),
    ('listitem', 'truck (American) -> lorry (British) | 卡車', 'truck (美式) -> lorry (英式) | 卡車'),
    ('listitem', 'sidewalk (American) -> pavement (British) | 人行道', 'sidewalk (美式) -> pavement (英式) | 人行道'),
    ('listitem', 'mail (American) -> post (British) | 郵件', 'mail (美式) -> post (英式) | 郵件'),
    ('listitem', 'line (American) -> queue (British) | 排隊', 'line (美式) -> queue (英式) | 排隊'),
    ('listitem', 'subway (American) -> underground railway/tube (British) | 地鐵', 'subway (美式) -> underground railway/tube (英式) | 地鐵')
]

if __name__ == "__main__":
    # Generate the 4 detailed bilingual PDFs
    build_pdf("to_be_or_not_to_be_bilingual.pdf", "Unit: To Be or Not to Be", to_be_content)
    build_pdf("how_difficult_read_bilingual.pdf", "Unit: How Difficult and How Much Should I Read?", difficulty_content)
    build_pdf("damage_ignorance_bilingual.pdf", "Unit: Reading Can Seriously Damage Your Ignorance", damage_content)
    build_pdf("potato_potato_bilingual.pdf", "Unit: Language: Potato, Potato", potato_content)
    print("Done generating all 4 newest detailed bilingual PDFs.")
