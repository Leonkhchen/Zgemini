
# Try to decode the summary of S2: "閰Ｚ隢摮鈭"
# Hex characters might help
import binascii

def try_fix(s):
    print(f"Original: {s}")
    # Many Chinese characters in Big5 start with 0xA1-0xF9
    # If they are treated as Unicode directly or via some other path...
    try:
        # Try to see if it's UTF-8 that should have been Big5
        # but Python's print/shell might have already mangled it.
        pass
    except: pass

# Based on the user's feedback, the first one was "幼兒園體能活動 (新竹市)"
# Let's see if we can find those words in the second one.
# s2_sum: 閰Ｚ隢摮鈭
# The description was "撣嗅蝳桃憟賭"
# Let's try Big5 encoding of "幼兒園"
test_str = "幼兒園"
print(f"'幼兒園' Big5: {binascii.hexlify(test_str.encode('big5'))}")
print(f"'幼兒園' UTF-8: {binascii.hexlify(test_str.encode('utf-8'))}")

# If we take Big5 bytes and decode as something else?
b_big5 = test_str.encode('big5')
print(f"Big5 decoded as CP1252: {b_big5.decode('cp1252', errors='ignore')}")
print(f"Big5 decoded as Latin-1: {b_big5.decode('latin-1', errors='ignore')}")

# "幼" in Big5 is A4 74. In Unicode, U+A474 is "ꑴ" (Yi syllable)
# "兒" in Big5 is A4 a4. In Unicode, U+A4A4 is "꒤"
# "園" in Big5 is B6 eb. In Unicode, U+B6EB is "뛫"

# Wait, the summary was: 斗陸鞈
# Repr: '\uf074\uf2ea'
# \uf074 is a private use character.

# Let's look at the second one: S2 Des Repr: '\uf55d單\uf3e7陪'
# Description: "撣嗅蝳桃憟賭"
# "撣" Big5 is BD AD. U+BDAD is "붭"
# "嗅" Big5 is B3 CA. U+B3CA is "돊"
# "" Big5 is 8F 5D. 
# "蝳" Big5 is C1 B3. U+C1B3 is "솳"

# Actually, if I just look at the context:
# 4/26 13:40 Location: "瘞貊儔踹-蝡孵蝳摨眺憟賣蝯末蝺"
# This looks like "新竹縣-竹北市..." (Hsinchu County - Zhubei City...)
# The summary of S2 starts with "" (Big5 A4 4A?)
# "諮" Big5 is BDB2.
# "詢" Big5 is B3D2.
# "歐德" Big5 is BC EC BC 77.
# "歐德傢俱"

# The user said "幼兒園體能活動 (新竹市) 這件事不對"
# Maybe the event is "親子運動會" or something similar?
