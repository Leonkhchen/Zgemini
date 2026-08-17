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


# ================= 1. MODERN ARTS DATA =================
modern_arts_content = [
    ('section', 'Lead-in Questions', '導入問題'),
    ('paragraph',
     '1. Andy Warhol won frequent awards for his uniquely whimsical style, using his own blotted line technique and rubber stamps to create his drawings as a world-known commercial artist.',
     '1. 安迪·沃荷因其獨特奇幻的風格而頻繁獲獎，他利用自己首創的「吸墨線條」技術和橡皮印章來創作繪畫，成為一名享譽世界的商業藝術家。'),
    ('paragraph',
     '2. Kusama Yayoi becomes a central figure in the New York avant-garde, she has been acknowledged as one of the most important living artists of Japan.',
     '2. 草間彌生野心勃勃地成為紐約前衛藝術的核心人物，她已被公認為日本最重要的在世藝術家之一。'),
    
    ('section', 'Featured Artists', '藝術家介紹'),
    ('subsection', 'Andy Warhol (1928-1987)', '安迪·沃荷'),
    ('paragraph',
     'Andy Warhol (original name Andrew Warhola, 1928-1987) was an American illustrator, filmmaker and leading artist of 1960s Pop art movements. He was born in a Slovakian immigrant family in Pittsburgh, Pennsylvania, and graduated from the Carnegie Institute of Technology (now Carnegie Mellon University), Pittsburgh, with a degree in pictorial design in 1949. He then went to New York City, where he worked as a commercial illustrator.',
     '安迪·沃荷（原名 Andrew Warhola，1928-1987）是美國插畫家、電影製片人，也是1960年代波普藝術運動的領軍藝術家。他出生於賓夕法尼亞州奧克蘭的一個斯洛伐克移民家庭，並於1949年畢業於卡內基理工學院（現卡內基美隆大學），獲得圖案設計學位。隨後他前往紐約市，在那裡擔任商業插畫家。'),
    ('paragraph',
     'Warhol ventured into wide variety of art forms, including performance art, filmmaking and video installations. In 1960s, he unveiled the concept of Pop Art and showcased a collection of paintings that focused on mass-produced commercial goods: the screen-printed images of Marilyn Monroe, Campbell’s soup cans, Coca-Cola bottles, wooden replicas of Brillo soap pad boxes, and sensational newspaper stories.',
     '沃荷涉足了廣泛的藝術形式，包括行為藝術、電影製作和錄影裝置。在1960年代，他推出了波普藝術的概念，並展示了一系列以大量生產的商業商品為主題的畫作：包括瑪麗蓮·夢露、康寶濃湯罐頭、可口可樂瓶的絲網印刷圖像，Brillo肥皂盒的木製複製品，以及聳人聽聞的新聞故事。'),
    ('paragraph',
     'His artistic risks and constant experimentation with subjects and media made him a pioneer in almost all forms of visual art. His unconventional sense of style and his celebrity entourage helped him reach the mega-star status to which he aspired.',
     '他的藝術冒險和對主題與媒介的不斷嘗試，使他成為幾乎所有視覺藝術形式的先驅。他不落俗套的風格感和他的名人隨從，幫助他達到了他所嚮往的超級巨星地位。'),
     
    ('subsection', 'Kusama Yayoi (born 1929)', '草間彌生'),
    ('paragraph',
     'Kusama Yayoi (born in 1929) is a Japanese artist who self-described as an “obsessional artist,” known for her extensive use of polka dots and for her infinity installations. She also employed painting, sculpture, performance art in a variety of styles, including Pop art and Minimalism. She started to paint using polka dots and nets as motifs at around age ten, at about the time she began experiencing hallucinations that often involved fields of dots.',
     '草間彌生（Kusama Yayoi，1929年出生），是一位自稱為「偏執藝術家」的日本藝術家，以大量使用波點和她的無限裝置而聞名。她還採用了多種風格的繪畫、雕塑、行為藝術，包括波普藝術和極簡主義。她在大約十歲時開始使用波點和網作為圖案進行繪畫，大約在那個時候，她開始經歷經常涉及波點區域的幻覺。'),
    ('paragraph',
     'Kusama studied art from 1948 to 1949 at the Kyōto City Specialist School of Arts; in 1957, due to family conflict and the desire to become an artist drove her to move to the United States, where she settled in New York City, and then moved back to Japan in 1973. Today, her works can be found in enviable collections of the Los Angeles County Museum of Art, the National Museum of Modern Art in Tokyo, and The Museum of Modern Art in New York.',
     '草間彌生於1948年至1949年在京都市立美術工藝專門學校學習藝術；1957年，由於家庭衝突和成為藝術家的渴望，驅使她移居美國，並在紐約市定居，隨後於1973年返回日本。如今，她的作品可以在洛杉磯郡立美術館、東京國立近代美術館和紐約現代藝術博物館的珍貴收藏中找到。'),
     
    ('pagebreak',),
    
    ('section', 'Extended Content', '延伸內容'),
    ('subsection', 'The Andy Warhol Museum', '安迪·沃荷博物館'),
    ('paragraph',
     'Located in Pittsburgh, Pennsylvania, the museum holds the largest collection of Warhol’s artworks and archival materials. Paintings, drawings, commercial illustrations, sculptures, prints, photographs, wallpapers, sketchbooks, and books cover the entire range of Warhol’s career, from his early student work to pop art paintings and collaborations. It also offers sound series concerts, contemporary performances, online courses to the public. In addition, the ongoing “The Pop District” program aims at comprehensively transform Pittsburgh’s eastern North Shore through the power of arts, creativity, and economic development.',
     '位於賓夕法尼亞州匹茲堡，該博物館擁有最大數量的沃荷藝術作品和檔案材料。繪畫、素描、商業插圖、雕塑、版畫、照片、壁紙、素描本和書籍涵蓋了沃荷的整個職業生涯，從他早期的學生作品到波普藝術繪畫和合作作品。它還向公眾提供聲音系列音樂會、當代表演和線上課程。此外，正在進行的「波普區」計畫旨在通過藝術、創意和經濟發展的力量，全面改造匹茲堡東部的北岸。'),
     
    ('subsection', 'BBC Documentary: Modern Masters: Andy Warhol', 'BBC 紀錄片《現代大師：安迪·沃荷》'),
    ('paragraph',
     'It introduces the life and art styles of Andy Warhol, and his world-known works and skill screen painting. Warhol was one of the most influential artists of the second half of the 20th century, creating some of the most recognizable images ever produced, and embraced popular culture and commercial processes to produce work that appealed to the general public. He was one of the founding fathers of the Pop art movement, expanding the ideas of Duchamp by challenging the very definition of art.',
     '它介紹了安迪·沃荷的一生、藝術風格、世界知名的作品和絲網印刷技術。沃荷是20世紀下半葉最具影響力的藝術家之一，創作了一些有史以來最知名的圖像，並擁抱流行文化和商業流程，以創作出吸引大眾的作品。他是波普藝術運動的奠基人之一，通過挑戰藝術的定義來擴展杜象的想法。'),
     
    ('subsection', 'YAYOI KUSAMA Museum', '草間彌生博物館'),
    ('paragraph',
     'Yayoi Kusama Museum was founded by the avant-garde artist Yayoi Kusama, and is run by the Yayoi Kusama Foundation. It opened in 2017 with the aim of spreading and promoting Kusama’s art, exhibiting her works and related materials to contribute to the development of art as a whole.',
     '草間彌生博物館由前衛藝術家草間彌生創立，並由草間彌生基金會營運。它於2017年開館，旨在傳播和推廣草間彌生的藝術，展出她的作品和相關材料，為整個藝術的發展做出貢獻。'),
     
    ('subsection', 'Documentary: Yayoi Kusama – Obsessed with Polka Dots', '紀錄片《草間彌生：波點偏執》'),
    ('paragraph',
     'The nine decades of artist Yayoi Kusama’s life have taken her from rural Japan to the New York art scene to contemporary Tokyo, in a career in which she has continuously innovated and re-invented her style.',
     '藝術家草間彌生九十年的生命歷程將她從日本農村帶到紐約藝術界再到當代東京，在她的職業生涯中，她不斷創新並重新塑造自己的風格。')
]


