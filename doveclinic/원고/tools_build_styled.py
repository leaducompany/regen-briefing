import re,sys,html
# Styled builder that mirrors the editor's formatting in 1~4편 (Google Docs HTML import)
src=open(sys.argv[1],encoding='utf-8').read().splitlines()
LS=''
BG={'y':'#fff1cc','p':'#f4cccc','b':'#c9daf7','m':'#ead1dc','t':'#d0e0e3','g':'#d9ead3','o':'#fce4cd','gr':'#eeeeee','lb':'#e1ecff'}
FG={'blue':'#3c78d8','red':'#cc0000','brown':'#7f6000','purple':'#674ea7','teal':'#45818e','plum':'#a64d78','dred':'#660000','navy':'#1155cc','wine':'#731b47','dteal':'#134f5c'}
def span(t,st): return f'<span style="{st}">{t}</span>'
def inl(t):
    t=html.escape(t,quote=False)
    # [[key:text]] bold + highlight / color ; [[text]] bold
    def b(m):
        k,txt=m.group(1),m.group(2)
        st='font-weight:700'
        if k:
            k=k[:-1]
            for part in k.split(','):
                if part in BG: st+=f';background-color:{BG[part]}'
                elif part in FG: st+=f';color:{FG[part]}'
                elif part=='u': st+=';text-decoration:underline'
                elif part.endswith('pt'): st+=f';font-size:{part}'
        return span(txt,st)
    t=re.sub(r'\[\[((?:[a-z0-9,]+):)?(.+?)\]\]',b,t)
    t=re.sub(r'\{\{u:(.+?)\}\}',lambda m:span(m.group(1),'text-decoration:underline'),t)
    t=re.sub(r'\{\{q:(.+?)\}\}',lambda m:span(m.group(1),'font-style:italic;color:#434343;font-size:12pt'),t)
    t=re.sub(r'\{\{i:(.+?)\}\}',lambda m:span(m.group(1),'font-style:italic;font-size:12pt'),t)
    t=re.sub(r'\(출처: (https?://\S+?)\)',lambda m:span(f'(출처: {m.group(1)})','color:#666666;font-size:9pt'),t)
    t=re.sub(r'(?<![">])(https://blog\.naver\.com/\S+)',lambda m:f'<a href="{m.group(1)}">{m.group(1)}</a>',t)
    return t
def P(t,extra=''):
    a=f' style="{extra[1:]}"' if extra else ''
    return f'<p{a}>{inl(t) if t else "<br>"}</p>'
BR=P('')+P('')
def cell(lines,bg=None,align=None):
    st=''
    if bg: st=f'background-color:{BG.get(bg,bg)}'
    ex=';text-align:center' if align=='c' else ''
    return (f'<td style="{st}">' if st else '<td>')+''.join(P(x,ex) for x in lines)+'</td>'
TB='<table>'
# 파스텔 팔레트 (진한 머리행, 중간 행, 연한 본문) — 표마다 돌려 가며 사용
PALS=[('#c5d9f2','#dbe8f8','#edf3fc'),('#c3e3d5','#d9eee5','#edf7f2'),('#d6cdea','#e5def2','#f3effa'),
      ('#f5d3bf','#f9e2d4','#fdf1ea'),('#f1e1a6','#f7ebc4','#fcf6e3'),('#d3e0c4','#e3ebd8','#f2f6ec'),('#efcbd6','#f5dde4','#fbeff3')]
import zlib
_pi=[zlib.crc32(sys.argv[3].encode())%len(PALS)]
def pal():
    p=PALS[_pi[0]%len(PALS)]; _pi[0]+=1; return p
CAUTION='#f6d6d6'
out=[];para=[];i=0
def flush():
    global para
    if para: out.append(''.join(P(l) for l in para)); out.append(BR); para=[]
while i<len(src):
    l=src[i]
    if l.strip()=='': flush(); i+=1; continue
    if l.startswith('TITLE:'): out.append(f'<h1 style="line-height:150%">{inl(l[6:].strip())}</h1>'); i+=1; continue
    if l=='HR': flush(); out.append('<hr>'); i+=1; continue
    if l=='IMG': flush(); out.append(P('[image]')); i+=1; continue
    if l.startswith('BIG:'):  # bold 13pt line
        flush(); out.append(P(f'[[13pt:{l[4:].strip()}]]')); out.append(BR); i+=1; continue
    if l.startswith('H3C:'): flush(); out.append(f'<h3 style="text-align:center;line-height:150%"><span style="font-size:14pt;font-weight:700">{inl(l[4:].strip())}</span></h3>'); i+=1; continue
    if l.startswith('H3:'): flush(); out.append(f'<h3 style="line-height:150%">{inl(l[3:].strip())}</h3>'); i+=1; continue
    if l.startswith('Q:'):
        flush(); qs=l[2:].strip().split('⏎')
        out.append(TB+'<tr><td>'+''.join(f'<h2 style="line-height:100%;margin:0">{inl(q)}</h2>' for q in qs)+'</td></tr></table>'); out.append(BR)
        i+=1; continue
    m=re.match(r'(BOX|ROWS|INFO|SUMMARY)(?::(\S+))?$',l)
    if m:
        kind,bg=m.group(1),m.group(2); flush(); i+=1; rows=[]
        while src[i]!='END': rows.append(src[i]); i+=1
        i+=1
        if kind=='BOX': out.append(TB+'<tr>'+cell([x for r in rows for x in r.split('⏎')],CAUTION if bg=='p' else ('#f3f3f3' if bg=='gr' else pal()[2]))+'</tr></table>')
        elif kind=='SUMMARY':
            title,body=rows[0],rows[1:]
            out.append(TB+'<tr><td style="background-color:'+pal()[2]+'">'
                       f'<h3 style="text-align:center;line-height:150%;margin:0">{inl(title)}</h3>'+P('')+''.join(P(x) for r in body for x in r.split('⏎'))+'</td></tr></table>')
        elif kind=='ROWS':
            pm=pal()[1]; out.append(TB+''.join('<tr>'+cell(r.split('⏎'),pm)+'</tr>' for r in rows)+'</table>')
        elif kind=='INFO':  # "label|line⏎line"
            h=''; pm=pal()[1]
            for r in rows:
                lab,txt=r.split('|',1)
                h+='<tr><td style="background-color:'+pm+'">'+f'<h3 style="line-height:150%;margin:0"><b>{inl(lab)}</b></h3>'+''.join(P(x) for x in txt.split('⏎'))+'</td></tr>'
            out.append(TB+h+'</table>')
        out.append(BR); continue
    m=re.match(r'GRID(?::(\S+),(\S+))?$',l)
    if m:
        hb,bb=m.group(1),m.group(2); flush(); i+=1; rows=[]
        while src[i]!='END': rows.append(src[i].split('|')); i+=1
        i+=1; h=''; ps=pal()
        for ri,r in enumerate(rows):
            h+='<tr>'+''.join(cell([f'[[12pt:{c.strip()}]]'] if ri==0 else c.strip().split('⏎'),ps[0] if ri==0 else ps[2],'c') for c in r)+'</tr>'
        out.append(TB+h+'</table>'); out.append(BR); continue
    para.append(l); i+=1
flush()
title=sys.argv[3]
doc=f'<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>{title}</title><style>p{{line-height:150%;margin:0}} table{{border-collapse:collapse;width:468pt}} td{{border:0.75pt solid #999999;padding:4.5pt;vertical-align:top}} h1,h3{{line-height:150%}}</style></head><body>\n'+'\n'.join(out)+'\n</body></html>\n'
open(sys.argv[2],'w',encoding='utf-8').write(doc)
