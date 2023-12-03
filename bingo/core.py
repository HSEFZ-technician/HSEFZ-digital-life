from PIL import Image, ImageDraw, ImageFont
import random
import club_main.settings

def gen1(name):
  n = 3
  m = 50
  e = 3
  f = 100
  img = Image.new("RGB", (n * f + (n + 1) * e, n * f + (n + 1) * e), (255, 255, 255))
  draw = ImageDraw.Draw(img)
  ap = []
  for i in range(0, n):
    for j in range(0, n):
      d = e * 2 + f - 1
      draw.rectangle([i * (e + f), j * (e + f), i * (e + f) + d, j * (e + f) + d], (0, 0, 0))
      font = ImageFont.truetype(os.path.join(club_main.settings.STATIC_ROOT, 'consola.ttf'), 32)
      d = f - 1
      draw.rectangle([i * (e + f) + e, j * (e + f) + e, i * (e + f) + e + d, j * (e + f) + e + d], (255, 255, 255))
      d = e * 2 + f - 1
      x = random.randint(1, m)
      while (ap.count(x) != 0):
        x = random.randint(1, m)
      word = str(x)
      ap.append(x)
      A, B, C, D = font.getbbox(word)
      xy = (i * (e + f) + (d - C) / 2, j * (e + f) + (d - D) / 2)
      draw.text(xy, word, (0, 0, 0), font)
  img.save(name)

import os
import zipfile

def gen(n):
  s = "bingo"
  with zipfile.ZipFile(os.path.join(club_main.settings.MEDIA_ROOT, s + ".zip"), mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
    for i in range(1, n + 1):
      gen1(os.path.join(club_main.settings.MEDIA_ROOT, "bingo.png"))
      zf.write(os.path.join(club_main.settings.MEDIA_ROOT, "bingo.png"), str(i) + ".png")
      os.remove(os.path.join(club_main.settings.MEDIA_ROOT, "bingo.png"))
  return os.path.join(club_main.settings.MEDIA_ROOT, s + ".zip")