# ================= 2. CREATIVITY DATA =================
creativity_content = [
    ('section', 'Lead-in Questions', '導入問題'),
    ('paragraph',
     'Have you ever won a prize? If so, what for? If you could be awarded for a prize, what would you like it to be awarded for? Does award always have to be serious? In this unit, we will learn about an award that is less serious but still scientifically important. Do you know what I am referring to?',
     '你曾獲得過獎項嗎？如果有，是為了什麼？如果你可以被授予一個獎項，你希望是為了什麼？獎項一定要很嚴肅嗎？在本單元中，我們將學習一個不那麼嚴肅但仍然具有科學重要性的獎項。你知道我指的是什麼嗎？'),
     
    ('section', 'Defining Creativity & Awards', '定義創造力與獎項'),
    ('paragraph',
     'Let us start by discussing ‘creativity’. We can see its definition in the dictionary is “the ability to produce new ideas or things using skill and imagination”. In order to own the ‘ability’ to be able to become creative, one must accumulate knowledge in the daily life, so that someday when you need the new knowledge, your brain could provide you enough information (our schema, or information base) to become your ‘inspiration’. The knowledge accumulation does not happen in one day, it has to go through a really complicated and long process to be able to store in our brain for later retrieval. This is why people who devote their time so much to become experts in some fields deserves our respect and should be awarded with great honor, such as scientists and researchers. Many awards are world-famous. Do you know the following awards?',
     '讓我們從討論「創造力」開始。我們可以看到它在字典中的定義是「利用技巧和想像力產生新想法或新事物的能力」。為了擁有能夠變得有創造力的「能力」，一個人必須在日常生活中積累知識，這樣當有一天你需要新知識時，你的大腦才能為你提供足夠的信息（我們的圖式或信息庫）來成為你的「靈感」。知識的積累不是一天完成的，它必須經歷一個非常複雜和漫長的過程，才能儲存在我們的大腦中以便日後檢索。這就是為什麼那些投入大量時間成為某些領域專家的人值得我們的尊敬，並應該被授予學術榮譽，例如科學家和研究人員。許多獎項是舉世聞名的。你知道以下獎項嗎？'),
     
    ('listitem', '1. For the highest achievement in film production? (Academy Awards / Oscars)', '1. 電影製作的最高成就獎？（奧斯卡金像獎）'),
    ('listitem', '2. To people who have done the most significant work in physics, chemistry, medicine, literature, and peace? (Nobel Prize)', '2. 頒給在物理、化學、醫學、文學和和平領域做出最重大貢獻的人？（諾貝爾獎）'),
    ('listitem', '3. For the most excellent work in journalist, fiction, and non-fiction in the U.S.? (Pulitzer Prize)', '3. 頒給美國最優秀的新聞、小說和非小說作品？（普立茲獎）'),
    ('listitem', '4. To the worst film of the year? (Golden Raspberry Awards / Razzies)', '4. 頒給年度最爛的電影？（金酸莓獎）'),
    ('listitem', '5. To people whose work in television has been excellent? (Emmy Awards)', '5. 頒給在電視領域表現卓越的人？（艾美獎）'),
    ('listitem', '6. In the U.S. for special achievement in the popular music recording industry? (Grammy Awards)', '6. 美國流行音樂錄音工業的特殊成就獎？（格萊美獎）'),
    ('listitem', '7. To the best film at the Cannes Film Festival in France? (Palme d\'Or)', '7. 法國坎城影展的最佳影片獎？（金棕櫚獎）'),
    ('listitem', '8. To the highest scorer in soccer? (Golden Boot)', '8. 足球賽中的神射手獎？（金靴獎）'),
    
    ('paragraph',
     'My guess is, at least, you will get “the Nobel Prize” right. Most of us know the Nobel Prize; however, have you heard about the “Ig Nobel Prize”? This is the prize that is getting more and more attention nowadays. Therefore, let us learn about it, so we can keep up with the world.',
     '我的猜測是，至少你會答對「諾貝爾獎」。我們大多數人都知道諾貝爾獎；然而，你聽說過「搞笑諾貝爾獎」嗎？這是如今越來越受到關注的獎項。因此，讓我們來了解它，這樣我們才能跟上世界的腳步。'),
     
    ('section', 'The Ig Nobel Prize', '搞笑諾貝爾獎'),
    ('paragraph',
     'First, the name of the award requires some English knowledge. The word looks like it has some negative connotation. So, the name of the award is a play of the word ‘ignoble’. When you separate ‘ig’ and ‘noble’, and change the spelling of ‘noble’ into ‘nobel’, then you get “Ig Nobel” prize. So, the name gives us some ideas about what the award is. Ig Nobel Prize is an actual award. It is awarded each year to people, usually scientists, who have made significant achievements that are funny and should not be reproduced. The first ceremonies of the Ig Nobel Prize were held at MIT, but later moved to Harvard University due to the objection of the MIT administrators.',
     '首先，這個獎項的名稱需要一些英文知識。這個詞看起來有一些負面的含義。所以，這個獎項的名字是「ignoble」（不光彩的/卑微的）一詞的雙關語。當你把「ig」和「noble」分開，並把「noble」的拼寫改成「nobel」，你就得到了「搞笑諾貝爾獎（Ig Nobel Prize）」。所以，這個名字給了我們一些關於這個獎項是什麼的概念。搞笑諾貝爾獎是一個真實存在的獎項。它每年頒發給那些做出了有趣且不應被複製的重大成就的人，通常是科學家。搞笑諾貝爾獎的第一屆頒獎典禮在麻省理工學院（MIT）舉行，但後來由於麻省理工學院管理人員的反對，移到了哈佛大學舉行。'),
    ('paragraph',
     'The founder of the Ig Nobel awards, Marc Abrahams, is with the Improbable Research. Marc Abrahams together with the governors of Improbable Research choose winners of the Ig Nobel Prize every year. In his inspiring talk at TedTalks in 2014 “Marc Abrahams: A science award that makes you laugh, then think”, he tells the world about why those winners of the Ig Nobel Prize are as important as the real Nobel Prize winners. Silly science can make the public interested in serious science and so the Igs are of critical importance. In his talk, he said:',
     '搞笑諾貝爾獎的創始人馬克·亞伯拉罕斯（Marc Abrahams）任職於《不可思議研究年報》。馬克·亞伯拉罕斯與《不可思議研究年報》的理事們每年選出搞笑諾貝爾獎的得主。在2014年一場啟發人心的Ted演講中，他發表了《搞笑諾貝爾獎：讓你笑，然後思考的科學獎》，向世界介紹了為什麼這些搞笑諾貝爾獎得主與真正的諾貝爾獎得主一樣重要。滑稽的科學可以讓公眾對嚴肅的科學產生興趣，因此搞笑諾貝爾獎至關重要。他在演講中說：'),
    ('paragraph',
     '“In 1991, I, together with bunch of other people, started the Ig Nobel prize ceremony. Every year we give out 10 prizes. The prizes are based on just one criteria. It’s very simple. It’s that you’ve done something that makes people laugh and then think. What you’ve done makes people laugh and then think. Whatever it is, there’s something about it that when people encounter it at first, their only possible reaction is to laugh. And then a week later, it’s still rattling around in their heads and all they want to do is tell their friends about it. That’s the quality we look for.”',
     '「在1991年，我和其他一群人一起創辦了搞笑諾貝爾獎頒獎典禮。我們每年頒發10個獎項。這些獎項僅基於一個標準。它非常簡單。那就是你做了一些讓人們發笑然後思考的事情。不論那是什麼，當人們第一次接觸到它時，他們唯一的反應就是笑。然後一週後，它仍然在他們的大腦中盤旋，而他們唯一想做的就是告訴他們的朋友。這就是我們尋找的品質。」'),
    ('paragraph',
     'So, it is not as silly as it looks. The Improbable Research takes it very seriously. Every year, they choose their 10 winners based on this criteria from over 9,000 new nominations. After they decide the winners, they will contact the winners very quietly and offer them the chance to decline the award. Abrahams said “Happily for us, almost everyone who’s offered a prize decides to accept.” See, people in science have sense of humor too. The Ig Nobel Prize design is different every year, usually handmade and cheap. The ceremony at Harvard University takes place at Harvard’s biggest meeting place and classroom, which fits 1,100 people. Abrahams described:',
     '所以，它並不像看起來那麼愚蠢。《不可思議研究年報》非常認真地對待它。每年，他們從9,000多個新提名中，基於這個標準選出10位得主。在決定得主後，他們會非常低調地與得主聯繫，並給予他們拒絕接受獎項的機會。亞伯拉罕斯說：「對我們來說很幸運的是，幾乎每個被授予獎項的人都決定接受。」你看，科學界的人也很有幽默感。搞笑諾貝爾獎每年的設計都不同，通常是手工製作且廉價的。在哈佛大學舉行的典禮在哈佛最大的會議場所和教室舉行，可容納1,100人。亞伯拉罕斯描述道：'),
    ('paragraph',
     '“It’s jammed to the gills, and up on the stage, waiting to shake your hand, waiting to hand you your Ig Nobel prize, are a bunch of Nobel prize winners. That’s the heart of the ceremony. The winners are kept secret until that moment, even the Nobel laureates who will shake their hand don’t know who they are until they’re announced.”',
     '「典禮現場擠得水洩不通，在講台上等待與你握手、等待將搞笑諾貝爾獎遞交給你的是一群真正的諾貝爾獎得主。這就是典禮的核心。得主的身份直到那一刻都是保密的，甚至連將與他們握手的諾貝爾獎得主在宣佈之前也不知道他們是誰。」'),
     
    ('pagebreak',),
    
    ('subsection', 'Elena Bodnar’s Emergency Mask', '埃琳娜·波德納爾的應急口罩'),
    ('paragraph',
     'He introduced several winning achievements in his talk. One of them relates to our life recently is the emergency mask. “The final thing that I want to tell you about is a prize we gave to Dr. Elena Bodnar. Dr. Elena Bodnar invented a brassiere that in an emergency can be quickly separated into a pair of protective face masks. One to save your life, one to save the life of some lucky bystander. (Laughter) Why would someone do this, you might wonder. Dr. Bodnar came to the ceremony and she explained that she grew up in Ukraine. She was one of the doctors who treated victims of the Chernobyl power plant meltdown. And they later discovered that a lot of the worst medical problems came from the particles people breathed in. So she was always thinking after that about could there be some simple mask that was available everywhere when the unexpected happens. Years later, she moved to America. She had a baby. One day she looked, and on the floor, her infant son had picked up her bra, and had her bra on his face. And that\'s where the idea came from. She came to the Ig Nobel ceremony with the first prototype of the bra and she demonstrated.”',
     '他在演講中介紹了幾項獲獎成就。其中一項與我們最近的生活有關，那就是應急口罩。「我想告訴你們的最後一項是我們頒給埃琳娜·波德納爾（Elena Bodnar）博士的一個獎項。波德納爾博士發明了一款胸罩，在緊急情況下，它可以迅速拆卸成一對保護性口罩。一個用來救你自己的命，另一個用來救某個幸運的旁觀者。（笑聲）你可能會想，為什麼會有人做這件事？波德納爾博士來到典禮現場，她解釋說她在烏克蘭長大。她是治療車諾比核電廠熔毀事故受害者的醫生之一。他們後來發現，許多最嚴重的醫療問題都來自人們吸入的微粒。所以從那以後，她一直在思考，當意外發生時，是否可以有一種隨處可得的簡單口罩。多年後，她搬到了美國。她生了個寶寶。有一天她看過去，在地上，她嬰兒期的兒子撿起了她的胸罩，並把胸罩戴在臉上。這就是這個靈感的來源。她帶著胸罩的第一個原型來到搞笑諾貝爾獎典禮，並進行了演示。」'),
    ('paragraph',
     'Dr. Bodnar took off a brassiere and made two emergency masks to put on Professor Paul Krugman, the Nobel laureate in economics in 2008 and Professor Wolfgang Ketterle, the Nobel laureate in Physics in 2001 in the ceremony. Everyone in the ceremony laughed, I laughed when I first saw it a few years back too. However, after the Covid pandemic, if we think more seriously about it, this is not goofy science anymore; it may just save lives when an emergency happens. Other discoveries Abrahams mentioned in his talk also made contributions to the real science. For instance, Doctor Ivan Schwab’s research on “Why don’t woodpeckers get headaches?” (2006) and Dr. Emmanuel Ben-Boussan’s research on how doctors could minimize the danger of exploding patients while they perform colonoscopies in 2012. There are other famous winners, and I would like to present them to you selectively based on the criteria of level of interest, novelty, category, level of acceptance, level of comprehension and perception and language; therefore, some award winners which require professional knowledge are not listed for they require high level of scientific and linguistic knowledge.',
     '波德納爾博士脫下胸罩，製成兩個應急口罩，並在典禮上戴在2008年諾貝爾經濟學獎得主保羅·克魯曼（Paul Krugman）教授和2001年諾貝爾物理學獎得主沃爾夫岡·克特勒（Wolfgang Ketterle）教授的臉上。典禮上的每個人都笑了，幾年前我第一次看到它時也笑了。然而，在新冠疫情大流行之後，如果我們更嚴肅地思考它，這不再是愚蠢的科學了；當緊急情況發生時，它真的可能挽救生命。亞伯拉罕斯在演講中提到的其他發現也對真正的科學做出了貢獻。例如，伊凡·施瓦布（Ivan Schwab）博士關於「為什麼啄木鳥不會頭痛？」的研究（2006年），以及伊曼紐爾·本-布桑（Emmanuel Ben-Boussan）博士關於醫生在2012年進行大腸鏡檢查時如何將患者爆炸危險降至最低的研究。還有其他著名的得主，我想根據趣味性、新穎性、類別、接受度、理解力和感知度等標準選擇性地向大家展示；因此，一些需要專業知識的獲獎者並未列出，因為他們需要高水準的科學和語言知識。'),

    ('subsection', 'Selective List of Ig Nobel Winners (1994 - 2022)', '搞笑諾貝爾獎得主精選清單（1994 - 2022年）'),
    ('listitem', '1994 Peace: Lee Kuan Yew, for his thirty-year study of the effects of punishing three million citizens of Singapore whenever they spat, chewed gum, or fed pigeons.', '1994年和平獎：新加坡前總理李光耀獲獎，因其對處罰隨地吐痰、嚼口香糖或餵鴿子的三百萬新加坡公民的效果進行了長達三十年的研究。'),
    ('listitem', '1995 Medicine: Robert Beaumont, for his incisive study “Patient Preference for Waxed or Unwaxed Dental Floss”.', '1995年醫學獎：羅伯特·比蒙（Robert Beaumont）獲獎，因其深入的研究「患者對打蠟或不打蠟牙線的偏好」。'),
    ('listitem', '1995 Nutrition: John Martinez, for luak coffee, the world’s most expensive coffee, which is made from coffee beans ingested and excreted by the luak, a bobcat-like animal native to Indonesia.', '1995年營養學獎：授予 J. Martinez & Company 的約翰·馬丁內斯（John Martinez），因為「麝香貓咖啡」是世界上最昂貴的咖啡，由印尼本土一種類似山貓的動物吞食並排泄的咖啡豆製成。'),
    ('listitem', '1995 Peace: The Legislative Yuan of the Republic of China (Taiwan), for demonstrating that “politicians gain more by punching, kicking and gouging each other than by waging war against other nations”, in the context of legislative violence.', '1995年和平獎：授予中華民國（台灣）立法院，因為他們證明了「在立法暴力背景下，政治家通過互相拳打腳踢和挖眼珠獲得的利益，比向其他國家發動戰爭更多」。'),
    ('listitem', '1996 Physics: Robert Matthews of Aston University, England, for his studies of Murphy’s Law, and especially for demonstrating that toast often falls on the buttered side.', '1996年物理學獎：授予英國阿斯頓大學的羅伯特·馬修斯（Robert Matthews），因其對墨菲定律的研究，特別是證明了「塗了奶油的吐司經常掉落在塗有奶油的一面」。'),
    ('listitem', '1997 Economics: Akihiro Yokoi and Aki Maita for diverting millions of man-hours of work into the husbandry of virtual pets (Tamagotchi).', '1997年經濟學獎：授予橫井昭裕和真板亞紀，因為他們將數百萬工時引導到虛擬寵物（電子雞）的飼養中。'),
    ('listitem', '1999 Literature: The British Standards Institute for its six-page specification of the proper way to make a cup of tea.', '1999年文學獎：授予英國標準協會，因為其制定了「如何沖泡一杯好茶」的六頁規範。'),
    ('listitem', '1999 Sociology: Steve Penfold, of York University in Toronto, for doing his PhD thesis on the history of Canadian doughnut shops.', '1999年社會學獎：授予多倫多約克大學的史蒂夫·彭福爾德（Steve Penfold），因其對加拿大甜甜圈店歷史的博士論文。'),
    ('listitem', '2000 Chemistry: Donatella Marazziti et al. of University of Pisa, Italy, and Hagop Akiskal of the University of California, San Diego, for their discovery that, biochemically, romantic love may be indistinguishable from having severe obsessive-compulsive disorder.', '2000年化學獎：授予義大利比薩大學的 Donatella Marazziti 等人，以及加州大學聖地牙哥分校的 Hagop Akiskal，因為他們發現「從生物化學角度看，浪漫的愛與嚴重的強迫症可能無法區分」。'),
    ('listitem', '2000 Computer Science: Chris Niswander of Tucson, Arizona, for inventing PawSense, software that detects when a cat is walking across your computer keyboard.', '2000年計算機科學獎：授予亞利桑那州圖森市的克里斯·尼斯萬德（Chris Niswander），因為他發明了 PawSense，這是一種能檢測貓何時在電腦鍵盤上走過的軟體。'),
    ('listitem', '2002 Hygiene: Eduardo Segura, from Tarragona, Catalonia (Spain), for inventing a washing machine for cats and dogs.', '2002年衛生獎：授予西班牙加泰羅尼亞的 Eduardo Segura，因為他發明了貓狗專用的洗滌機。'),
    ('listitem', '2002 Literature: Vicki L. Silvers of the University of Nevada, Reno and David S. Kriner of Central Missouri State University, for their colorful report “The Effects of Pre-Existing Inappropriate Highlighting on Reading Comprehension.”', '2002年文學獎：授予內華達大學的 Vicki L. Silvers 和中央密蘇里州立大學的 David S. Kriner，因其發表的報告《預先存在的不當螢光筆標記對閱讀理解的影響》。'),
    ('listitem', '2003 Interdisciplinary Research: Stefano Ghirlanda, Liselotte Jansson, and Magnus Enquist of Stockholm University, for their inevitable report “Chicken Prefer Beautiful Humans.”', '2003年跨學科研究獎：授予斯德哥爾摩大學的 Stefano Ghirlanda 等人，因其報告《雞偏愛漂亮的人類》。'),
    ('listitem', '2004 Peace: Daisuke Inoue of Hyogo Prefecture, Japan, for inventing Karaoke, thereby providing an entirely new way for people to learn to tolerate each other.', '2004年和平獎：授予日本兵庫縣的井上大佑，因為他發明了卡拉OK，從而為人們提供了一種學習容忍彼此的全新方式。'),
    ('listitem', '2004 Psychology: Daniel Simons of the University of Illinois at Urbana-Champaign and Christopher Chabris of Harvard University, for demonstrating that when people pay close attention to something, it is all too easy to overlook anything else – even a woman in a gorilla suit.', '2004年心理學獎：授予伊利諾大學香檳分校的 Daniel Simons 和哈佛大學的 Christopher Chabris，因為他們證明了「當人們密切關注某事時，很容易忽視其他任何事情——甚至是穿著大猩猩服裝的女人」。'),
    ('listitem', '2004 Public Health: Jillian Clarke of the Chicago High School for Agricultural Science, and the Howard University, for investigating the scientific validity of the five-second rule about whether it is safe to eat food that has been dropped on the floor.', '2004年公共衛生獎：授予芝加哥農業科學高中的 Jillian Clarke 和霍華德大學，因為他們調查了關於「掉在地上的食物在五秒鐘內吃掉是否安全」的五秒定律的科學有效性。'),
    ('listitem', '2005 Economics: Gauri Nanda of the Massachusetts Institute of Technology, for inventing Clocky, an alarm clock that runs away and hides, repeatedly, thus ensuring that people get out of bed, and thus theoretically adding many productive hours to the workday.', '2005年經濟學獎：授予麻省理工學院的 Gauri Nanda，因為她發明了 Clocky，這是一個會逃跑並躲藏的鬧鐘，從而確保人們起床，理論上為工作日增加了許多生產工時。'),
    ('listitem', '2006 Physics: Nic Sveson and Piers Barnes of the Australian Commonwealth Scientific and Industrial Research Organisation, for calculating the number of photographs that must be taken to (almost) ensure that nobody in a group photo will have their eyes closed.', '2006年物理學獎：授予澳大利亞聯邦科學與工業研究組織的 Nic Sveson 和 Piers Barnes，因為他們計算了「為確保合照中幾乎沒有人閉眼，必須拍攝的照片數量」。'),
    ('listitem', '2008 Medicine: Rebecca Waber et al., for demonstrating that expensive placebos are more effective than inexpensive placebos.', '2008年醫學獎：授予 Rebecca Waber 等人，因為他們證明了「昂貴的安慰劑比便宜的安慰劑更有效」。'),
    ('listitem', '2009 Medicine: Donald L. Unger of Thousand Oaks, California, US, for investigating a possible cause of arthritis of the fingers, by diligently cracking the knuckles of his left hand but not his right hand every day for 50 years.', '2009年醫學獎：授予加州 Donald L. Unger，因為他通過每天堅持捏響自己左手關節而不捏右手關節持續50年，來調查指關節炎的可能原因。'),
    ('listitem', '2009 Veterinary Medicine: Catherine Douglas and Peter Rowlinson of Newcastle University, UK, for showing that cows with names give more milk than cows that are nameless.', '2009年獸醫學獎：授予英國紐卡索大學的 Catherine Douglas 和 Peter Rowlinson，因為他們證明了「有名字的母牛比無名字的母牛產奶更多」。'),
    ('listitem', '2010 Peace: Richard Stephens et al. of Keele University, UK, for confirming the widely held belief that swearing relieves pain.', '2010年和平獎：授予英國基爾大學的 Richard Stephens 等人，因為他們證實了「說髒話可以緩解疼痛」這一廣泛流傳的信念。'),
    ('listitem', '2011 Peace: Arturas Zuokas, the mayor of Vilinius, Lithuania, for demonstrating that the problem of illegally parked luxury cars can be solved by running them over with a tank.', '2011年和平獎：授予立陶宛維爾紐斯市長 Arturas Zuokas，因為他證明了「非法停放豪華轎車的問題可以通過用坦克將其壓扁來解決」。'),
    ('listitem', '2013 Probability: Bert Tolkamp et al., for making two related discoveries: First, that the longer a cow has been lying down, the more likely that cow will soon stand up; and second, that once a cow stands up, you cannot easily predict how soon that cow will lie down again.', '2013年概率獎：授予 Bert Tolkamp 等人，因為他們做出了兩個相關的發現：首先，母牛躺下的時間越長，牠很快站起來的可能性就越大；其次，一旦母牛站起來，你無法輕易預測牠很快會再躺下。'),
    ('listitem', '2014 Art: Marina de Tommaso et al., for measuring the relative pain people suffer while looking at an ugly painting, rather than a pretty painting, while being shot in the hand by a powerful laser beam.', '2014年藝術獎：授予 Marina de Tommaso 等人，因為他們測量了「當人們的手被強大的雷射光束照射時，看著一幅醜陋的畫作比看著一幅美麗的畫作，所承受的相對疼痛感」。'),
    ('listitem', '2014 Physics: Kiyoshi Mabuchi et al., for measuring the amount of friction between a shoe and a banana skin, and between a banana skin and the floor, when a person steps on a banana skin that is on the floor.', '2014年物理學獎：授予馬淵清資等人，因為他們測量了「當人踩到地上的香蕉皮時，鞋子與香蕉皮之間，以及香蕉皮與地面之間的摩擦力」。'),
    ('listitem', '2015 Economics: The Bangkok Metropolitan Police, for offering to pay policemen extra cash if the policemen refuse to take bribes.', '2015年經濟學獎：授予曼谷大都會警察局，因為他們提出如果警察拒絕收受賄賂，將向警察發放額外的現金。'),
    ('listitem', '2017 Anatomy: James Heathcote, for his medical research study “Why Do Old Men Have Big Ears?”', '2017年解剖學獎：授予 James Heathcote，因其醫學研究報告《為什麼老年人有大耳朵？》。'),
    ('listitem', '2018 Anthropology: Tomas Persson et al., for collecting evidence in a zoo that chimpanzees imitate humans about as often, and about as well, as humans imitate chimpanzees.', '2018年人類學獎：授予 Tomas Persson 等人，因為他們在動物園收集證據，證明「黑猩猩模仿人類的頻率和質量與人類模仿黑猩猩差不多」。'),
    ('listitem', '2019 Psychology: Fritz Strack, for discovering that holding a pen in one’s mouth makes one smile, which makes one happier – and for then discovering that it does not.', '2019年心理學獎：授予 Fritz Strack，因為他發現「口中含筆會讓人微笑，從而使人更快樂——而隨後發現其實並不會」。'),
    ('listitem', '2020 Medical Education: Jair Bolsonaro of Brazil, Boris Johnson of the United Kingdom, Narendra Modi of India, Andrés Manuel López Obrador of Mexico, Alexander Lukashenko of Belarus, Donald Trump of the United States, Recep Tayyip Erdoğan of Turkey, Vladimir Putin of Russia, and Gurbanguly Berdimuhamedow of Turkmenistan, for using the COVID-19 viral pandemic to teach the world that politicians can have a more immediate effect on life and death than scientists and doctors can.', '2020年醫學教育獎：授予巴西總統波索納洛、英國首相強森、印度總理莫迪、美國總統川普、俄羅斯總統普丁等人，因為他們「利用新冠疫情向世界證明，政治家對生死的直接影響，可以比科學家和醫生更即時」。'),
    ('listitem', '2021 Physics: Alessandro Corbetta et al., for conducting experiments to learn why pedestrians do not constantly collide with other pedestrians.', '2021年物理學獎：授予 Alessandro Corbetta 等人，因為他們進行了實驗，以了解「為什麼行人在路上不會經常與其他行人相撞」。'),
    ('listitem', '2022 Applied Cardiology: Eliska Prochazkova et al., for seeking and finding evidence that when new romantic partners meet for the first time and feel attracted to each other, their heart rates synchronize.', '2022年應用心臟病學獎：授予 Eliska Prochazkova 等人，因為他們尋找並發現了證據，證明「當新的浪漫伴侶第一次見面並感到彼此吸引時，他們的心率會同步」。'),
    ('listitem', '2022 Literature: Eric Martínez, Francis Mollica, and Edward Gibson, for analyzing what makes legal documents unnecessarily difficult to understand.', '2022年文學獎：授予 Eric Martínez 等人，因為他們分析了「是什麼讓法律文件變得不必要地難以理解」。'),
    ('listitem', '2022 Medicine: Marcin Jasiński et al., for showing that when patients undergo some forms of toxic chemotherapy, they suffer fewer harmful side effects when ice cream replaces one traditional component of the procedure.', '2022年醫學獎：授予 Marcin Jasiński 等人，因為他們表明「當患者接受某些形式的有毒化療時，如果用冰淇淋代替該療程中的一個傳統成分，他們所遭受的有害副作用會更少」。'),
    ('listitem', '2022 Engineering: Gen Matsuzaki et al., for trying to discover the most efficient way for people to use their fingers when turning a knob.', '2022年工程學獎：授予 Gen Matsuzaki 等人，因為他們試圖發現「人們在轉動旋鈕時使用手指的最有效方式」。'),
    ('listitem', '2022 Peace: Junhui Wu et al., for developing an algorithm to help gossipers decide when to tell the truth and when to lie.', '2022年和平獎：授予 Junhui Wu 等人，因為他們開發了一種算法，以幫助「傳播閒話者決定何時說真話、何時說謊」。'),
    ('listitem', '2022 Economics: Alessandro Pluchino, Alessio Emanuele Biondo, and Andrea Rapisarda, for explaining, mathematically, why success most often goes not to the most talented people, but instead to the luckiest.', '2022年經濟學獎：授予 Alessandro Pluchino 等人，因為他們用數學解釋了「為什麼成功最常不屬於最有才華的人，而是屬於最幸運的人」。'),
    
    ('paragraph',
     'Of course, we are not asking you to memorize these winners and their awards. What I would like to say in this unit is to show you how interesting science can be and how people who devote their lives into a specific area deserve our respect.',
     '當然，我們並不是要你記住這些獲獎者和他們的獎項。在這個單元中，我想說的是向你展示科學可以有多麼有趣，以及那些將一生奉獻給特定領域的人如何值得我們的尊敬。')
]


