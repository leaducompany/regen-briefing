import sys
from PIL import Image, ImageDraw, ImageFont
S=sys.argv[1]; F=S+'/fonts/'
K=2; W,H=1080*K,1350*K
BG=(25,26,20); WH=(236,233,226); MINT=(195,220,207); GR=(150,145,138); DIM=(90,88,82); QC=(79,119,112)
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
def f(n,s): return ImageFont.truetype(F+'Pretendard-'+n+'.otf',s*K)
def ctext(y,t,font,fill): d.text((W//2,y*K),t,font=font,fill=fill,anchor='mm')
# header from template
hdr=Image.open(S+'/efpe_zip/dove_efpe_07_low_and_slow.png').convert('RGB').crop((0,70,1080,170)).resize((1080*K,100*K),Image.LANCZOS)
im.paste(hdr,(0,70*K))
ctext(229,'Q. 에페는 어떤 약인가요?',f('Medium',26),QC)
# title with mint accent
tf=f('Regular',64)
ctext(312,'주 1회,',tf,WH)
y=394; a='펜 형태'; b=' 주사로 맞습니다.'
wa=d.textlength(a,font=tf); wb=d.textlength(b,font=tf); x0=(W-(wa+wb))/2
d.text((x0,y*K),a,font=tf,fill=MINT,anchor='lm'); d.text((x0+wa,y*K),b,font=tf,fill=WH,anchor='lm')
# pen illustration (line art), centered at y=590
lw=2*K; cy=600*K
def rr(x1,y1,x2,y2,r,**kw): d.rounded_rectangle((x1*K,y1*K,x2*K,y2*K),radius=r*K,width=lw,**kw)
# cap (mint filled)
rr(152,555,340,645,26,fill=MINT,outline=MINT)
# needle-shield tip
rr(126,580,152,620,8,outline=WH)
# body
rr(346,548,860,652,30,outline=WH)
# window
rr(470,580,610,620,12,outline=MINT)
for i in range(5): d.line(((490+i*25)*K,588*K,(490+i*25)*K,612*K),fill=DIM,width=K)
# grip lines
for xx in (680,700,720): d.line((xx*K,560*K,xx*K,640*K),fill=DIM,width=K)
# end button
rr(860,565,930,635,18,outline=WH)
rr(930,582,955,618,8,fill=MINT,outline=MINT)
# caption under pen
ctext(700,'일러스트 · 실제 제품과 모양이 다를 수 있습니다',f('Regular',18),DIM)
# three points
items=[('01','매주 정한 요일에','한 번'),('02','낮은 용량부터','단계적으로'),('03','첫 주사는','진료 때 함께')]
cx=[230,540,850]
for (n,l1,l2),x in zip(items,cx):
    d.ellipse(((x-56)*K,(790-56)*K,(x+56)*K,(790+56)*K),outline=WH,width=lw)
    d.text((x*K,790*K),n,font=f('Regular',30),fill=MINT,anchor='mm')
    d.text((x*K,885*K),l1,font=f('Regular',26),fill=WH,anchor='mm')
    d.text((x*K,925*K),l2,font=f('SemiBold',26),fill=WH,anchor='mm')
for x in (385,695): d.line((x*K,750*K,x*K,945*K),fill=DIM,width=K)
body=['피부 바로 아래(피하)에 맞는 주사로,','처음 시작할 때는 주사 방법과 부위를','진료실에서 직접 알려드립니다.']
for i,t in enumerate(body): ctext(1035+i*46,t,f('Regular',30),(205,200,192))
ctext(1275,'식사·운동 관리와 함께 쓰는 전문의약품이며, 처방 여부와 용량은 진료 후 결정합니다.',f('Regular',19),GR)
im.resize((1080,1350),Image.LANCZOS).save(S+'/pen/dove_efpe_11_pen_weekly.png')
