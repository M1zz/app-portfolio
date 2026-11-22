import os, random, colorsys
from PIL import Image, ImageDraw, ImageFilter
MAC = set()
def dominant(img):
    s = img.convert("RGB").resize((32, 32)); best, score = (120, 90, 255), -1
    for (r, g, b) in s.getdata():
        h, l, sat = colorsys.rgb_to_hls(r/255, g/255, b/255)
        sc = sat * (1 - abs(l - .5) * 2)
        if sc > score: score, best = sc, (r, g, b)
    return best
def icon_layer(path, size, mac):
    ic = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    if ic.getpixel((2, 2))[3] > 200:
        m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, size-1, size-1], radius=int(size*.2237), fill=255)
        ic.putalpha(m)
    return ic
def render(aid, W, H, cx, cy, isz):
    path = f"icons/{aid}.png"; mac = aid in MAC
    col = dominant(Image.open(path))
    bg = Image.new("RGB", (W, H), (10, 10, 14))
    glow = Image.new("RGB", (W, H), (10, 10, 14)); d = ImageDraw.Draw(glow)
    R = int(min(W, H) * .42); d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=tuple(int(c*.5) for c in col))
    bg = glow.filter(ImageFilter.GaussianBlur(R*.6))
    # 금빛 반짝이
    rnd = random.Random(aid); sp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sp)
    for _ in range(140):
        x, y = rnd.randrange(W), rnd.randrange(H); r = rnd.choice([2, 3, 3, 4, 6])
        if abs(x-cx) < isz*.75 and abs(y-cy) < isz*.75: continue
        a = rnd.randrange(60, 200); sd.ellipse([x-r, y-r, x+r, y+r], fill=(255, 205, 110, a))
    bg = Image.alpha_composite(bg.convert("RGBA"), sp.filter(ImageFilter.GaussianBlur(.6)))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle(
        [cx-isz//2, cy-isz//2+30, cx+isz//2, cy+isz//2+30], radius=int(isz*.22), fill=(0, 0, 0, 170))
    bg = Image.alpha_composite(bg, sh.filter(ImageFilter.GaussianBlur(40)))
    ic = icon_layer(path, isz, mac); bg.alpha_composite(ic, (cx-isz//2, cy-isz//2))
    return bg.convert("RGB")
for f in sorted(os.listdir("icons")):
    aid = f[:-4]
    render(aid, 1920, 1080, 1360, 440, 520).save(f"media/{aid}-card.png")
    render(aid, 1080, 1920, 540, 700, 560).save(f"media/{aid}-detail.png")
print("ok")