# ================= 3. VACCINATION DATA =================
vaccination_content = [
    ('section', 'Lead-in', '導入資訊'),
    ('paragraph',
     'Coronavirus Disease 2019 (COVID-19) first broke out at Wuhan city of China in early December 2019. It has rapidly widespread in almost every country around the world and has become a global public health crisis. The virus was originated in bats in Huanan seafood and animal market in China, infected to humans and transmitted from person to person. Globally, as of 23, December 2022, there have been 651,918,402 confirmed cases of COVID-19, including 6,656,601 deaths, reported by WHO.',
     '2019新型冠狀病毒病（COVID-19）於2019年12月初在中國武漢市首次爆發。它已在世界各地的幾乎每個國家迅速傳播，並已成為全球公共衛生危機。該病毒起源於中國華南海鮮及野生動物市場的蝙蝠，感染人類並在人與人之間傳播。全球範圍內，截至2022年12月23日，世界衛生組織（WHO）報告了 651,918,402 例確診病例，其中包含 6,656,601 例死亡。'),
     
    ('section', 'Words You Should Learn', '你應該學習的字詞'),
    ('subsection', 'Lockdown', '封城 / 封鎖'),
    ('paragraph',
     'It means “an emergency situation in which people are not allowed to freely enter, leave, or move around in a building or area because of danger” (Cambridge Dictionary). Aimed at curbing the virus’ spread, countries around the world enforced restrictions of business time and only essential business were allowed to remain open.',
     '它意味著「由於危險，人們不被允許自由進入、離開或在建築物或區域內移動的緊急情況」（《劍橋詞典》）。為了遏制病毒的傳播，世界各國強制限制商業營業時間，僅允許維持基本運作的行業保持開放。'),
    ('paragraph',
     'Beginning with the first lockdown in China\'s Hubei province and nationwide in Italy in March, lockdowns continued to be implemented in many countries throughout 2020 and 2021. The world\'s longest continuous lockdown lasting 234 days took place in Buenos Aires, Argentina in 2020. As of October 2021, the city of Melbourne, Australia, and certain cities in Peru and Chile spent the most cumulative days in lockdown over separate periods, although measures varied among these countries.',
     '從3月中國湖北省的首次封鎖以及義大利全國範圍內的封鎖開始，封鎖措施在整個2020年和2021年繼續在許多國家實施。2020年，阿根廷布宜諾斯艾利斯發生了世界上持續時間最長的連續封鎖，長達 234 天。截至2021年10月，澳洲墨爾本以及秘魯和智利的某些城市在不同時期實施的封鎖累計天數最多，儘管這些國家的措施各有不同。'),
     
    ('subsection', 'School Closure', '學校關閉'),
    ('paragraph',
     'The COVID-19 crisis has significantly affected the education sector across all regions. Full and partial school closures have devastating consequences for children’s learning and wellbeing. The majority of schoolchildren worldwide rely on their schools as a place where they can interact with their peers, seek support, access health and immunization services and a nutritious meal. The longer schools remain closed, the longer children are cut off from these critical elements of childhood.',
     '新冠病毒危機嚴重影響了所有地區的教育部門。全面和部分學校關閉對兒童的學習和福祉造成了毀滅性的後果。全球大多數男女學童都依賴學校作為與同伴互動、尋求支持、獲得健康和免疫儲備接種服務以及營養膳食的場所。學校關閉的時間越長，兒童與童年這些關鍵元素的隔絕時間就越長。'),
    ('paragraph',
     'The most vulnerable children and those unable to access remote learning are at an increased risk of never returning to the classroom, and even being forced into child marriage or child labor.',
     '最脆弱的兒童和那些無法進行遠程學習的兒童面臨著永遠無法重返課堂的更大風險，甚至被迫面臨童婚或童工。'),
    ('paragraph',
     'Except east Asia, which commenced school closure in January–February 2020, by the end of March school closure affected the normal academic routine of 1.5 billion learners (84% worldwide total) across 169 countries of the world.',
     '除東亞於2020年1月至2月開始關閉學校外，到3月底，關閉學校影響了全球169個國家的 15 億學習者（佔全球總數的84%）的正常學術常規。'),
     
    ('pagebreak',),
    
    ('subsection', 'Reopen / Lift Lockdown', '重新開放 / 解除封鎖'),
    ('paragraph',
     'Countries worldwide are starting to lift restrictions that were first imposed in 2020 to slow the spread of COVID-19 — including rules that governed travel, socializing, mask wearing and self-isolation. For example, all legal restrictions related to COVID-19, including required masking in public and self-isolation following a positive test, are being scrapped in the United Kingdom. Poland, Slovakia and Iceland have removed the requirement to wear masks outdoors in public and relaxed rules on gatherings, including reopening nightclubs and lifting capacity limits.',
     '全球各國開始解除2020年為減緩疫情傳播而實施的限制措施——包括限制旅行、社交、佩戴口罩和自我隔離的規定。例如，在英國，所有與 COVID-19 相關的法律限制，包括在公共場所強制佩戴口罩和檢測陽性後的自我隔離，都已被取消。波蘭、斯洛伐克和冰島取消了在公共戶外場所佩戴口罩的要求，並放寬了關於聚會的規定，包括重新開放夜總會和取消容納量限制。'),
     
    ('subsection', 'Vaccine', '疫苗'),
    ('paragraph',
     'There are several COVID-19 vaccines validated for use by WHO, including the AstraZeneca, the Pfizer-BioNTech (BNT), the Moderna, and so on. According to WHO, vaccines are a critical tool in the battle against COVID-19, and getting vaccinated is one of the best ways to protect yourself and others from COVID-19. Vaccines train our immune system to recognize the target virus and create antibodies to fight off the disease without getting the disease itself. After vaccination, the body is ready to fight the virus if it is later exposed to it, thereby preventing illness.',
     '世界衛生組織（WHO）已經驗證了幾種可用於臨床的 COVID-19 疫苗，包括阿斯特捷利康（AstraZeneca，即AZ疫苗）、輝瑞-BioNTech（BNT疫苗）、莫德納（Moderna）等等。世界衛生組織表示，疫苗是抗擊 COVID-19 戰役中的關鍵工具，接種疫苗是保護自己和他人免受 COVID-19 侵害的最佳方法之一。疫苗訓練我們的免疫系統識別目標病毒並產生抗體來對抗疾病，而不會讓我們自己感染疾病。接種疫苗後，如果身體日後接觸到病毒，就已經做好了對抗病毒的準備，從而預防疾病。'),
     
    ('section', 'Situation and Vaccination in Taiwan', '台灣疫情與疫苗接種情況'),
    ('paragraph',
     'According to statistics from Taiwan Centers for Disease Control, as of 27 December 2022, there are a total of 8,738,114 confirmed cases of COVID-19 and 15,120 deaths in Taiwan. On 19 March 2021, the Central Epidemic Command Center (CECC) in Taiwan announced that vaccinations would start on 22 March. In addition, CECC announced vaccination plan listing prioritization, which included 10 prioritized groups, such as health workers, other frontline workers and seniors were the first to be inoculated with the vaccine. After inoculation, individuals receive an official yellow card that records individuals\' vaccination information. On 6 July, CECC announced the creation of Taiwan Domestic COVID-19 Vaccination Appointment Platform, allowing the digitalization of COVID-19 vaccination sign up and appointments. As of 27 October 2022, 65,115,783 doses were administered, and 94% of the Taiwan population has received at least one dose, and the second dose coverage reaches to 88.8%.',
     '根據台灣衛生福利部疾病管制署的統計，截至2022年12月27日，台灣累計確診病例 8,738,114 例，死亡 15,120 例。2021年3月19日，台灣中央流行疫情指揮中心（CECC）宣佈疫苗接種將於3月22日開始。此外，指揮中心宣佈了疫苗接種優先順序計劃，其中包括 10 個優先群體，例如醫事人員、其他第一線工作人員和老年人是第一批接種疫苗的人。接種疫苗後，個人會收到一張記錄個人接種信息的官方黃色卡片（即黃卡）。7月6日，指揮中心宣佈建立台灣本地 COVID-19 疫苗接種預約平台，實現疫苗接種登記和預約的數位化。截至2022年10月27日，已累計接種 65,115,783 劑，已有 94%的台灣人口接種了至少一劑疫苗，第二劑覆蓋率達到 88.8%。'),
     
    ('section', 'Extended Content', '延伸內容'),
    ('paragraph',
     'In order to disseminate information about COVID-19 prevention, CECC made short videos in various languages, including English, Thai, Vietnamese, Indonesian, Filipino, etc., ensuring no one was left behind.',
     '為了傳播有關 COVID-19 預防的信息，中央流行疫情指揮中心製作了多種語言的短片，包括英語、泰語、越南語、印尼語、菲律賓語等，以確保不遺漏任何人。'),
    ('subsection', 'Video Transcript: 5 Tips to Prevent Epidemics', '影片逐字稿：日常防疫五大貼士'),
    ('paragraph',
     'Hello! I’m Dr. Felice O’Donnell. COVID prevention is part of our daily lives. In this video, let’s review together, five tips to prevent COVID.',
     '你好！我是費莉絲·歐唐納（Felice O\'Donnell）博士。預防新冠病毒是我們日常生活的一部分。在這段影片中，讓我們一起複習預防新冠病毒的五個貼士。'),
    ('listitem', '1. Take your temperature daily; see a doctor if necessary.', '1. 每天測量體溫；如有必要請就醫。'),
    ('listitem', '2. Wear a mask; change it when necessary.', '2. 戴口罩；必要時更換。'),
    ('listitem', '3. Wash your hands often; avoid touching your face.', '3. 勤洗手；避免觸摸臉部。'),
    ('listitem', '4. Maintain social distance to prevent transmission.', '4. 保持社交距離以防止傳播。'),
    ('listitem', '5. Disinfect your environment; maintain good ventilation.', '5. 對環境進行消毒；保持良好的通風。'),
    ('paragraph',
     'The five prevention tips can help detect symptoms early and reduce the risk of transmission. To prevent COVID, everyone is important. Let’s all do our part to protect each other’s health.',
     '這五個預防貼士可以幫助及早發現症狀並減少傳播風險。為了預防新冠病毒，每個人都很重要。讓我們都盡自己的一份力量來保護彼此的健康。')
]


