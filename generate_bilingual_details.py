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
    # Setup document: Margins are 54pt left/right, 72pt top/bottom to clear header/footer
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
    
    style_en_lyrics = ParagraphStyle(
        'EnLyrics',
        parent=styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#374151'),
        leftIndent=24,
        spaceAfter=2
    )
    
    style_zh_lyrics = ParagraphStyle(
        'ZhLyrics',
        parent=styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#4B5563'),
        leftIndent=24,
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
            
        elif item_type == 'lyrics':
            en_lines = item[1].split('\n')
            zh_lines = item[2].split('\n')
            # Loop through lines and print side by side or sequentially
            for en_line, zh_line in zip(en_lines, zh_lines):
                if en_line.strip():
                    story.append(Paragraph(en_line, style_en_lyrics))
                if zh_line.strip():
                    story.append(Paragraph(zh_line, style_zh_lyrics))
            story.append(Spacer(1, 6))
            
        elif item_type == 'pagebreak':
            story.append(PageBreak())
            
        elif item_type == 'spacer':
            story.append(Spacer(1, item[1]))

    # Callback wrapper to pass custom title
    def first_page_cb(canvas, doc):
        make_header_footer(canvas, doc, doc_title)
    def later_pages_cb(canvas, doc):
        make_header_footer(canvas, doc, doc_title)

    doc.build(story, onFirstPage=first_page_cb, onLaterPages=later_pages_cb)
    print(f"Generated PDF: {filename}")


# ================= DATA FOR SONGS AND SINGERS =================
songs_content = [
    ('section', 'Unit Introduction', '單元簡介'),
    ('paragraph', 
     'This is a more relaxing and pleasant unit since we are half way through the course. I would like to include a bit of fun in the course and so we are going to learn English through 5 songs that are special…. Well, at least, to me.',
     '這是一個比較輕鬆且愉快的單元，因為我們的課程已經過半了。我希望能為課程增添一些趣味，因此我們將透過五首對我而言相當特別的歌曲來學習英文。'),
    ('paragraph',
     'In this unit, we are going to learn five songs with significant importance. Of course there are other songs with special meaning or background, and you are welcome to share them after reading this unit in the discussion forum. I have chosen the first four songs because they send positive messages to help the world, while the last one is based on the singer who everyone knows probably, old or young.',
     '在本單元中，我們將學習五首具有重大意義的歌曲。當然，還有其他具有特殊意義或背景的歌曲，歡迎大家在閱讀完本單元後在討論區分享。我選擇前四首歌是因為它們傳遞了幫助世界的正面訊息，而最後一首則是基於一位老少皆知的歌手。'),
    
    ('section', '#1. Do They Know It’s Christmas?', '#1. 他們知道今天是聖誕節嗎？'),
    ('paragraph',
     'Christmas is always one of my must-celebrate holidays. People do their Christmas shopping and the street is full of joys. However, we should also think of the people who do not own the luxury of celebration. “Do They Know It’s Christmas?” is written for a special reason, to raise money for the famine happened in Ethiopia between 1983-1985, i.e. for charity. It was released in 1984. The song aimed to raise £70,000, but ended up raising £8 million within a year. It reached number one within a very short time and still is one of the favorite Christmas songs in the UK. It is a song sung by many world-famous artists, including Bono (U2), Sting (The Police), Phil Collins (vocalist and drummer), George Michael (Wham!), Boy George (Culture Club) and many more (How many of them do you know?). The success of “Do They Know It’s Christmas?” led to our #2 song “We Are the World” in 1985, which is probably even more famous. Let us now read the lyrics and maybe you can listen to the song too.',
     '聖誕節一直是我必慶祝的節日之一。人們忙著採購聖誕年貨，街上充滿了歡樂。然而，我們也應該想想那些無法享有慶祝奢侈的人們。《他們知道今天是聖誕節嗎？》是為了特殊原因而寫的，旨在為 1983 至 1985 年間衣索比亞發生的饑荒籌款，即用於慈善。它於 1984 年發行。這首歌的目標是籌集 7 萬英鎊，但最終在一年之內籌集了 800 萬英鎊。它在極短的時間內登上第一名，且至今仍是英國最受喜愛的聖誕歌曲之一。這首歌由許多世界知名的藝人合唱，包括 Bono (U2)、Sting (The Police)、Phil Collins (主唱兼鼓手)、George Michael (Wham!)、Boy George (Culture Club) 等等（你認識其中的幾位呢？）。《他們知道今天是聖誕節嗎？》的成功促成了我們在 1985 年的第二首歌《四海一家》，這首歌可能更為著名。現在讓我們來讀歌詞，或許你也可以聽聽這首歌。'),
    ('paragraph', 'YouTube Link: https://youtu.be/j3fSknbR7Y4', 'YouTube 連結：https://youtu.be/j3fSknbR7Y4'),
    ('subsection', 'Lyrics (Part 1)', '歌詞（第一部分）'),
    ('lyrics',
     "It’s Christmas time, there’s no need to be afraid.\nAt Christmas time, we let in light and we banish shade.\nAnd in our world of plenty, we could spread a smile of joy.\nThrow your arms around the world at Christmas time.",
     "這是聖誕佳節，無須感到恐懼。\n在聖誕時刻，我們迎來光明並驅散陰霾。\n而在我們富足的世界裡，我們可以傳播喜悅的笑容。\n在聖誕時刻，用你的雙手擁抱這個世界。"),
    ('subsection', 'Lyrics (Part 2)', '歌詞（第二部分）'),
    ('lyrics',
     "But say a prayer, pray for the other one-e-es.\nAt Christmas time, it’s hard but when you’re having fun,\nthere’s a world outside your window,\nand it’s a world of dread and fear,\nwhere the only water flowing is the bitter sting of tears,\nand the Christmas bells that ring there\nare the clanging chimes of doom,\nWell tonight, thank God it’s them instead of you…",
     "但請為其他人們做個祈禱。\n在聖誕時刻，雖然很艱難但當你正樂在其中時，\n你的窗外還有另一個世界，\n那是一個充斥著恐懼與害怕的世界，\n在那裡唯一流動的水是苦澀的淚水，\n在那裡敲響的聖誕鐘聲，\n是末日的沉重喪鐘。\n今晚，感謝上帝是他們在承受，而不是你……"),
    ('lyrics',
     "Well there won’t be snow in Africa this Christmas time.\nThe greatest gift they’ll get this year is life.\nOoh~ Where nothing ever grows, no rain or rivers flow,\ndo they know it’s Christmas time at all?\nHere’s to you, raise a glass for everyone.\nHere’s to them underneath that burning sun.\nDo they know it’s Christmas time at all?\nFeed the world\nFeed the world\nFeed the world, let them know it’s Christmas time",
     "這個聖誕節，非洲是不會下雪的。\n他們今年能得到的最大禮物就是生命。\n喔～ 在那個萬物不生、無雨也無河流的地方，\n他們真的知道聖誕節到了嗎？\n敬你一杯，為每個人舉杯。\n敬在烈日之下的他們。\n他們真的知道聖誕節到了嗎？\n拯救這個世界\n拯救這個世界\n拯救這個世界，讓他們知道聖誕節到了"),
     
    ('pagebreak',),
    
    ('section', '#2. We Are The World (USA for Africa)', '#2. 四海一家（美國援非委員會）'),
    ('paragraph',
     '“We Are The World” is the American version of charity song for the African famine, following the 1984 “Do They Know It’s Christmas”. The song was written by Michael Jackson and Lionel Richie and produced by Quincy Jones and Michael Omartian. The song raised almost 10.8 million and received many awards. Forty-five artists worked together for the song, including Steve Wonder, Diana Ross, Tina Turner, Cyndi Lauper, Kenneth Rogers and so on. The USA and UK also held ‘Life Aid’ concerts. The song was later reproduced in 2010 to raise money for earthquake victims in Haiti, which involved over 75 musicians. In Taiwan, we have a similar version, “A Better Tomorrow”, which was also a group work of artists and made the billboard at the time.',
     '《四海一家》是美國為非洲饑荒創作的慈善歌曲，繼 1984 年的《他們知道今天是聖誕節嗎？》之後推出。這首歌由麥可·傑克森與萊諾·李奇共同創作，並由昆西·瓊斯與麥可·歐馬提安製作。該曲籌集了將近 1080 萬美元並獲得了諸多獎項。45 位藝人共同合作了這首歌，包括史提夫·汪達、黛安娜·羅絲、蒂娜·透納、辛蒂·羅波、肯尼·羅傑斯等等。美國與英國也舉行了『援助生命 (Live Aid)』演唱會。這首歌后來於 2010 年重製，為海地地震災民籌款，有超過 75 位音樂人參與。在台灣，我們也有一個類似的版本《明天會更好》，同樣是由多位藝人合力創作，並在當時登上了排行榜。'),
    ('paragraph', 'YouTube Link: https://youtu.be/s3wNuru4U0I', 'YouTube 連結：https://youtu.be/s3wNuru4U0I'),
    ('subsection', 'Lyrics (Part 1)', '歌詞（第一部分）'),
    ('lyrics',
     "There comes a time\nWhen we heed a certain call\nWhen the world must come together as one\nThere are people dying\nOh, and it’s time to lend a hand to life\nThe greatest gift of all\nWe can’t go on\nPretending day-by-day\nThat someone, somewhere will soon make a change\nWe’re all a part of God’s great big family\nAnd the truth, you know, love is all we need",
     "是時候了\n當我們聽到某個呼喚\n當世界必須團結一致\n有人正在死去\n噢，是時候向生命伸出援手了\n這是最偉大的禮物\n我們不能繼續\n日復一日地假裝\n某些人或某個地方很快會做出改變\n我們都是上帝這個大家庭的一份子\n而事實上，你知道，愛就是我們所需要的一切"),
    ('subsection', 'Lyrics (Part 2)', '歌詞（第二部分）'),
    ('lyrics',
     "We are the world\nWe are the children\nWe are the ones who make a brighter day, so let’s start giving\nThere’s a choice we’re making\nWe’re saving our own lives\nIt’s true we’ll make a better day, just you and me\nOh, send them your heart\nSo they know that someone cares\nAnd their lives will be stronger and free\nAs God has shown us by turning stones to bread\nAnd so we all must lend a helping hand",
     "四海一家\n我們是國家的未來\n我們是創造更美好明天的人，所以讓我們開始奉獻\n這是我們正在做出的選擇\n我們正在拯救我們自己的生命\n的確，我們將創造更美好的一天，只有你和我\n噢，送上你的愛心\n讓他們知道有人在關心\n他們的生命將會變得更堅強與自由\n正如上帝向我們展示的，將石頭化為麵包\n因此我們所有人都必須伸出援手"),
    ('lyrics',
     "When you’re down and out, there seems no hope at all\nBut if you just believe there’s no way we can fall\nWell, well, well, well let us realize\nOh, that a change can only come\nWhen we stand together as one, yeah~~",
     "當你窮困潦倒時，似乎毫無希望\n但只要你相信，我們絕對不會倒下\n好吧，讓我們明白\n噢，改變唯有在\n我們團結一致時才會到來，耶～～"),

    ('pagebreak',),

    ('section', '#3. Heal The World (Michael Jackson)', '#3. 拯救這世界（麥可·傑克森）'),
    ('paragraph',
     'I believe everyone knows Michael Jackson, but I am not sure if you have noticed this song. Michael Jackson recorded this song in 1991 to express his antiwar wishes and organized a charity foundation ‘Heal the World’ to make a world ‘a better place’. He emphasized the concept of ‘betterment for all’ by teaching children how to help others to help themselves in the future for all human beings. The song did not have my attention when it was first released because I was too young; it took my attention recently for the positivity behind the song.',
     '我相信每個人都認識麥可·傑克森，但我不確定您是否注意到這首歌。麥可·傑克森於 1991 年錄製了這首歌以表達他的反戰心願，並組織了『拯救世界 (Heal the World)』慈善基金會，旨在讓世界『變得更好』。他強調了『人人受益』的概念，教導孩子們如何幫助他人，以便在未來幫助全人類。當這首歌首次發行時，它並沒有引起我的注意，因為我當時太年輕了；直到最近，因為這首歌背後的積極正面意義，它才吸引了我的注意。'),
    ('paragraph', 'YouTube Link: https://youtu.be/BWf-eARnf6U', 'YouTube 連結：https://youtu.be/BWf-eARnf6U'),
    ('subsection', 'Lyrics (Part 1)', '歌詞（第一部分）'),
    ('lyrics',
     "There is a place in your heart and I know that it is love\nAnd this place it was brighter than tomorrow\nAnd if you really try you’ll find there’s no need to cry\nIn this place you’ll feel there’s no hurt or sorrow\nThere are ways to get there if you care enough for the living\nMake a little space, make a better place",
     "在你心中有一個地方，我知道那就是愛\n這個地方曾經比明天還要明亮\n如果你真的去嘗試，你會發現沒有必要哭泣\n在這個地方，你會感覺不到傷痛或悲哀\n如果你足夠關心活著的人，就有方法到達那裡\n騰出一點空間，創造一個更美好的地方"),
    ('subsection', 'Lyrics (Part 2)', '歌詞（第二部分）'),
    ('lyrics',
     "Heal the world\nMake it a better place for you and for me, and the entire human race\nThere are people dying if you care enough for the living\nMake a better place for you and for me\nIf you want to know why there’s love that cannot lie\nLove is strong\nIt only cares of joyful giving\nIF we try we shall see in this bliss we cannot feel\nFear of dread, we stop existing and start living",
     "拯救這個世界\n讓它成為一個對你、對我以及對全人類都更美好的地方\n有人正在死去，如果你足夠關心活著的人\n為你和我創造一個更美好的地方\n如果你想知道為什麼，有一種愛無法說謊\n愛是強大的\n它只在乎喜悅的奉獻\n如果我們去嘗試，我們將在這種福祉中看到我們無法感受到的東西\n免於恐懼，我們不再只是生存，而是開始生活"),
    ('lyrics',
     "And the dream we were conceived in will reveal a joyful face\nAnd the world we once believed in will shine again in grace\nThen why do we keep strangling life\nWould this earth, crucify its soul?\nBe god’s glow",
     "我們所孕育的夢想將展現出喜悅的容顏\n我們曾經深信的世界將在恩典中再次閃耀\n那為什麼我們還要繼續扼殺生命？\n難道這地球要釘死自己的靈魂嗎？\n成為上帝的光輝吧"),
    ('lyrics',
     "We could fly so high\nLet our spirits never die\nIn my heart I feel you are all my brothers\nCreate a world with no fear\nTogether we cry happy tears\nSee the nations turn their swords into plowshares",
     "我們可以飛得很高\n讓我們的精神永不磨滅\n在我心中，我感覺你們都是我的兄弟\n創造一個沒有恐懼的世界\n我們將一起流下幸福的淚水\n看著各國將他們的利劍鑄成犁鋤"),

    ('pagebreak',),

    ('section', '#4. Imagine (John Lennon)', '#4. 想像（約約翰·藍儂）'),
    ('paragraph',
     'This is the song by the English rock musician John Lennon (1971) and was his best solo single. The website Lyric Interpretations (https://www.lyricinterpretations.com/john-lennon/imagine) had an exquisite description about the song that I believe myself cannot triumph. So, I am just going to use the top-rated interpretation on this website as the introduction for its reader friendliness.',
     '這是英國搖滾音樂家約約翰·藍儂 (1971年) 的歌曲，也是他最優秀的個人單曲。Lyric Interpretations 網站對這首歌有著非常精妙的描述，我相信自己無法超越它。因此，為了讀者的便利，我將直接使用該網站上評價最高的解讀作為介紹。'),
    ('paragraph', 'YouTube Link: https://youtu.be/YkgkThdzX-8', 'YouTube 連結：https://youtu.be/YkgkThdzX-8'),
    ('subsection', 'Top Rated Interpretation', '最佳歌曲解讀'),
    ('paragraph',
     'Through these lyrics, John Lennon was asking us to imagine a place where things that divide people did not exist. The song covers the violence issue we have in this world. We are surrounded by hate, cruelty, murder, war and racism. The world that he sings about tells us how we should want the world to be. In the song there is world peace and everyone is living together as one; sharing the world. It was written to show us that there is another way out there to live our lives; that we don\'t need to hate and kill but to learn to live in peace and harmony with each other. It\'s so pleasant to imagine that everyone is sharing the world, instead of fighting for the imaginary boundaries. These are all fantasies that can never come true and he is dreamer, he knows that there are many other people like him who dream of peace, love and equality - "You, you may say I\'m a dreamer, but I\'m not the only one." He hopes that someday everyone will have the same dream and so it won\'t be a dream anymore, it will become reality and then we won\'t be separated by our countries or beliefs and we\'ll live together as one. - "I hope someday you will join us, and the world will live as one."',
     '透過這些歌詞，約翰·藍儂邀請我們去想像一個不存在分裂人類之物的世界。這首歌探討了我們在這個世界上所面臨的暴力問題。我們被仇恨、殘忍、謀殺、戰爭和種族主義所包圍。他所歌唱的世界告訴我們，我們應該希望世界變成什麼樣子。在歌中，世界是和平的，每個人都團結一致地生活，共同分享這個世界。這首歌的創作是為了向我們展示，還有另一種生活方式；我們不需要仇恨和殺戮，而是要學會彼此和平共處、和諧相處。想像每個人都在分享這個世界，而不是為虛無的邊界而戰，這是多麼令人愉悅的事。雖然這些都是永遠無法實現的幻想，而他是一個夢想家，但他知道還有許多人和他一樣夢想著和平、愛與平等——「你，你可能會說我是個夢想家，但我不是唯一的一個。」他希望有一天每個人都會有相同的夢想，這樣它就不再只是個夢想，而是會成為現實，然後我們將不再因國家或信仰而分離，我們將團結一致地生活。——「我希望有一天你能加入我們，世界將合而為一。」'),
    ('subsection', 'Lyrics (Part 1)', '歌詞（第一部分）'),
    ('lyrics',
     "Imagine there’s no heaven\nIt’s easy if you try\nNo hell below us\nAbove us only sky\nImagine all the people\nLiving for today",
     "想像沒有天堂\n只要你嘗試，這並不難\n在我們之下沒有地獄\n在我們之上只有藍天\n想像所有的人\n都為今天而活"),
    ('subsection', 'Lyrics (Part 2)', '歌詞（第二部分）'),
    ('lyrics',
     "Imagine there’s no countries\nIt isn’t hard to do\nNothing to kill or die for\nAnd no religion too\nImagine all the people\nLiving life in peace\n\nYou may say I’m a dreamer\nBut I’m not the only one\nI hope someday you’ll join us\nAnd the world will be one",
     "想像沒有國家\n這並不難做到\n沒有人會為此殺戮或犧牲\n也沒有宗教信仰\n想像所有的人\n都和平地生活\n\n你可能會說我是個夢想家\n但我不是唯一的一個\n我希望有一天你能加入我們\n世界將合而為一"),
    ('lyrics',
     "Imagine no possessions\nI wonder if you can\nNo need for greed or hunger\nA brotherhood of man\nImagine all the people\nSharing all the world\n\nYou may say I’m a dreamer\nBut I’m not the only one\nI hope someday you’ll join us\nAnd the world will live as one",
     "想像沒有財產\n我不知道你是否能做到\n沒有貪婪或飢餓的需要\n人類情同手足\n想像所有的人\n共同分享這個世界\n\n你可能會說我是個夢想家\n但我不是唯一的一個\n我希望有一天你能加入我們\n世界將會合而為一地生活"),

    ('pagebreak',),

    ('section', '#5. That’s Life (Frank Sinatra)', '#5. 這就是人生（法蘭克·辛納屈）'),
    ('paragraph',
     'Some people say art imitates life; this song really describes life vividly. I believe many of us, being a grown-up with plenty of life experience, would agree that life is full of ups and downs and it is so important that we should not give up. We need to ‘pull ourselves together’ and ‘be back on our feet’ for soon we will be ‘back on top’ and we want to be ready for it. The song was first recorded in 1963 by Marion Montgomery, but the most famous version is by Frank Sinatra in 1966, who is a legendary singer and actor (12 December 1915 – 14 May 1998). Even though he did not learn to read music, he had his own arrangement of the structure and interpretation of his singing and required perfection when he recorded songs. In his life, he recorded over 1,300 songs and participated in more than 50 films. 13 May is considered “Frank Sinatra Day” and there is a Frank Sinatra Park in New Jersey with a 6-foot bronze statue honoring him.',
     '有人說藝術模仿生活；這首歌確實生動地描繪了生活。我相信我們許多人，作為一個擁有豐富生活經驗的成年人，都會同意生活充滿了起起落落，而最重要的是我們不能放棄。我們需要『振作起來』並『重新站穩腳跟』，因為很快我們就會『重回巔峰』，而我們必須對此做好準備。這首歌首錄於 1963 年，由 Marion Montgomery 演唱，但最著名的版本是法蘭克·辛納屈在 1966 年演唱的版本，他是一位傳奇歌手兼演員（1915年12月12日－1998年5月14日）。儘管他沒有學過識譜，但他對自己的演唱結構和詮釋有著獨特的安排，並在錄製歌曲時要求完美。在他的一生中，他錄製了 1,300 多首歌曲，並參與了 50 多部電影。 5月13日被定為“法蘭克·辛納屈日”，在紐澤西州還有一個設有 6 英尺高青銅雕像的法蘭克·辛納屈公園以紀念他。'),
    ('paragraph', 'YouTube Link: https://youtu.be/VZ_DUzHYwhM', 'YouTube 連結：https://youtu.be/VZ_DUzHYwhM'),
    ('subsection', 'Lyrics (Part 1)', '歌詞（第一部分）'),
    ('lyrics',
     "That's life\nThat's what all people say\nYou're riding high in April\nShot down in May\nBut I know I'm gonna change that tune\nWhen I'm back on top, back on top in June",
     "這就是人生\n大家都是這麼說的\n你在四月時意氣風發\n在五月時卻跌落谷底\n但我知道我會改變這個調子\n當我在六月重新回到巔峰時"),
    ('subsection', 'Lyrics (Part 2)', '歌詞（第二部分）'),
    ('lyrics',
     "That's life\nAnd is funny it may seem\nSome people get their kicks stomping on a dream\nBut I don't let it get me down\nCause this fine old world it keeps me spinning round",
     "這就是人生\n雖然這看起來滑稽\n有些人以踐踏別人的夢想為樂\n但我不會讓它擊垮我\n因為這個美好的世界仍在不停旋轉"),
    ('lyrics',
     "I've been a puppet, a pauper, a pirate\nA poet, a pawn and a king\nI've been up and down and over and out\nAnd I know one thing\nEach time I find myself flat on my face\nI just pick myself up and get back in the race",
     "我當過木偶、乞丐、海盜\n詩人、兵卒和君王\n我經歷過起起伏伏，也曾一敗塗地\n但我知道一件事\n每次我摔得鼻青臉腫\n我都會自己站起來，重新回到競爭中"),
    ('lyrics',
     "That's life\nOh, and you know I can't deny it\nMany times I thought of quitting, baby\nBut my heart won't buy it\nAnd if I didn't think it was worth one single try\nWell, I'd hop upon a big bird and then I'd fly",
     "這就是人生\n噢，你知道我無法否認\n許多次我都想放棄，寶貝\n但我的心不接受\n如果我不認為它值得再試一次\n好吧，我會跳上一隻大鳥，然後展翅高飛")
]


# ================= DATA FOR SHERLOCK HOLMES =================
holmes_content = [
    ('section', 'Lead-in Questions', '導入問題'),
    ('paragraph',
     "1. The Sherlock Holmes stories established crime fiction as a respectable genre, and Doyle's success inspired many contemporary detective stories.",
     "1. 福爾摩斯故事使犯罪小說成為一個受人尊敬的文學流派，而柯南·道爾的成功啟發了許多同時代的偵探故事。"),
    ('paragraph',
     "2. Sherlock Holmes is arguably the best-known fictional detective, adaptations have been seen in different directions or placed in different times.",
     "2. 夏洛克·福爾摩斯無疑是知名度最高的虛構偵探，其改編作品在不同的方向上被呈現，或被置於不同的時代背景中。"),
    
    ('section', 'Character Profile', '角色特徵'),
    ('paragraph',
     "Sherlock Holmes is the main character in the stories by Sir Arthur Conan Doyle. He is very clever, always notices very small details and then uses them to guess what has happened. He is known for wearing a deerstalker, smoking a pipe, and playing the violin. (Longman Dictionary of Contemporary English)",
     "夏洛克·福爾摩斯是亞瑟·柯南·道爾爵士筆下故事的主角。他非常聰明，總是能注意到非常細微的細節，然後利用它們來推測發生了什麼。他以戴著獵鹿帽、抽著煙斗和拉小提琴而聞名。（朗文當代英語辭典）"),
    
    ('section', 'Origin & History', '起源與歷史'),
    ('paragraph',
     "First appeared in Sir Arthur Conan Doyle’s A Study in Scarlet (1887), Sherlock Holmes, as a “consulting detective”, is known for his proficiency with observation, deduction, forensic science and logical reasoning while investigating cases for a wide variety of clients.",
     "夏洛克·福爾摩斯首次出現於亞瑟·柯南·道爾爵士的《血字的研究》（1887年），作為一名「諮詢偵探」，他在為各種客戶調查案件時，以精通觀察、演繹推理、法醫科學和邏輯推理而聞名。"),
    ('paragraph',
     "Throughout 4 novels and 56 short stories featuring Holmes, the background were set in Victorian and Edwardian eras. Holmes shared one room with Dr. John H. Watson at 221B Baker Street in London due to financial difficulties, and they pursued criminal cases jointly. Most of the stories were narratives written from Dr. Watson’s point of view, and he described Holmes as a very complex and moody character. The residence was maintained by their landlady, Mrs. Hudson.",
     "在以福爾摩斯為主角的 4 部小說和 56 篇短篇故事中，故事背景主要設定在維多利亞時代和愛德華時代。由於經濟困難，福爾摩斯與約翰·H·華生醫生合租倫敦貝克街 221B 號的一間公寓，他們共同追查刑事案件。大多數故事都是從華生醫生的視角以第一人稱敘述，他將福爾摩斯描述為一個非常複雜且喜怒無常的人。這所住宅由他們的房東太太哈德森太太維護。"),
    ('paragraph',
     "The only woman whom Holmes ever held in high regard is Irene Adler—one of the few characters to be clever enough to get past him. Though only appearing in Conan Doyle’s A Scandal in Bohemia (1891), she had often been portrayed as a potential love interest of Holmes in contemporary adaptations. In the original stories, the important characters included the Scotland Yard inspector Lestrade, his brother Mycroft, and his formidable opponent Professor James Moriarty whom Holmes considered the “Napoleon of Crime”.",
     "福爾摩斯唯一高度敬重的女性是艾琳·艾德勒——她是少數聰明到足以瞞過他的角色之一。雖然她僅在柯南·道爾的《波希米亞醜聞》（1891年）中露面，但在現代的改編作品中，她經常被塑造成福爾摩斯的潛在戀愛對象。在原著故事中，重要人物還包括蘇格蘭場的雷斯垂德警官、他的哥哥邁克羅夫特，以及他強大的對手詹姆斯·莫里亞蒂教授，福爾摩斯將後者視為「犯罪界的拿破崙」。"),
     
    ('pagebreak',),
    
    ('section', 'Extended Content & Adaptations', '延伸內容與改編'),
    
    ('subsection', 'Film: Sherlock Holmes (2009)', '電影：《福爾摩斯》（2009年）'),
    ('paragraph',
     "In this 2009 mystery action film, Sherlock Holmes (Robert Downey Jr.) and his stalwart partner, Dr. Watson (Jude Law) take on their latest challenge. The only woman ever to have bested Holmes, Irene Adler (Rachel McAdams) again sparks her tempestuous relationship with the detective, while a mysterious new nemesis - Blackwood (Mark Strong) - constructs a deadly plot that could destroy the country.",
     "在這部 2009 年的懸疑動作電影中，夏洛克·福爾摩斯（小勞勃·道尼飾）和他堅定的夥伴華生醫生（裘德·洛飾）迎接了他們的最新挑戰。唯一擊敗過福爾摩斯的女性艾琳·艾德勒（瑞秋·麥亞當斯飾）再次激起了她與這位偵探之間狂暴的關係，而一個神祕的新宿敵布萊克威爾（馬克·史壯飾）則策劃了一個可能毀滅國家的致命陰謀。"),
     
    ('subsection', 'BBC TV Series: Sherlock', 'BBC 電視劇：《新世紀福爾摩斯》'),
    ('paragraph',
     "This is a British mystery crime drama television series, thirteen episodes have been produced, with four three-part series airing from 2010 to 2017 and a special episode that aired on 1 January 2016. Sherlock Holmes (Benedict Cumberbatch) lives in early-21st century London and Dr. Watson (Martin Freeman) is a fairly young veteran of the Afghan war, less adoring and more active.",
     "這是一部英國懸疑犯罪電視連續劇，共製作了 13 集，於 2010 年至 2017 年播出了四季（每季三集），以及於 2016 年 1 月 1 日播出的一集特別篇。夏洛克·福爾摩斯（班奈狄克·康柏拜區飾）生活在 21 世紀初的倫敦，而華生醫生（馬丁·費里曼飾）則是阿富汗戰爭的年輕退伍軍人，他少了一點崇拜，多了一點主動。"),
     
    ('subsection', 'Sherlock Holmes Museum', '福爾摩斯博物館'),
    ('paragraph',
     "Situated at 221B Baker Street, London, Sherlock Holmes made this his residence from 1881 to 1904. His rooms have been faithfully maintained to give visitors from all around the globe an insight into this life. The setting is filled with authentic Victorian furniture and curiosities, and a treasure trove of items belonging to Sherlock, his friends and adversaries.",
     "福爾摩斯博物館位於倫敦貝克街 221B 號，福爾摩斯於 1881 年至 1904 年間在此居住。他的房間被忠實地維護著，以便讓來自全球各地的遊客能夠深入了解他的生活。這裡擺滿了真實的維多利亞時代家具與奇珍異寶，並且是屬於福爾摩斯、他的朋友和對手們物品的寶庫。"),
     
    ('subsection', 'HBO Asia TV Series: Miss Sherlock', 'HBO Asia 電視劇：《神探夏洛克小姐》'),
    ('paragraph',
     "This is a female-led adaptation of Sherlock Holmes detective stories, co-produced between HBO Asia and Hulu Japan. The show is primarily set in Tokyo, Japan, and both the main characters, based on Sherlock Holmes (Yuko Takeuchi) and Dr. Watson (Shihori Kanjiya), are played by actresses. It is the first major series to cast a woman as Holmes-like detective.",
     "這是一部以女性為主導的夏洛克·福爾摩斯偵探故事改編劇，由 HBO Asia 和日本 Hulu 聯合製作。該劇主要設定在日本東京，基於夏洛克·福爾摩斯（竹內結子飾）和華生醫生（貫地谷詩穗梨飾）的兩位主角皆由女演員飾演。這是首部將女性塑造成福爾摩斯式偵探的大型電視劇。"),
     
    ('subsection', 'Arsène Lupin & Herlock Sholmès', '亞森·羅蘋與赫洛克·索爾摩斯'),
    ('paragraph',
     "Arsène Lupin is a fictional gentleman thief and master of disguise created in 1905 by French writer Maurice Leblanc. The first story, “The Arrest of Arsène Lupin”, was published on 15 July 1905. Leblanc introduced Sherlock Holmes to Lupin in the short story “Sherlock Holmes Arrives Too Late” in June 1906. In it, an aged Holmes meets a young Lupin for the first time. After legal objections from Arthur Conan Doyle, the name was changed to “Herlock Sholmes”. In the second collection of Arsène Lupin stories, “Arsène Lupin versus Herlock Sholmès” published, featuring two adventures following a match of wits between Lupin and Herlock Sholmès.",
     "亞森·羅蘋是法國作家莫里斯·盧布朗於 1905 年創立的虛構紳士小偷與易容大師。第一篇故事《亞森·羅蘋被捕》發表於 1905 年 7 月 15 日。盧布朗在 1906 年 6 月的短篇故事《福爾摩斯來得太遲》中將福爾摩斯引入了亞森·羅蘋的故事。在故事中，年邁的福爾摩斯首次遇到了年輕的羅蘋。在亞瑟·柯南·道爾提出法律抗議後，名字被改為「赫洛克·索爾摩斯（Herlock Sholmes）」。在發表的第二部亞森·羅蘋故事集《亞森·羅蘋對決赫洛克·索爾摩斯》中，包含了兩篇描寫羅蘋與索爾摩斯智力對決的冒險故事。"),
     
    ('subsection', 'TV Mini Series: IQ246~ Kareinaru Jikembo', '電視劇：《IQ246～華麗事件簿～》'),
    ('paragraph',
     "Broadcasted in 2016, this mystery TV series depicts the protagonist 法門寺 沙羅駆 (Homonji Sharak) (Yuji Oda), who has an IQ of 246, solves difficult cases with his vast knowledge and brilliant reasoning. Names of the characters in this series are taken from Sherlock Holmes: the pronunciation of the protagonist's name “ほうもんじ しゃらく” is taken from the homonym of “Sherlock Holmes”; his guard from the Metropolitan Police Department, 和藤 奏子 (Souko Wato) (Tsuchiya Tao), her name \"わとう そうこ\" is taken from the homonym of the surname of Watson, the assistant of Sherlock Holmes, “John H. Watson”; Maria T. (Miki Nakatani), the person who e-mails perfect crime instruction to the prisoner, disguised as the forensic doctor, 森本朋美 (Tomomi Morimoto), her name \"マリア・ティー\" is taken from the homonym of “Professor Moriarty”, the enemy of Sherlock Holmes.",
     "這部於 2016 年播出的懸疑電視劇描述了主角法門寺沙羅驅（織田裕二飾），他擁有高達 246 的智商，憑藉其廣博的知識和精妙的推理來解決棘手案件。該劇中角色的名字皆取自福爾摩斯：主角的名字「ほうもんじ しゃらく（法門寺沙羅驅）」的發音與「Sherlock Holmes」諧音；他來自警視廳的護衛和藤奏子（土屋太鳳飾）的名字「わとう そうこ」與福爾摩斯助手華生醫生的姓氏「John H. Watson」諧音；而在劇中化身為法醫森本朋美（中谷美紀飾），並向囚犯寄送完美犯罪指示的神秘人物 Maria T，其名字「マリア・ティー（Maria T）」則是取自福爾摩斯的宿敵「莫里亞蒂教授（Professor Moriarty）」的諧音。")
]

if __name__ == "__main__":
    # Generate the detailed bilingual PDFs
    build_pdf("songs_and_singers_bilingual.pdf", "Unit: Songs and Singers", songs_content)
    build_pdf("sherlock_holmes_bilingual.pdf", "Unit: Sherlock Holmes at Different Times and Cultures", holmes_content)
    print("Done generating detailed bilingual PDFs.")
