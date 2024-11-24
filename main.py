from PIL import ImageFont
from PIL import Image,ImageTk
from PIL import ImageDraw
from PIL import ImageFilter
from PIL import ImageOps
from random import randint
import tkinter as tk
import tkinter.ttk as ttk
import os
import shutil
import json
import time

os.chdir(os.path.dirname(__file__))  # 修正工作目录


with open("tips.txt","r",encoding="utf-8") as f:
    tips = f.readlines()
pool=[]
sp_pool=[]
for i in tips:
    if i.startswith("<date="):
        if i.split(">")[0][6:]==time.strftime("%m.%d", time.localtime()):
            sp_pool.append("".join(i.split(">")[1:]))
    else:
        pool.append(i)
if sp_pool:
    text = sp_pool[randint(0,len(sp_pool)-1)]
else:
    text = pool[randint(0,len(pool)-1)]
if len(text)>50:
    text = text[:49]+"\n"+text[49:]
    
# text = "英国皇家学会恩情课文《牛顿爷爷用平面几何证明万有引力定律》"  #调试
# 处理图片
def stack(background:Image.Image,foreground:Image.Image,x:int=0,y:int=0)->Image.Image:
    '''b叠加在a上'''    
    background.paste(foreground, (x, y), foreground)
    return background


def generate(alpha=120,blur=8,is_mirror=False,temp=False)->Image.Image:
    '''alpha:0-255'''
    font = ImageFont.truetype("msyh.ttc",24)
    if not temp:
        bg_image = Image.open("bg.png").convert('RGBA')
        x = bg_image.size[0]
        y = bg_image.size[1]
        # target:948,556
        target_x = 948
        target_y = 556
        if x<target_x or y<target_y:
            bg_image=bg_image.resize((target_x,target_y))
        elif x==target_x and y==target_y:
            pass
        else:
            if x>target_x*1.2 and y>target_y*1.2:
                times = min(x/target_x,y/target_y)
                x = int(x/times)
                y = int(y/times)
                bg_image=bg_image.resize((x,y))
            bg_image = bg_image.crop(((x-target_x)//2, (y-target_y)//2, (x-target_x)//2+target_x, (y-target_y)//2+target_y))
            
        # 模糊化
        bg_image=bg_image.filter(ImageFilter.GaussianBlur(radius=blur))

        # 水平镜像翻转
        if is_mirror:
            bg_image=ImageOps.mirror(bg_image)
        # 透明化
        # 获取数据列表
        datas = bg_image.getdata()
        
        
        # 创建一个新的透明度映射表
        newData = []
        for item in datas:
            # 若已经是透明的，则不做改变
            if item[0] == 0 and item[1] == 0 and item[2] == 0:
                newData.append((0, 0, 0, 0))
            else:
                # 设置新的透明度
                newData.append((item[0], item[1], item[2], alpha))
        
        # 更新图片数据
        bg_image.putdata(newData)

        # 设置圆角
        pixels = bg_image.load()
        invisables = []
        for row in range(6):
            for i in range((7,5,3,2,1,1)[row]):
                invisables.append((i,row))
                invisables.append((target_x-i-1,row))
                invisables.append((i,target_y-row-1))
                invisables.append((target_x-i-1,target_y-row-1))
        for i in invisables:
            pixels[i[0],i[1]] = (0,0,0,0)

        black ="black.png"
        up = "up.png"
        # 打开背景图片和前景图片
        image_black = Image.open(black).convert('RGBA')
        image_up = Image.open(up).convert('RGBA')
        base_image = stack(stack(image_black,bg_image,124,121),image_up)
        # 不透明化
        datas = base_image.getdata()
        
        # 创建一个新的透明度映射表
        newData = []
        for item in datas:
            # 若已经是透明的，则不做改变
            if item[3]==0:
                newData.append((0, 0, 0, 0))
            else:
                # 设置新的透明度
                newData.append((item[0], item[1], item[2], 255))
        
        # 更新图片数据
        base_image.putdata(newData)
        
        # 保存缓存
        base_image.save("temp.png")
        shutil.copyfile("settings.json","temp_effective")
    else:
        print("temp")
        base_image=Image.open("temp.png").convert("RGBA")
    tp = base_image

    draw = ImageDraw.Draw(tp)
    draw.text((158,600),text,(255,255,255),font=font)

    return tp

if __name__=="__main__":
    if os.path.exists("settings.json"):
        with open("settings.json","r",encoding="utf-8") as f:
            datar = json.load(f)
    else:
        datar = {"alpha":120,"blur":8,"mirror":0}
    is_temp=False
    if os.path.exists("temp_effective"):
        with open("temp_effective","r",encoding="utf-8") as f :
            effective=json.load(f)
        if datar==effective:
            is_temp=True
    img=generate(datar["alpha"],datar["blur"],datar["mirror"],is_temp)
    img.save("res.png")
    # 替换文件
    bannerDir = os.path.join(os.getenv("AppData"),r"Seewo\EasiNote5\Resources\Banner\Banner.png")
    if os.path.exists(bannerDir):
        os.remove(bannerDir)
    shutil.move("res.png",bannerDir)
else:
    win = tk.Tk()
    win.title("BetterEasinoteOpening")
    win.geometry("1400x600")
        # 创建一个Canvas用于显示图片
    canvas = tk.Canvas(win, width=978, height=570, background="black")
    canvas.pack(side="left", padx=0, pady=0)
    def alpha_refresh(a):
        global alpha
        alpha=int(float(a))
        label.config(text="亮度:"+str(alpha))
        if is_auto_pre.get():
            refresh()
    def blur_refresh(a):
        global blur
        blur=int(float(a))
        label1.config(text="模糊度:"+str(blur))
        if is_auto_pre.get():
            refresh()
    def refresh():
        global img,image,alpha,blur
        canvas.delete("all")
        img=generate(alpha,blur,is_mirror.get())
        image = ImageTk.PhotoImage(img)
        canvas.create_image(490, 290, image=image)
    def mirror_refresh():
        if is_auto_pre.get():
            refresh()
    def save():
        with open("settings.json","w",encoding="utf-8") as f:
            f.write(json.dumps({"alpha":alpha,"blur":blur,"mirror":is_mirror.get()}, sort_keys=True, indent=4, separators=(',', ': '),ensure_ascii=False))
    if os.path.exists("settings.json"):
        with open("settings.json","r",encoding="utf-8") as f:
            datar = json.load(f)
    else:
        datar = {"alpha":120,"blur":8,"mirror":0}
    alpha=datar["alpha"]
    blur=datar["blur"]
    label = tk.Label(win,text="亮度:"+str(alpha))
    label.pack()
    scale = ttk.Scale(win, orient=tk.HORIZONTAL, command=alpha_refresh, value=alpha)
    scale['from_'] = 0  # 设定最小值
    scale['to'] = 255   # 设定最大值
    scale.pack()
    label1 = tk.Label(win,text="模糊度:"+str(blur))
    label1.pack()
    scale1 = ttk.Scale(win, orient=tk.HORIZONTAL, command=blur_refresh,value=blur)
    scale1['from_'] = 0  # 设定最小值
    scale1['to'] = 20   # 设定最大值
    scale1.pack()
    is_mirror = tk.IntVar()
    is_mirror.set(datar["mirror"])
    mirror = tk.Checkbutton(win,text="水平翻转",variable=is_mirror,onvalue=1,offvalue=0,command=mirror_refresh)
    mirror.pack()
    preview=tk.Button(win,text="预览",command=refresh)
    preview.pack()
    is_auto_pre = tk.IntVar()
    is_auto_pre.set(1)
    auto_pre = tk.Checkbutton(win,text="自动预览",variable=is_auto_pre,onvalue=1,offvalue=0)
    auto_pre.pack()
    apply=tk.Button(win,text="保存",command=save)
    apply.pack()
    refresh()
    win.mainloop()

