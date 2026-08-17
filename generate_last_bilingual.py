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
    
    style_en_lyrics = ParagraphStyle(
        'EnLyrics',
        parent=styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#374151'),
        leftIndent=20,
        spaceAfter=2
    )
    
    style_zh_lyrics = ParagraphStyle(
        'ZhLyrics',
        parent=styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#4B5563'),
        leftIndent=20,
        spaceAfter=6
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
            
        elif item_type == 'lyrics':
            en_lines = item[1].split('\n')
            zh_lines = item[2].split('\n')
            for en_line, zh_line in zip(en_lines, zh_lines):
                if en_line.strip():
                    story.append(Paragraph(en_line, style_en_lyrics))
                if zh_line.strip():
                    story.append(Paragraph(zh_line, style_zh_lyrics))
            story.append(Spacer(1, 4))
            
        elif item_type == 'pagebreak':
            story.append(PageBreak())
            
        elif item_type == 'spacer':
            story.append(Spacer(1, item[1]))

    def page_cb(canvas, doc):
        make_header_footer(canvas, doc, doc_title)

    doc.build(story, onFirstPage=page_cb, onLaterPages=page_cb)
    print(f"Generated PDF: {filename}")


# ================= 1. FAMILY COMMUNICATION DATA =================
family_content = [
    ('section', 'Unit Purpose', '單元目的'),
    ('paragraph',
     'The purpose of this unit is twofold. We want to talk about some family culture that I observed in the United Kingdom and then introduce some picture books that I as an adult also enjoy reading. As a matter of fact, this unit and the following two units will introduce different types of books which are often used in English learning, including picture books, young adult literature (unit 14) and graded readers (unit 15).',
     '本單元的目的有兩個。我們想談談我在英國觀察到的一些家庭文化，然後介紹一些我作為成年人也喜歡閱讀的繪本。事實上，本單元和接下來的兩個單元將介紹英語學習中經常使用的不同類型的書籍，包括繪本、青少年文學（第14單元）和分級讀物（第15單元）。'),
     
    ('section', 'English Picture Books Introduction', '英文繪本引言'),
    ('paragraph',
     'First of all, I would like to start with the picture books. In my childhood, I was lucky to grow up among books, literally among books. We had three bookstores downstairs, and I was allowed to access whenever the stores were open. Therefore, I did not have to buy many books for it was an ‘all-you-can-read’ book buffet for free to me. I did not have any picture books that I could recall, not to mention any English picture books. I grew to love English picture books when I started my doctoral study. Even though I read English with comparative fluency than most of the people, I still prefer not to read difficult texts for entertainment, such as newspaper or classic novels. I love light readings. So, when I started to research on children’s literature, which covers a wide range of stories, books, and so on, I fell in love with classic picture books (even though I do not have any child) and started collecting them. Who doesn’t like books with large cute pictures with only a few lines to read? After I discovered the world of picture books at the university library, I went straight to the biggest bookstore “Waterstones” and bought my very first English picture book, There was an old lady who swallowed a fly, illustrated by Pam Adams and published by Child’s Play International first published in 1973 and reprinted in 2003.',
     '首先，我想從繪本開始。在我的童年，我很幸運能在書堆中長大，字面意義上的書堆中。我們樓下有三家書店，只要書店開門，我就可以進去。因此，我不需要買很多書，因為對我來說，這是一個免費的「全書自助餐」。在我的記憶中，我沒有任何繪本，更不用說英語繪本了。當我開始博士研究時，我開始熱愛英語繪本。儘管我讀英語比大多數人流利，但我仍然不喜歡讀困難的文本消遣，例如報紙或經典小說。我喜歡輕鬆的閱讀。所以，當我開始研究兒童文學時，它涵蓋了廣泛的故事、書籍等，我愛上了經典繪本（儘管我沒有任何孩子）並開始收集它們。誰不喜歡字少、圖大又可愛的書呢？在大學圖書館發現了繪本的世界後，我直奔最大的書店「Waterstones」，買了我生平第一本英文繪本《老婆婆吞了一隻蒼蠅》（There was an old lady who swallowed a fly），由 Pam Adams 繪製，並由 Child’s Play International 於1973年首次出版，並於2003年重印。'),
    ('paragraph',
     'Later, I bought my favorite, Not now, Bernard, written and illustrated by David McKee and first published in Great Britain in 1980 by Andersen Press, which means the book has been around for over 40 years, classic!!!',
     '後來，我買了我最喜歡的書《現在不行，伯納》（Not now, Bernard），由大衛·麥基（David McKee）撰寫和繪製，並於1980年由安徒生出版社在英國首次出版，這意味著這本書已經存在了40多年，堪稱經典！！！'),
    ('paragraph',
     'Picture books and bedtime story reading are tightly connected in the western culture. Many parents take their children to libraries, and schools encourage reading too. The education system also promotes reading through class reading or sustained silent reading, which is the extensive reading approach we mentioned before.',
     '繪本和床邊故事閱讀在西方文化中緊密相連。許多父母帶孩子去圖書館，學校也鼓勵閱讀。教育系統也通過課堂閱讀或持續默讀（SSR）來促進閱讀，這就是我們之前提到的泛讀方法。'),
     
    ('pagebreak',),
    
    ('section', 'Not Now, Bernard & Family Communication', '《現在不行，伯納》與家庭溝通'),
    ('paragraph',
     'As you can see in the cover of the book, the story has two characters, a little boy named Bernard and a monster. One day, Bernard, trying to attract his parents’ attention but failed, went into the garden and met a monster. The monster ate Bernard, came into the house, and lived Bernard’s life. Bernard’s parents did not even notice the monster replacing their son. The monster ended up getting lots of “Not now, Bernard”. From the story and illustrations, we observe the life of family at the time, for example, Bernard’s mother put the dinner in front of the television, showing us that family dinner was not a routine in the story as well as the milk before bed. I am particularly amused by the vivid facial expressions of the monster when the monster said “But I’m a monster” in bed with the milk in hand.',
     '正如你在書的封面所看到的，故事有兩個角色，一個名叫伯納的小男孩和一個怪物。一天，伯納試圖吸引父母的注意但失敗了，他走到花園裡遇到了一個怪物。怪物吃掉了伯納，走進屋子，過著伯納的生活。伯納的父母甚至沒有注意到怪物取代了他們的兒子。怪物最終得到了很多「現在不行，伯納」。從故事和插圖中，我們觀察到當時家庭的生活，例如，伯納的母親把晚餐放在電視機前，向我們展示了故事中家庭晚餐不是常規，睡前的牛奶也是如此。當怪物手拿牛奶在床上說「但我是一個怪物」時，怪物生動的臉部表情特別讓我感到好笑。'),
    ('paragraph',
     'The story also showed us that parents could misbehave by ignoring their children and turn them into little monsters (Ferguson, 2020). Or, as Hancock (2014) wrote, this book demonstrates that “parents can be naughty too” and that “when we don’t listen to people, monsters can take over.”',
     '故事還向我們表明，父母可能會因為忽視孩子並將他們變成小怪物而表現不佳（Ferguson, 2020）。或者，正如 Hancock（2014年）所寫，這本書表明「父母也可以很調皮」，而且「當我們不聽人說話時，怪物就會接管。」'),
    ('subsection', 'Bernard’s Dialogue', '伯納對話錄'),
    ('listitem', 'Child: Mum, look!!\nParent: Not now, dear!', '孩子：媽媽，看！！\n家長：現在不行，寶貝！'),
    ('listitem', 'Child: But…… look!\nParent: NOT NOW, dear!!!\nChild: ……', '孩子：但是……看！\n家長：現在不行，寶貝！！！\n孩子：……'),
    
    ('paragraph',
     'How often do we hear or say this in the daily life? I have a very dear friend who is probably the best parent I have ever seen in life. She never got loud or mad at her children when I met them at the age of 12 and 14. She always listened to the children, and they had dinner together most of the time. When they sat and ate, books, phones or TVs were not allowed; they focused on how their days were and on each other, even for just a half hour. I know this because I lived with them for nearly two years and watched how she and her husband took care of their children, who turn out to become excellent adults now. In situations like the conversation above, she would always answered: “Yes, dear. What is it?”',
     '我們在日常生活中多頻繁地聽到或說這句話？我有一個非常要好的朋友，她可能是我一生中見過最好的家長。當我在孩子們12歲和14歲時遇見他們時，她從不對孩子們大聲喧嘩或生氣。她總是傾聽孩子們的聲音，他們大部分時間都在一起吃晚餐。當他們坐下來吃飯時，書本、手機或電視都是不允許的；他們專注於彼此的一天是怎麼過的，甚至只有半小時。我知道這一點，因為與他們一起生活了將近兩年，看著她和她的丈夫如何照顧他們的孩子，他們現在都成為了優秀的成年人。在像上面那樣的談話情況下，她總是會回答：「是的，寶貝。怎麼了？」'),
    ('paragraph',
     'Recently, new illustrations of the book have been created to reflect the daily life of families in the age of technology. Digital devices, such as smartphones and tablets are added to the new version. The author, David McKee, aged 85, revealed to the Observer that “He thinks listening to children is one of the most important thing a parent can do – and during the lockdown, when children are isolated from their teachers and friends, it is even more important.” He thinks good parents should make sure that they listen to their children, or at least, should take time to explain to their children why they are unavailable at that moment. McKee also thinks that one of the most important point is that neither Bernard nor the monster understand why the parents just keep on ignoring them and even the monster does not know how to ‘handle the situation’. However, parents are not the only people who get to say ‘not now’ nowadays, children say ‘not now’ to their parents, too, McKee noticed and pointed out in the interview. So, family communication is something that needs a lot of attention and deserves working on (Ferguson, 2020).',
     '最近，這本書創作了新的插圖，以反映技術時代家庭的日常生活。智慧型手機和平板電腦等數位設備被添加到新版本中。作者大衛·麥基，85歲，向《觀察家報》透露：「他認為傾聽孩子的聲音是父母能做的最重要的事情之一——在封鎖期間，當孩子們與老師和朋友隔離時，這甚至更為重要。」他認為好父母應該確保他們傾聽孩子的聲音，或者至少應該花時間向他們的孩子解釋為什麼他們此時沒有空。麥基還認為最重要的一點是，伯納和怪物都不明白為什麼父母只是不斷忽視他們，甚至怪物也不知道如何『處理這種情況』。然而，如今父母並不是唯一會說『現在不行』的人，孩子也會對他們的父母說『現在不行』，麥基在採訪中注意到並指出了這一點。因此，家庭溝通是需要給予大量關注並值得努力改進的事情。'),
     
    ('subsection', 'Other Classic Picture Books', '其他經典繪本推薦'),
    ('listitem', '1. I will not ever NEVER eat a tomato by Lauren Child', '1. 《我絕對絕對不吃番茄》（蘿倫·柴爾德 著）'),
    ('listitem', '2. The Gruffalo by Julia Donaldson and Axel Scheffler', '2. 《怪獸古飛樂》（茱莉亞·唐納森 著，艾賽爾·薛弗勒 繪）'),
    ('listitem', '3. Where the Wild Things Are by Maurice Sendak', '3. 《野獸國》（莫里斯·桑達克 著）'),
    ('listitem', '4. Mr. Men and Little Miss book, e.g. Little Miss Wise by Roger Hargreaves', '4. 《奇先生妙小姐》系列，例如《聰明小姐》（羅傑·哈格里夫斯 著）'),
    ('listitem', '5. Two Monsters by David McKee', '5. 《兩隻怪獸》（大衛·麥基 著）'),
    ('listitem', '6. Under the Bed by Paul Bright and Ben Cort', '6. 《床底下》（保羅·布萊特 著，班·柯特 繪）'),
    ('listitem', '7. The Doorbell Rang by Pat Hutchins', '7. 《門鈴響了》（帕特·哈金斯 著）'),
    
    ('paragraph',
     'Please do not automatically assume that picture books are easy readings. They generally are, but not necessarily are. I have a pop-up book called Fungus the Bogeyman by Raymond Briggs, which I think is fun and funny but difficult to read.',
     '請不要自動認為繪本是簡單的讀物。它們通常是，但並不一定是。我有一本立體書叫《黴菌人》（Fungus the Bogeyman，雷蒙·布力格 著），我認為它很有趣且滑稽，但很難讀。'),
    ('paragraph',
     'Off the topic for a little bit......There is another kind of book that I enjoy reading. It is traditionally not considered as children’s literature, but many children love them, sort of like comic books. The one that I am introducing is a book called The Adventures of Super Diaper Baby by Pilkey in 2002. The book is full of pictures but with more texts. What I like the most is its little design of pages that you can flip while reading to create a moving effect on some pages.',
     '稍微偏離一下主題……還有另一種我喜歡閱讀的書。傳統上它不被視為兒童文學，但許多孩子喜歡它們，有點像漫畫書。我正在介紹的是一本名叫《超級尿布寶貝歷險記》（The Adventures of Super Diaper Baby，皮爾奇 著於2002年）的書。這本書充滿了圖片，但文字較多。我最喜歡的是它的翻頁小設計，您可以在閱讀時快速翻動以在某些頁面上創建移動效果（Flip-o-rama）。')
]


# ================= 2. BALLADS DATA =================
ballads_content = [
    ('section', 'Unit Introduction', '單元簡介'),
    ('paragraph',
     'We learned songs in unit 10 “Songs and Singers”. In this unit, we are going to introduce you another type of songs. They have a special name, called ‘ballad’. We will learn two ballads that I know of:\n1. Frankie and Johnny\n2. Bonnie and Clyde\nI know there are more ballads, such as “The Griesly Wife”, and "The Ballad of Charlotte Dymond”. If you are interested, you can look up the information and share.',
     '我們在第10單元「歌曲與歌手」中學習了歌曲。在本單元中，我們將向您介紹另一種類型的歌曲。它們有一個特殊的名字，叫做「歌謠（ballad）」。我們將學習兩首我知道的歌謠：\n1. 弗蘭基與約翰尼\n2. 邦妮與克萊德\n我知道還有更多的歌謠，例如《可怕的妻子》和《夏洛特·戴蒙德之歌》。如果您感興趣，可以查找信息並分享。'),
     
    ('section', 'Defining Ballads', '定義歌謠'),
    ('paragraph',
     'Definition from Oxford Advanced Learner’s Dictionary: A simple song or poem, esp one that tells a story: a ballad singer. A slow popular song about love: Her latest single is a ballad.',
     '牛津高階學習詞典定義：簡單的歌曲或詩歌，特別是講述故事的（例如：歌謠歌手）。慢速流行的情歌（例如：她最新發行的單曲是一首慢歌）。'),
    ('paragraph',
     'Definition from Cambridge Online Dictionary: A song or poem that tells a story, or (in popular music) a slow love song.',
     '劍橋線上詞典定義：講述故事的歌曲或詩歌，或（在流行音樂中）慢速柔和的情歌。'),
    ('paragraph',
     'Ballads are poems; they are short, spare, stanzaic and formulaic. They repeat through variation (refrain). Since ballads are usually stories, they need suspense or interesting plots to attract the readers to read on, such as murder or accidental death, so many of them are tragic. The first ballad that I am going to introduce you is ‘Frankie and Johnny’. I learned it at my university years.',
     '歌謠是詩歌；它們簡短、精煉、具分節性且公式化。它們通過變體（副歌）進行重複。由於歌謠通常是故事，它們需要懸念或有趣的劇情來吸引讀者繼續閱讀，例如謀殺或意外死亡，因此其中許多都是悲劇。我要向您介紹的第一首歌謠是《弗蘭基與約翰尼》。這是我在大學期間學到的。'),
     
    ('pagebreak',),
    
    ('section', 'Ballad 1: Frankie and Johnny (Anonymous)', '歌謠一：弗蘭基與約翰尼（無名氏）'),
    ('lyrics',
     "Frankie and Johnny were lovers, great God how they could love!\nSwore to be true to each other, true as the stars up above.\nHe was her man, but he done her wrong.\n\nFrankie she was his woman, everybody knows.\nShe spent her forty dollars for Johnny a suit of clothes.\nHe was her man, but he done her wrong.\n\nFrankie and Johnny went walking, Johnny in his brand new suit.\n“O good Lawd,” said Frankie, “but don’t my Johnny look cute?”\nHe was her man, but he done her wrong.",
     "弗蘭基和約翰尼是一對戀人，天啊，他們愛得有多深！\n誓言對彼此忠誠，就像頭頂的星星一樣真誠。\n他是她的男人，但他對不起她。\n\n弗蘭基是他的女人，每個人都知道。\n她花了40美元為約翰尼買了一套衣服。\n他是她的男人，但他對不起她。\n\n弗蘭基和約翰尼去散步，約翰尼穿著他的新衣服。\n「噢，天啊，」弗蘭基說，「我的約翰尼看起來不是很可愛嗎？」\n他是天的男人，但他對不起她。"),
    ('lyrics',
     "Frankie went down to the corner, just for a bucket of beer.\nFrankie said, “Mr. Bartender, has my loving Johnny been here?\nHe is my man, he wouldn’t do me wrong.”\n\n“I don’t want to tell you no story, I don’t want to tell you no lies,\nBut your Johnny left here an hour ago with that lousy Nellie Blye.\nHe is your man, but he’s doing you wrong.”\n\nFrankie went back to the hotel, she didn’t go there for fun,\nFor under her red kimono she toted a forty-four gun.\nHe was her man, but he done her wrong.",
     "弗蘭基走到拐角處，只想買一桶啤酒。\n弗蘭基說：「酒保先生，我深愛的約翰尼來過這裡嗎？\n他是我的男人，他不會對不起我。」\n\n「我不想編故事騙你，我不想對你撒謊，\n但是你的約翰尼一小時前和那個討厭的奈莉·布萊一起離開了這裡。\n他是你的男人，但他對不起你。」\n\n弗蘭基回到旅館，她不是去那裡玩的，\n因為在她的紅色和服下，她攜帶了一把點四四口徑手槍。\n他是她的男人，但他對不起她。"),
    ('lyrics',
     "Frankie went down to the hotel and looked in the window so high,\nAnd there was her loving Johnny a-loving up Nellie Blyde.\nHe was her man, but he was doing her wrong.\n\nFrankie threw back her kimono, took out that old forty-four.\nRoot-a-toot-toot, three times she shot, right through the hardwood door.\nHe was her man, but he done her wrong.\n\nJohnny grabbed off his Stetson, crying “O Frankie don’t shoot!”\nFrankie pulled that forty-four, went root-a-toot-toot-toot-toot.\nHe was her man, but he done her wrong.",
     "弗蘭基走到旅館，看著高高的窗戶，\n發現她深愛的約約翰尼正與奈莉·布萊調情。\n他是她的男人，但他對不起她。\n\n弗蘭基掀開和服，拿出那把舊點四四手槍。\n砰、砰、砰！她開了三槍，直接射穿了硬木門。\n他是她的男人，但他對不起她。\n\n約翰尼抓下他的牛仔帽，大喊：「噢，弗蘭基，別開槍！」\n弗蘭基扣動扳機，手槍發出連環的砰砰聲。\n他是她的男人，但他對不起她。"),
    ('lyrics',
     "“Roll me over gently, roll me over slow,\nRoll me on my right side, for my left side hurts me so,\nI was her man, but I done her wrong.”\n\nWith the first shot Johnny staggered, with the second shot he fell;\nWhen the last bullet got him, there was a new man’s face in hell.\nHe was her man, but he done her wrong.",
     "「輕輕地幫我翻身，慢慢地幫我翻身，\n幫我翻到右側，因為我的左側疼得太厲害了，\n我曾是她的男人，但我對不起她。」\n\n第一槍，約約翰尼搖搖晃晃；第二槍，他倒下了；\n當最後一顆子彈擊中他時，地獄裡多了一張新男人的面孔。\n他是她的男人，但他對不起她。"),
    ('lyrics',
     "“O, bring out your rubber-tired hearses, bring out your rubber-tired hacks;\nGonna take Johny to the graveyard and ain’t gonna bring him back.\nHe was my man but he done me wrong.”\n\n“O, put me in the dungeon, put me in that cell,\nPut me where the northeast wind blows from the southeast corner of hell.\nI shot my man, cause he done me wrong.”",
     "「噢，開出你們的橡膠輪胎靈車，開出你們的橡膠輪胎馬車；\n準備把約翰尼送去墓地，不打算帶他回來了。\n他是我的男人，但他對不起我。」\n\n「噢，把我關進地牢，把我關進那間牢房，\n把我關在東北風從地獄東南角吹來的地方。\n我開槍打死了我的男人，因為他對不起我。」"),
     
    ('pagebreak',),
    
    ('paragraph',
     'A quick search on YouTube will lead us to different versions of ‘Frankie and Johnny’ at different times. (Jimmie Rodgers (1929), Johnny Cash, Elvis Presley, Sam Cooke (1963), Big Bill Broonzy, Frank Crumit (1927), Lindsay Lohan). Among them, the content varies but the main plot remains, Johnny betrayed Frankie and she shot him and ended up in prison. Elvis Presley personalized the story and turned himself into Johnny to act out the story in his performance, which was intriguing. I am sure, after watching each version of them, you would be able to hear the story easily and sing along. Some of the versions also include the following story about Frankie’s life in jail. Even though she had killed Johnny, she was still in misery, because she said, “There ain’t no good in a man. I had a man but he done me wrong.” She was punished to sit in the electric chair. The story ends up with: This story has no moral, this story has no end, This story only goes to show that there ain’t no good in men. The story is as interesting as the TV drama nowadays, even with the sound effect “Root-a-toot-toot” in it. Unlike the other literature classes, this is something that I have never seen in a ‘poem’.',
     '在 YouTube 上進行快速搜尋將會引導我們找到不同時期不同版本的《弗蘭基與約翰尼》。其中包括吉米·羅傑斯（1929）、約翰尼·卡什、艾維斯·普里斯萊（貓王）、山姆·庫克（1963）、大比爾·布倫齊、法蘭克·克魯米特（1927）、林賽·羅韓。在這些版本中，內容有所不同，但主要情節保持不變：約翰尼背叛了弗蘭基，她開槍打死了他並最終入獄。貓王將故事個人化，在表演中把自己化身為約翰尼來演繹這個故事，這非常耐人尋味。我相信，在觀看了每個版本後，您將能夠輕鬆聽到故事並跟著唱。有些版本還包括以下關於弗蘭基在監獄生活的故事。即使她殺了約約翰尼，她仍然在痛苦中，因為她說：「男人沒一個好東西。我曾擁有一個男人，但他對不起我。」她被懲罰坐電椅。故事的結尾是：這故事沒有道德，這故事沒有結局，這故事只是用來表明，男人沒一個好東西。這個故事和如今的電視劇一樣有趣，甚至還有聲音效果「砰、砰、砰」在裡面。與其他文學課不同，這是我從未在「詩歌」中見過的東西。'),
     
    ('section', 'Ballad 2: Bonnie and Clyde', '歌謠二：邦妮與克萊德'),
    ('paragraph',
     'The second ballad we are going to read is about a couple who robbed a bank. Let us have a read.',
     '我們要讀的第二首歌謠是關於一對搶劫銀行的情侶。讓我們來讀一讀。'),
    ('lyrics',
     "Bonnie and Clyde were pretty lookin’ people\nbut I can tell you people they were the devil’s children.\nBonnie and Clyde began their evil doin’\none lazy afternoon down Savannah way,\nThey robbed a store and high-tailed outa that town\ngot clean away in a stolen car\nand waited till the heat died down.\n\nBonnie and Clyde advance their reputation\nand made the graduation into the banking business\n“Reach for the sky” sweet-talking Clyde would holler\nas Bonnie loaded dollars in the dewlap bag.\nNow one brave man he tried to take’em alone\nThey left him lyin’ in a pool of blood,\nAnd laughed about it all the way home.",
     "邦妮和克萊德都是長相好看的人\n但我可以告訴你們，他們是惡魔的孩子。\n邦妮和克萊德開始了他們的惡行\n在薩凡納路上一個慵懶的下午，\n他們搶劫了一家商店，並迅速逃離了那個小鎮\n坐上一輛偷來的車子全身而退\n並一直等待，直到風頭過去。\n\n邦妮和克萊德名聲大噪\n並晉升到了搶劫銀行的業務中\n甜言蜜語的克萊德會大喊「舉起手來」\n而邦妮則把美元裝進提袋裡。\n現在有一位勇敢的人試圖獨自對付他們\n他們留他躺在血泊之中，\n並一路上笑著回家。"),
    ('lyrics',
     "Bonnie and Clyde got to be public enemy number one\nRunning and hiding from ev’ry Americain lawman’s gun.\nThey used to laugh about dyin’,\nBut deep inside ‘em they knew\nThat pretty soon they’d be lyin’\nBeneath the ground together\nPushing up daisies to welcome the sun\nAnd the morning dew.\n\nActing upon reliable information\na fed’ral deputation laid a deadly ambush.\nWhen Bonnie and Clyde came walking in the sunshine\na half a dozen carbines opened up on them.\nBonnie and Clyde, they lived a lot together\nand finally together they died.",
     "邦妮和克萊德成了頭號公敵\n四處逃竄，躲避著每一位美國執法者的槍口。\n以前他們常對死亡一笑置之，\n但在內心深處，他們知道\n很快他們就會躺在\n地底之下\n埋在花下迎接著太陽\n和早晨的露水。\n\n根據可靠消息\n聯邦代表設下了致命的埋伏。\n當邦妮和克萊德在陽光下走來時\n半打卡賓槍向他們開了火。\n邦妮和克萊德，他們曾生活在一起\n最終他們也死在了一起。"),
     
    ('pagebreak',),
    
    ('section', 'Vocabulary: Love and Attraction', '愛與吸引力字彙'),
    ('listitem', 'to fall in love | 墜入愛河', 'to fall in love | 墜入愛河'),
    ('listitem', 'to fall for someone | 迷上某人 / 愛上某人', 'to fall for someone | 迷上某人 / 愛上某人'),
    ('listitem', 'to be fascinated by someone | 被某人吸引/著迷', 'to be fascinated by someone | 被某人吸引/著迷'),
    ('listitem', 'to have a crush on someone | 暗戀某人 / 對某人有好感', 'to have a crush on someone | 暗戀某人 / 對某人有好感'),
    ('listitem', 'to be infatuated with someone | 對某人極度迷戀', 'to be infatuated with someone | 對某人極度迷戀'),
    ('listitem', 'to adore someone | 崇拜/熱愛某人', 'to adore someone | 崇拜/熱愛某人'),
    ('listitem', 'to be fond of someone | 喜歡某人', 'to be fond of someone | 喜歡某人'),
    ('listitem', 'to care for someone | 關心/照顧某人', 'to care for someone | 關心/照顧某人'),
    ('listitem', 'to worship someone | 崇拜/敬仰某人', 'to worship someone | 崇拜/敬仰某人'),
    ('listitem', 'to be devoted to someone | 對某人專心致志/奉獻', 'to be devoted to someone | 對某人專心致志/奉獻'),
    ('listitem', 'to be head over heels in love with someone | 神魂顛倒地愛上某人', 'to be head over heels in love with someone | 神魂顛倒地愛上某人'),
    
    ('section', 'Sentence Rewriting Exercises', '句型改寫練習'),
    ('listitem', '1. When I first met you, I quickly grew to like you. -> When I first met you, I quickly grew fond of you.', '1. 當我第一次遇見你時，我很快就喜歡上了你。 (fond) -> 當我第一次遇見你時，我很快就對你產生了好感。'),
    ('listitem', '2. Later, I felt a very strong attraction to you. -> Later, I fell for you.', '2. 後來，我感到了對你的強烈吸引。 (fell) -> 後來，我愛上了你。'),
    ('listitem', '3. Then, I couldn’t stop thinking about you. -> Then, I was infatuated with you.', '3. 然後，我無法停止想你。 (infatuated) -> 然後，我對你無可自拔地迷戀。'),
    ('listitem', '4. I was totally charmed by you. -> I was totally captivated by you.', '4. 我完全被你迷住了。 (captivated) -> 我完全被你吸引了。'),
    ('listitem', '5. I was completely in love! -> I was head over heels in love!', '5. 我完全陷入了愛河！ (head) -> 我神魂顛倒地墜入了愛河！')
]

if __name__ == "__main__":
    build_pdf("family_communication_bilingual.pdf", "Unit: Family Communication: Not Now, Bernard", family_content)
    build_pdf("ballads_bilingual.pdf", "Unit: Ballads", ballads_content)
    print("Done generating both newest detailed bilingual PDFs.")