# ================= 4. ENGLISH CULTURE DATA =================
english_culture_content = [
    ('section', 'Unit Introduction', '單元導言'),
    ('paragraph',
     'This unit has two sections. First, I would like to introduce a ‘graded reader’ to you, which is composed of short stories about English culture. Then, we want to learn about English / British culture in more depth.',
     '本單元有兩個部分。首先，我想向您介紹一種「分級讀物」，它由關於英國文化的短篇故事組成。然後，我們想更深入地了解英國/不列顛文化。'),
    ('paragraph',
     '1. Some people would argue that British food is terrible, but I couldn’t disagree more. You should definitely try the traditional pies, pudding, fish & chips, bangers & mash, Sunday roast, and English breakfast, except the Christmas pudding.',
     '1. 有些人會認為英國的食物很難吃，但我完全不同意。你絕對應該嘗試傳統的派、布丁、炸魚薯條、香腸土豆泥、週日烤肉和英式早餐，除了聖誕布丁。'),
    ('paragraph',
     '2. The British have the habit of queuing and it is considered taboo that someone jumps the queue, so make sure to wait for your turn.',
     '2. 英國人有排隊的習慣，插隊被視為禁忌，所以請務必耐心等待輪到你。'),
     
    ('section', 'What are Graded Readers?', '什麼是分級讀物？'),
    ('paragraph',
     'In the previous units, we have learned about extensive reading, speed and level of reading, and material choosing, such as picture books and young adult novels for language learning. In this unit, the last type of material that I would like to encourage you to read in this course is ‘graded readers’.',
     '在先前的單元中，我們學習了泛讀、閱讀速度和水準，以及語言學習的材料選擇（例如繪本和青少年小說）。在本單元中，我希望鼓勵您在此課程中閱讀的最後一種材料類型是「分級讀物（graded readers）」。'),
    ('paragraph',
     'We now know that extensive reading aims to ask the learners to read in large quantities at the learner’s level. We mentioned that ideally there should be only around two unfamiliar words out of every 100 running words. In practice, learners neither know their own vocabulary size nor have the ability to judge the level of text difficulty if they are not advanced learners. To respond to these issues, many publishers have created ‘graded readers’, which are specifically written to be at the right level of vocabulary and at the appropriate length for learners. Usually, graded readers are produced in series. According to The Extensive Reading Foundation:',
     '我們現在知道，泛讀旨在要求學習者在適合其水準的基礎上進行大量閱讀。我們提到，理想情況下，每100個連續字詞中應該只有大約兩個陌生字詞。在實踐中，除非是高階學習者，否則學習者既不知道自己的詞彙量，也沒有能力判斷文本難易度。為了應對這些問題，許多出版社創建了「分級讀物」，這些讀物是專門為學習者量身定做的合適詞彙水準和長度。通常，分級讀物是成系列出版的。根據泛讀基金會的說法：'),
    ('paragraph',
     '“Graded Readers are books of various genres that are specially created for learners of foreign languages. They may be simplified versions of existing works, original stories or books that are factual in nature. They are ‘graded’ in the sense that the syntax and lexis are controlled in order to make the content accessible to learners of the language. Publishers normally issue reader series with 4-6 different reading levels to suit a range of skill levels and allow progress over time. The Extensive Reading Foundation also refers to graded readers as Language Learner Literature (LLL), indicating that they comprise a valid, ‘authentic’ type of literature aimed at a specific readership.”',
     '「分級讀物是專門為外語學習者創作的各種流派的書籍。它們可能是現有作品的簡化版本、原創故事或紀實性質的書籍。它們之所以被稱為『分級』，是因為其句法和詞彙都受到了控制，以便該語言的學習者能夠理解其內容。出版社通常會發行具有 4 到 6 個不同閱讀水準的讀物系列，以適應不同的技能水準並允許隨著時間的推移取得進步。泛讀基金會也將分級讀物稱為語言學習者文學（LLL），表明它們構成了一種針對特定讀者群的有效且『真實』的文學類型。」'),
    ('paragraph',
     'Most major publishers have at least one and often several series of graded readers (Nation, 2013). My personal favorite in teaching is Cambridge English Readers which are original stories written specifically at different vocabulary levels and so far there is no Chinese translation available yet. Nation (2013) also used Cambridge English Reader as an example to introduce the idea using graded readers in extensive reading programs.',
     '大多數主要出版社都至少有一個、通常是幾套分級讀物系列（Nation, 2013）。我個人在教學中最喜歡的是《劍橋英語讀物》（Cambridge English Readers），這些是專門為不同詞彙水準編寫的原創故事，目前還沒有中文譯本。Nation（2013）也以劍橋英語讀物為例，介紹了在泛讀計畫中使用分級讀物的概念。'),
     
    ('pagebreak',),
    
    ('subsection', 'Cambridge English Readers Level Equivalence (Nation, 2013)', '分級讀物水準對照表'),
    ('listitem', 'Level 1: 400 unique words | Approx. 4,000 words length | Example: Bad love, Blood diamonds', '第一級：400個不同字詞 | 約 4,000 字長度 | 範例：《糟糕的愛》、《血鑽石》'),
    ('listitem', 'Level 2: 800 unique words | Approx. 10,000 words length | Example: Apollo’s gold, Jojo’s story', '第二級：800個不同字詞 | 約 10,000 字長度 | 範例：《阿波羅的金子》、《喬喬的故事》'),
    ('listitem', 'Level 3: 1,300 unique words | Approx. 15,000 words length | Example: The Beast, Two lives', '第三級：1,300個不同字詞 | 約 15,000 字長度 | 範例：《野獸》、《兩個生命》'),
    ('listitem', 'Level 4: 1,900 unique words | Approx. 20,000 words length | Example: Berlin express, Staying together', '第四級：1,900個不同字詞 | 約 20,000 字長度 | 範例：《柏林快車》、《在一起》'),
    ('listitem', 'Level 5: 2,800 unique words | Approx. 25,000 words length | Example: All I want, Tangled web', '第五級：2,800個不同字詞 | 約 25,000 字長度 | 範例：《我所想要的一切》、《錯綜複雜的網》'),
    ('listitem', 'Level 6: 3,800 unique words | Approx. 30,000 words length | Example: A love for life, Murder maker', '第六級：3,800個不同字詞 | 約 30,000 字長度 | 範例：《一生的愛》、《謀殺製造者》'),
    
    ('paragraph',
     'For example, in level 3 of the series, all of the books are well-designed and written within the vocabulary of 1,300 words, so if you are around this level, you will be able to read the books at this level without difficulty. Therefore, a level-1 or level-2 learner will find it hard to read a level-3 book due to the unfamiliar words in the texts. These books are designed to be quite long, because this gives learners opportunities to practice reading at the appropriate level for them. While the readers read these interesting, exciting, or at least new stories, they recall some words they have learned before, retrieve words from memory, and see different forms of the same word in a variety of sentences or contexts.',
     '例如，在該系列的第三級中，所有的書都設計得很好，並且是在 1,300 個單字的詞彙量範圍內編寫的，因此如果您大約處於這個水準，您將能夠毫無困難地閱讀這個水準的書籍。因此，由於文本中存在不熟悉的字詞，第一級或第二級的學習者會發現很難閱讀第三級的書。這些書設計得相當長，因為這給了學習者在適合他們的水準上練習閱讀的機會。當讀者閱讀這些有趣、刺激或至少是新的故事時，他們會回想起以前學過的一些單字，從記憶中檢索單字，並在各種句子或語境中看到同一個單字的不同形式。'),
    ('paragraph',
     'The book which I think suits this course purpose is from Cambridge English Readers 6. The book title is ‘Frozen Pizza and other slices of life’. The author is Antoinette Moses and it introduces life in modern England through eight stories, which is the eight ‘slices of life’ following the metaphor of Frozen Pizza in the title. These eight short stories covered themes of food, media, immigration, student life, football hooliganism, inner-city problems, leisure activities and the country side of life in England. While you read the stories, you can also learn about life in modern England. People usually have certain stereotypes of the English people or culture, for instance, English people are indifferent and have a strange sense of humor. However, I find them friendly and warm. We all know that stereotypes could be wrong because stereotypes are often over-simplified or over-generalized images towards a certain group of people or issue. It is not a terrible crime to have stereotypes, but, at least, what we can do is try to get to know and understand them first, then make the judgment by ourselves as a way to show our respect towards other cultures.',
     '我認為適合本課程目的的書是劍橋英語讀物第六級的。書名是《冷凍披薩與人生的其他切片》。作者是安托瓦內特·摩西（Antoinette Moses），它通過八個故事介紹了現代英格蘭的生活，這八個故事是繼書名中冷凍披薩的比喻之後的八個「人生切片」。這八個短篇故事涵蓋了英國生活的食物、媒體、移民、學生生活、足球流氓、市中心問題、休閒活動和鄉村等主題。在閱讀故事的同時，您還可以了解現代英格蘭的生活。人們通常對英國人或英國文化有一些刻板印象，例如，英國人冷漠且有著奇怪的幽默感。然而，我發現他們很友好和熱情。我們都知道刻板印象可能是錯誤的，因為刻板印象往往是對特定人群或問題過於簡化或過於籠統的印象。有刻板印象並不是可怕的罪行，但至少我們可以做的是嘗試先去認識和理解他們，然後自己做出判斷，以展示我們對其他文化的尊重。'),
     
    ('section', 'Stereotypes of English Culture', '英國文化的刻板印象'),
    ('subsection', '1. British people love talking about weather', '1. 英國人熱愛談論天氣'),
    ('paragraph',
     'It is possibly the most spoken of the topic in the country. On the one hand, there is never a dull moment when it comes to the British weather since it is changeable and famously unpredictable. On the other hand, weather talk is an icebreaker, and it is used to fill awkward silences or divert the conversation away from uncomfortable topics, such as salary or age.',
     '這可能是該國被談論最多的話題。一方面，就英國天氣而言，從來沒有無聊的時刻，因為它多變且以不可預測而聞名。另一方面，天氣談話是打破僵局的工具，它被用來填補尷尬的沉默，或將對話從令人不適的話題（如薪水或年齡）中轉移開。'),
    ('paragraph',
     'According to social anthropologist Kate Fox, there are certain unwritten rules that the British follow when having these weather-related conversations. Firstly, the topic will always be introduced as a form of question, even if only in the intonation (e.g., “Raining again?”). Secondly, the person answering must agree. “Failing to agree is quite a serious breach of etiquette. Or at least if you disagree, you have to express it in terms of a sort of personal foible”. “If someone says: ‘Cold, isn’t it?’ and you say: ‘Well actually, no,’ the person would be a bit taken aback, and feel that that was a discourteous thing to say.”',
     '根據社會人類學家凱特·福克斯（Kate Fox）的說法，英國人在進行這些與天氣相關的對話時遵循某些不成文的規則。首先，這個話題總是會以問題的形式引入，即使只是在語調上（例如，「又下雨了？」）。其次，回答的人必須同意。「不表示同意是相當嚴重的失禮行為。或者至少如果你不同意，你也必須將其表達為一種個人怪癖。」「如果有人說：『很冷，不是嗎？』而你說：『嗯，其實沒有，』那個人會有點吃驚，並覺得那是一句粗魯無禮的話。」'),
     
    ('subsection', '2. British people always complain but also are polite', '2. 英國人總是抱怨，但也很禮貌'),
    ('paragraph',
     'British people love grumbling to each other about everything from neighbours to politicians, from energy bills to noisy parties and from the weather being too cold to the weather being too hot, but they also say “sorry”, “please” and “thank you” a lot. However, there are equally as many positive British people as there are negative ones, it completely depends on the person you talk to.',
     '英國人喜歡互相抱怨一切，從鄰居到政治家，從電費單到吵鬧的派對，從天氣太冷到天氣太熱，但他們也經常說「對不起」、「請」和「謝謝」。然而，積極的英國人與消極的英國人一樣多，這完全取決於你與之交談的人。'),
    ('paragraph',
     'Example: British people in a restaurant. When the waitress comes round to do her check and says: “how is everything?” and they respond with: “oh it’s lovely thank you” after secretly complaining for the last 10 minutes that the food is cold.',
     '範例：餐館裡的英國人。當女服務員過來詢問「一切都好嗎？」時，他們回答：「噢，非常好，謝謝你」，而在此之前的10分鐘裡，他們一直在私下抱怨食物是冷冰冰的。'),
     
    ('subsection', '3. British people have a stiff upper lip', '3. 英國人保持堅忍克己 (Stiff Upper Lip)'),
    ('paragraph',
     'This term comes from the idea that an emotional or upset person has a quivering upper lip, so a stiff upper lip refers to the concept that the British are quite reserved and keep their emotions and feelings to themselves. This stems from the Victorian period, when showing your emotions was indeed considered inappropriate to show their self-restrain. Whilst the times are changing and a number of newspaper articles in recent years have argued that the British stiff upper lip no more, for instance, the public outpouring of emotion at the death of Diana, Princess of Wales.',
     '這個詞來自於這樣一個觀點：一個情緒激動或沮喪的人會有顫抖的上唇，因此「硬上唇（stiff upper lip）」指的是英國人相當保守，將自己的情緒和感受隱藏起來的概念。這源於維多利亞時代，當時展示你的情緒確實被認為是不合適的，應該展示自我克制。雖然時代在變，近年來一些報紙文章也爭辯說英國人的堅忍克己已不復存在，例如威爾斯王妃黛安娜去世時公眾情緒的宣洩。'),
     
    ('subsection', '4. British people love drinking tea', '4. 英國人熱愛喝茶'),
    ('paragraph',
     'Tea is definitely a key part of British culture. From early morning to late at night, the kettle is on for a brew in many households across the country, and making tea for other people is the ultimate form of British hospitality. Milk in tea plays an important role while some taking their tea with sugar or lemon instead; however, more than the taste, milk in tea also gives off cues to Britain’s social class system.',
     '茶絕對是英國文化的核心部分。從清晨到深夜，全國許多家庭都在燒水泡茶，為他人沏茶是英式熱情好客的終極形式。茶中的牛奶起著重要作用，而有些人則用糖或檸檬代替；然而，除了口味之外，茶中的牛奶也發出了英國社會階級系統的信號。'),
    ('paragraph',
     'According to Fox, tea strength wanes as the social class gets nearer to the aristocracy. The strongest brews of black tea are drunk by the working class, who are then required to temper the bitter taste with plenty of milk and sugar to make “builder’s tea.” “Taking sugar in your tea is regarded by many as an infallible lower-class indicator”.',
     '根據福克斯的說法，隨著社會階級接近貴族，茶的濃度會減弱。最強烈的黑茶是由工人階級喝的，然後他們需要加入大量的牛奶和糖來緩和苦味，製成「建築工人之茶（builder’s tea）」。許多人將「在茶中加糖」視為工人階級無可爭議的指標。'),
     
    ('section', 'Extended Content', '延伸內容'),
    ('paragraph',
     'YouTube Video: British Stereotypes. In this video, some of the British stereotypes were asked to Britons, and they talked about their point of view. Issues covered: politeness, humour, tea, lack of emotion, teeth, food, monolingualism and anti-social behavior abroad. (video length: 13 minutes 25 seconds)',
     'YouTube 影片《英國人的刻板印象》：在這段影片中，一些關於英國人的刻板印象被向英國人提出，他們談論了自己的觀點。涵蓋的問題包括：禮貌、幽默、茶、缺乏情感、牙齒、食物、單一語言和在國外的反社會行為。')
]


