from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from random import randint
import os
import shutil

os.chdir(os.path.dirname(__file__))  # 修正工作目录

# def getLength(string:str)->int:
#     '''返回图片上文字的长度，汉字计3，其他记1'''
#     res = 0
#     for i in string:
#         if '\u4e00' <= i <= '\u9fa5':
#             res+=3
#         else:
#             res+=1
#     return res
# 获取tips
with open("tips.txt","r",encoding="utf-8") as f:
    tips = f.readlines()
text = tips[randint(0,len(tips)-1)]
if len(text)>50:
    text = text[:49]+"\n"+text[49:]
    
# text = "英国皇家学会恩情课文《牛顿爷爷用平面几何证明万有引力定律》"  #调试
# 处理图片

font = ImageFont.truetype("msyh.ttc",24)

imagefile = "Banner.png"
tp = Image.open(imagefile)

draw = ImageDraw.Draw(tp)
draw.text((158,600),text,(255,255,255),font=font)

tp.save("res.png")

# 替换文件
bannerDir = os.path.join(os.getenv("AppData"),r"Seewo\EasiNote5\Resources\Banner\Banner.png")
if os.path.exists(bannerDir):
    os.remove(bannerDir)
shutil.move("res.png",bannerDir)