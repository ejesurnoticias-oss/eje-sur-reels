import os
import subprocess
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
PEXELS_KEY = os.environ["PEXELS_API_KEY"]
CATEGORIA = os.environ["CATEGORIA"]
SUBTAG = os.environ["SUBTAG"]
TITULAR = os.environ["TITULAR"]
BAJADA = os.environ["BAJADA"]
BUSQUEDA = os.environ["BUSQUEDA_FOTO"]

os.makedirs("output", exist_ok=True)
os.makedirs("assets", exist_ok=True)

headers = {"Authorization": PEXELS_KEY}
r = requests.get(
    f"https://api.pexels.com/v1/search?query={BUSQUEDA}&orientation=portrait&per_page=1",
    headers=headers,
)
data = r.json()
photo_url = data["photos"][0]["src"]["large2x"]
photo_bytes = requests.get(photo_url).content
with open("assets/photo.jpg", "wb") as f:
    f.write(photo_bytes)

photo = Image.open("assets/photo.jpg").convert("RGB")
pw, ph = photo.size
scale = max(W / pw, H / ph)
new_w, new_h = int(pw * scale) + 1, int(ph * scale) + 1
photo = photo.resize((new_w, new_h), Image.LANCZOS)
left = (new_w - W) // 2
top = int((new_h - H) * 0.3)
photo = photo.crop((left, top, left + W, top + H))
base = photo.convert("RGBA")

fade = Image.new("L", (1, H), 0)
for y in range(H):
    v = 0 if y < H * 0.40 else int(255 * min(1, (y - H * 0.40) / (H * 0.60) * 1.2))
    fade.putpixel((0, y), v)
fade = fade.resize((W, H))
darkfade = Image.new("RGBA", (W, H), (8, 14, 26, 255))
darkfade.putalpha(fade)
base.alpha_composite(darkfade)

draw = ImageDraw.Draw(base)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_word = ImageFont.truetype(FONT, 46)
f_tag = ImageFont.truetype(FONT, 20)
f_cat = ImageFont.truetype(FONT, 30)
f_sub = ImageFont.truetype(FONT, 30)
f_title = ImageFont.truetype(FONT, 54)
f_body = ImageFont.truetype(FONT_R, 32)
f_foot = ImageFont.truetype(FONT, 22)
BLUE, WHITE, GRAY, NAVY = (29, 161, 242), (255, 255, 255), (233, 243, 251), (15, 23, 42)

if os.path.exists("assets/logo.png"):
    logo = Image.open("assets/logo.png").convert("RGBA").resize((90, 90), Image.LANCZOS)
    base.alpha_composite(logo, (60, 60))
    draw.line([(175, 60), (175, 150)], fill=(255, 255, 255, 140), width=3)
    text_x = 195
else:
    text_x = 60

draw.text((text_x, 58), "EJE", font=f_word, fill=WHITE)
draw.text((text_x, 104), "SUR", font=f_word, fill=BLUE)
draw.text((text_x, 158), "UNA MIRADA GLOBAL DESDE EL", font=f_tag, fill=GRAY)
draw.text((text_x, 182), "EJE SUR", font=f_tag, fill=BLUE)

bbox = draw.textbbox((0, 0), CATEGORIA, font=f_cat)
tw = bbox[2] - bbox[0]
x2, x1 = W - 60, W - 60 - (tw + 60)
draw.polygon([(x1 + 20, 60), (x2, 60), (x2, 120), (x1, 120)], fill=BLUE)
draw.text((x1 + 35, 74), CATEGORIA, font=f_cat, fill=WHITE)

cx, y = 65, 1180
bbox3 = draw.textbbox((0, 0), SUBTAG, font=f_sub)
sw = bbox3[2] - bbox3[0]
draw.rectangle([cx, y, cx + sw + 50, y + 56], fill=BLUE)
draw.text((cx + 25, y + 12), SUBTAG, font=f_sub, fill=NAVY)
y += 80

for line in textwrap.wrap(TITULAR, width=22):
    draw.text((cx, y), line.upper(), font=f_title, fill=WHITE)
    y += 68

y += 20
draw.rectangle([cx, y, cx + 90, y + 5], fill=BLUE)
y += 35
for line in textwrap.wrap(BAJADA, width=48):
    draw.text((cx, y), line, font=f_body, fill=GRAY)
    y += 42

draw.text((cx, H - 70), "EJE SUR — POLÍTICA · ECONOMÍA · GEOPOLÍTICA", font=f_foot, fill=(233, 243, 251, 180))

base.convert("RGB").save("assets/frame.jpg", quality=100)

subprocess.run([
    "ffmpeg", "-y", "-loop", "1", "-i", "assets/frame.jpg",
    "-i", "assets/music.mp3",
    "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30",
    "-vf", "scale=1080:1920,format=yuv420p",
    "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
    "-t", "30", "-movflags", "+faststart",
    "output/reel.mp4"
], check=True)

print("Reel generado con éxito")