# ================= 5. SURVEILLANCE DATA =================
surveillance_content = [
    ('section', 'Unit Introduction', '單元導言'),
    ('paragraph',
     'In this unit, we are going to learn about the second type of learning material that I recommend to learners frequently, which is the young adult novel. Then, we will look at a world-famous awarded young adult novel “The Giver”, followed by a short briefing on some utopian literary works.',
     '在本單元中，我們將學習我經常向學習者推薦的第二種學習材料，即青少年小說（young adult novel）。然後，我們將看看一部世界著名的獲獎青少年小說《記憶傳授人》（The Giver），隨後對一些烏托邦文學作品進行簡要介紹。'),
     
    ('section', 'Lead-in Dialogue', '導入對話'),
    ('paragraph',
     'Jack: Did you watch the news today? So many crimes everywhere… It’s like everyone has gone mad! What a horrible world we all live in!\nSam: Don’t you love the world now? What’s your ideal world like?\nJack: I want a world that people feel safe, where there is no war, and all men are equal without racism.\nSam: A utopia, you mean.\nJack: That would be nice, wouldn’t it?\nSam: Can’t agree more!',
     '傑克：你今天看新聞了嗎？到處都有那麼多犯罪……簡直每個人都瘋了！我們生活的世界真是太可怕了！\n山姆：你現在不愛這個世界了嗎？你理想中的世界是什麼樣的？\n傑克：我想要一個讓人們感到安全、沒有戰爭、人人平等且沒有種族主義的世界。\n山姆：你的意思是，一個烏托邦。\n傑克：那會很美好，不是嗎？\n山姆：再同意不過了！'),
     
    ('section', 'Utopia & Dystopia', '烏托邦與反烏托邦'),
    ('paragraph',
     'Definition of Utopia (from Cambridge Online Dictionary): The idea of a perfect society in which everyone works well with each other and is happy.',
     '烏托邦的定義（來自劍橋線上詞典）：一個每個人都與其他人相處融洽且幸福的完美社會的構想（烏托邦；理想中的完美世界）。'),
    ('paragraph',
     'From the above definition, we know that there is not a utopia yet, even though some Scandinavian nations were ranked at the top in the World Happiness Report, they are not perfect or ideal. So far, utopia is only “an imaginary (non-existent) community or society that possesses highly desirable or nearly perfect qualities for its members.” The word was coined by Sir Thomas More in his work Utopia in 1516. The word utopia was composed of the οὐ (“not”) and τόπος (“place”) in Greek, and it meant any non-existent society in More’s original work. There is a word with similar spelling and meaning, which is eutopia, meaning “good place”, from Greek: εὖ (“good” or “well”) and τόπος (“place”). The pronunciation of ‘utopia’ and ‘eutopia’ are identical, but the difference in meaning is subtle because eutopia would fit the modern idea of utopia better than utopia.',
     '從上述定義中，我們知道目前還沒有烏托邦，儘管一些斯堪地那維亞國家在《世界幸福報告》中名列前茅，但它們並不完美或理想。到目前為止，烏托邦僅僅是「一個虛構的（不存在的）社區或社會，為其成員擁有高度令人嚮往或近乎完美的品質。」這個詞是托馬斯·摩爾爵士在1516年的著作《烏托邦》中創造的。烏托邦一詞由希臘語中的 οὐ（「不」）和 τόπος（「地方」）組成，在摩爾的原著中意為任何不存在的社會。有一個拼寫和含義相似的詞，即 eutopia，意為「美好的地方」，來自希臘語中的 εὖ（「好」或「好地」）和 τόπος（「地方」）。「utopia」 and 「eutopia」的發音是相同的，但含義上的差別很微妙，因為 eutopia 比 utopia 更符合現代的烏托邦觀點。'),
    ('paragraph',
     'Would you like to live in a society where every meal is delivered to your door, a job assigned to you based on your observed specialty, with no climate change while everyone is polite and respectful? This sounds a little like utopia, doesn’t it? Maybe someday this will happen, but so far, we have only reached the first one ‘meal delivery to the doorstep’ after the Covid pandemic. Nevertheless, utopian societies exist in many books. The world I have described in the beginning of this paragraph can be found in the novel ‘The Giver’ by Lois Lowry.',
     '你想生活在一個每頓飯都送到你門口，根據你所觀察到的特長為你分配工作，沒有氣候變化，而且每個人都禮貌和尊重他人的社會中嗎？這聽起來有點像烏托邦，不是嗎？也許有一天這會實現，但到目前為止，在新冠疫情大流行之後，我們只實現了第一個「送餐上門」。然而，烏托邦社會存在於許多書中。我所描述的世界可以在洛伊絲·洛利（Lois Lowry）的小說《記憶傳授人》（The Giver）中找到。'),
     
    ('pagebreak',),
    
    ('section', 'The Giver by Lois Lowry', '《記憶傳授人》介紹'),
    ('paragraph',
     'The Giver was written as young adult novel, as the target readers are 12- to 18-year-old teenagers. Novels are different from stories for they include more details so the readers can contemplate on why, relate to the characters, emphasize, and find causal relationships. Young adult novels differ from novels for they have clear central themes, which is good for language learning. From these themes, we can easily expand vocabulary from the theme and put them into listening, writing or speaking exercises immediately. The second advantage of using young adult novel for English learning is that they tend to be shorter than novels written for adults. Also, classic or awarded young adult novels are often adopted into movies, which we can enjoy after we read for review. ‘The Giver’ has a movie version too.',
     '《記憶傳授人》是作為青少年小說撰寫的，因為目標讀者是 12 至 18 歲的青少年。小說不同於短篇故事，因為它們包含更多細節，使讀者能夠思考原因、與角色產生共鳴、產生同理心並尋找因果關係。青少年小說不同於普通小說，因為它們有明確的中心主題，這對語言學習很有好處。從這些主題中，我們可以輕鬆地擴展主題詞彙，並立即將其放入聽力、寫作或口說練習中。使用青少年小說學習英語的第二個好處是，它們往往比為成年人寫的小說要短。此外，經典或獲獎的青少年小說經常被改編成電影，我們可以在閱讀後觀看以進行複習。《記憶傳授人》也有電影版本。'),
    ('paragraph',
     'From the summary of the back cover of the book, we see the main character ‘Jonas’ lives in a perfect world, a utopia. In Jonas’s world, everything is arranged, decided and regulated though; the citizens of the ‘community’ are carefully monitored (watched) by the ‘Committee of Elders’ and everyone must obey the rules, or they will be warned and punished. Language must be precise, for instance, the concept of ‘love’ becomes too abstract and vague, so the word ‘love’ is banned. Everything you say or do is watched 24/7. Would you like to live in a world like this?',
     '從書的封底簡介中，我們看到主角「喬納斯」生活在一個完美的世界，一個烏托邦。然而，在喬納斯的世界裡，一切都是被安排、決定和監管的；「長老委員會」仔細監控（觀看）「社區」的公民，每個人都必須遵守規則，否則他們將受到警告和懲罰。語言必須精確，例如，「愛」的概念變得太抽象和模糊，所以「愛」這個詞被禁止了。你說的或做的每一件事都受到24小時全天候的監控。你想生活在這樣的世界裡嗎？'),
     
    ('section', 'Surveillance Society', '監視社會'),
    ('paragraph',
     'Definition of Surveillance (from Cambridge Online Dictionary): The careful watching of a person or place, especially by the police or army, because of a crime that has happened or is expected.',
     '監視（Surveillance）的定義：對某人或某個地方的仔細觀察，特別是由警察或軍隊進行，因為發生了或預期會發生犯罪。'),
    ('paragraph',
     'You might not be aware, but our society nowadays is a surveillance society. Have you thought about how many times you were on camera each day? I can give you some hints. Think about the cameras on the streets, at the crossroads, at the entrances and exits of buildings, dash cams on cars passing you on the roads, on the ATMs while you withdrawing cash, cameras installed by grocery shops, not to mention the accidental shot of someone taking a selfie next to you. We now leave our digital prints everywhere, online shopping, credit card purchase, cell phone records and details, financial investments, leisure music data and so on. We can be under surveillance from our whereabout, financial dealings to our personal lifestyle choices very easily.',
     '你可能沒有意識到，但我們如今的社會是一個監視社會。你是否想過你每天有多少次出現在鏡頭前？我可以給你一些提示。想想街上的攝像頭、十字路口、建築物的出入口、道路上擦身而過的車輛上的行車記錄器、取款時自動取款機上的攝像頭、雜貨店安裝的攝像頭，更不用說有人在你身旁自拍時意外拍到你的畫面。我們現在到處都留下數位足跡：線上購物、信用卡消費、手機記錄和詳細信息、金融投資、休閒音樂數據等。我們可以非常容易地在行蹤、財務往來以及個人生活方式選擇方面受到監視。'),
    ('paragraph',
     'Some people do not mind being watched because they think surveillance can deter crimes and they have nothing to hide; however, others might feel uncomfortable being watched as too much security threatens people’s freedom. With the advancement of biometric facial recognition, police can find a person very easily, possibly within hours or minutes. So, let us think about it for a while. Are you willing to exchange your freedom for security? Of course, this is up to you. However, in most of the utopian novels, the main characters are usually anti-utopian; they choose to fight against the perfect system to maintain more humanity. For instance, Jonas in The Giver left the community. So, a perfect world is not everyone’s choice. I will not spoil your fun of reading, but one thing I can tell you is that The Giver has three sequels, Gathering Blue, Messenger, and Son.',
     '有些人不介意被監視，因為他們認為監視可以威懾犯罪，而且他們沒有什麼可隱隱瞞的；然而，其他人可能會因為被監視而感到不舒服，因為過多的安全威脅到了人們的自由。隨著生物識別面部識別技術的進步，警方可以非常容易地找到一個人，可能在幾小時或幾分鐘內。所以，讓我們思考一下。你願意用自由換取安全嗎？當然，這取決於你。然而，在大多數烏托邦小說中，主角通常是反烏托邦的；他們選擇與完美的系統抗爭以維護更多的人性。例如，《記憶傳授人》中的喬納斯離開了社區。所以，一個完美的世界並不是每個人的選擇。我不會劇透你的閱讀樂趣，但有一件事我可以告訴你，《記憶傳授人》有三部續集：《藍色尋覓》（Gathering Blue）、《森林信使》（Messenger）和《兒子》（Son）。'),
    ('paragraph',
     'In a lot of the utopian novels, the storyline is actually dystopian, meaning ‘bad place’, which is the opposite of a utopia. Somehow a superficial perfect world turns into a cruel world because of the surveillance and centralization of power leading to social hierarchy, sameness and loss of freewill and choice. Another masterpiece, even more famous than The Giver, is George Orwell’s science fiction novel 1984, which was published in 1949. The story took place in 1984, which was a future for Orwell when he wrote the novel. The story was deep and insightful, but long, really long. Many terms that we are familiar with originate from 1984, such as “The Big Brother Is Watching You”, “doublethink”, “Thought Police”, “thoughtcrime”, “Newspeak”, and “2+2=5”. Together with Orwell’s 1984, Huxley’s Brave New World and Zamyatin’s We are called Dystopian trilogy. Since 1984 is a serious classic and masterpiece, the language is not easy to read. You might want to start with the Chinese translated book to know the story first. An international reality television franchise Big Brother uses allusion from 1984.',
     '在許多烏托邦小說中，情節實際上是反烏托邦（dystopian）的，意為「糟糕的地方」，這是烏托邦的反義詞。由於監視和權力集中導致社會階級、千篇一律以及失去自由意志和選擇，表面上完美的世界不知何故變成了殘酷的世界。另一部比《記憶傳授人》更著名的傑作是喬治·歐威爾於1949年出版的科幻小說《1984》。故事發生在1984年，這對歐威爾寫作該小說時來說是未來。這個故事深刻而富有洞察力，但很長，真的很長。許多我們熟悉的術語都源自《1984》，例如「老大哥在看著你」、「雙重思想」、「思想警察」、「思想犯罪」、「新話」和「2+2=5」。與歐威爾的《1984》、赫胥黎的《美麗新世界》和扎米亞京的《我們》並稱為反烏托邦三部曲。由於《1984》是一部嚴肅的經典和傑作，其語言不易閱讀。您可能想先從中文譯本開始以了解故事。'),
     
    ('section', 'Related Utopian/Dystopian Works', '相關烏托邦/反烏托邦作品'),
    ('listitem', 'Graded reader: Cambridge English Reader "In the House" (level 4)', '分級讀物：劍橋英語讀物《屋子裡》（第四級）'),
    ('listitem', 'Novel: Fahrenheit 451 by Ray Bradbury', '小說：雷·布萊伯利的《華氏451度》'),
    ('listitem', 'Film 1: The Truman Show (1998)', '電影 1：《楚門的世界》（1998年）'),
    ('listitem', 'Film 2: Minority Report (2002)', '電影 2：《關鍵報告》（2002年）'),
    ('listitem', 'Film 3: The Island (2005)', '電影 3：《絕地再生》（2005年）'),
    ('listitem', 'Film 4: The Hunger Games (2012)', '電影 4：《飢餓遊戲》（2012年）'),
    ('listitem', 'TV Series: The Handmaid’s Tale (2017)', '電視劇：《使女的故事》（2017年）'),
    ('listitem', 'Other Languages: "Folding Beijing" by Hao Jingfang', '其他語言：郝景芳的《北京折疊》（雨果獎得獎作品）')
]

if __name__ == "__main__":
    # Generate the 5 detailed bilingual PDFs
    build_pdf("modern_arts_bilingual.pdf", "Unit: Modern Arts", modern_arts_content)
    build_pdf("creativity_bilingual.pdf", "Unit: Creativity", creativity_content)
    build_pdf("vaccination_bilingual.pdf", "Unit: Vaccination", vaccination_content)
    build_pdf("english_culture_bilingual.pdf", "Unit: English Culture: Graded Readers & Stereotypes", english_culture_content)
    build_pdf("surveillance_bilingual.pdf", "Unit: Surveillance: The Giver", surveillance_content)
    print("Done generating all 5 detailed bilingual PDFs.")
