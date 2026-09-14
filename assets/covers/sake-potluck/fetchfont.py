import base64, json, re, subprocess, urllib.parse, sys

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

TEXT = ("日本酒持ち寄り会好きな一本を持ち寄ってゆるく乾杯、。"
        "20歳以上／飲酒の強要はしませんひとりでの参加も大丈夫です・"
        "純米歓迎飲みくらべSAKEPOTLUCKNIGHT 0123456789")

def grab(family, weight):
    q = urllib.parse.urlencode({"family": f"{family}:wght@{weight}", "text": TEXT})
    css = subprocess.run(["curl","-sS","-m","30","-H",f"User-Agent: {UA}",
                          f"https://fonts.googleapis.com/css2?{q}"],
                         capture_output=True, text=True, check=True).stdout
    m = re.search(r"src:\s*url\((https://[^)]+)\)\s*format\('([a-z2]+)'\)", css)
    if not m:
        print("NO MATCH for", family, weight, css[:300]); sys.exit(1)
    url, fmt = m.group(1), m.group(2)
    data = subprocess.run(["curl","-sS","-m","30","-H",f"User-Agent: {UA}", url],
                          capture_output=True, check=True).stdout
    print(f"{family} {weight}: {fmt} {len(data)} bytes")
    return {"family": family, "weight": weight, "format": fmt,
            "b64": base64.b64encode(data).decode()}

fonts = [grab("Noto Serif JP", 900), grab("Noto Sans JP", 700), grab("Noto Sans JP", 400)]
json.dump(fonts, open("fonts.json","w"))
