
s1 = "斗陸鞈"
s2 = "啁姘擃銝剖飛, 300啁啁姘撣摮詨頝36"

def test_decoding(s):
    print(f"Testing: {s}")
    # Common error: Big5 text interpreted as UTF-8
    try:
        raw = s.encode('utf-8')
        print(f"  UTF-8 to Big5: {raw.decode('big5', errors='ignore')}")
    except: pass
    
    try:
        # Sometimes it's Latin-1 interpreted as UTF-8
        raw = s.encode('latin-1')
        print(f"  Latin-1 to UTF-8: {raw.decode('utf-8', errors='ignore')}")
        print(f"  Latin-1 to Big5: {raw.decode('big5', errors='ignore')}")
    except: pass

print("--- Summary ---")
test_decoding(s1)
print("\n--- Location ---")
test_decoding(s2)
