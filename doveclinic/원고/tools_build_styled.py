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
# ---- 1) 원고 → 토큰 ----
J7_OLD=('밀착 상담하는 것이','[[오래 믿고 찾아주시는 ]]','[[<신뢰 있는 병원>이 되는 길이라고 생각합니다. ^^]]')
toks=[];para=[];i=0
def isurl(x): return re.fullmatch(r'https?://\S+',x.strip()) is not None
def flush():
    global para
    if not para: return
    ls=[x for x in para if x.strip()!='[네이버 예약 바로가기 버튼]']
    para=[]
    if not ls: return
    if all(x.startswith('{{q:>') or x.startswith('{{i:>') for x in ls): toks.append(('quote',ls)); return
    if len(ls)==1 and ls[0].startswith('[[네이버 클립 삽입]]'):
        toks.append(('clip',ls[0][len('[[네이버 클립 삽입]]'):].strip())); return
    # J7 문구 (김민 대리 최종본 261126)
    for k in range(len(ls)-2):
        if tuple(ls[k:k+3])==J7_OLD: ls[k:k+3]=['밀착 상담하는 것이 [[오래 믿고 찾아주시는]]','[[<신뢰할 수 있는 병원>이 되는 길이라고 생각합니다. ^^]]']; break
    body=[x for x in ls if not isurl(x)]; urls=[x for x in ls if isurl(x)]
    if body: toks.append(('para',body))
    for u in urls: toks.append(('url',u))
while i<len(src):
    l=src[i]
    if l.strip()=='': flush(); i+=1; continue
    if l.startswith('TITLE:'): toks.append(('title',l[6:].strip())); i+=1; continue
    if l=='HR':
        flush()
        if i+1<len(src) and src[i+1]=='IMG': toks.append(('hrimg',None)); i+=2
        else: toks.append(('hr',None)); i+=1
        continue
    if l=='IMG': flush(); toks.append(('img',None)); i+=1; continue
    if l.startswith('BIG:'): flush(); toks.append(('big',l[4:].strip())); i+=1; continue
    if l.startswith('H3C:'): flush(); toks.append(('h3c',l[4:].strip())); i+=1; continue
    if l.startswith('H3:'): flush(); toks.append(('h3',l[3:].strip())); i+=1; continue
    if l.startswith('Q:'): flush(); toks.append(('q',l[2:].strip().split('⏎'))); i+=1; continue
    m=re.match(r'(BOX|ROWS|INFO|SUMMARY)(?::(\S+))?$',l)
    if m:
        kind,bg=m.group(1),m.group(2); flush(); i+=1; rows=[]
        while src[i]!='END': rows.append(src[i]); i+=1
        i+=1
        k=kind.lower()
        if kind=='BOX': k='box_p' if bg=='p' else ('box_link' if any(isurl(r) for r in rows) else 'box')
        toks.append((k,(rows,bg))); continue
    m=re.match(r'GRID(?::(\S+),(\S+))?$',l)
    if m:
        flush(); i+=1; rows=[]
        while src[i]!='END': rows.append(src[i].split('|')); i+=1
        i+=1; toks.append(('grid',rows)); continue
    para.append(l); i+=1
flush()
# 인사말 '안녕하세요.' 분리
for k,(kind,v) in enumerate(toks):
    if kind=='para' and v[0].strip()=='안녕하세요.' and len(v)>1:
        toks[k:k+1]=[('para',[v[0]]),('greet',v[1:])]; break
# ---- 2) 토큰 렌더링 ----
def render(kind,v):
    if kind=='title': return f'<h1 style="line-height:150%">{inl(v)}</h1>'
    if kind=='hrimg': return '<hr>'+P('[image]')
    if kind=='hr': return '<hr>'
    if kind=='hrline': return '<hr>'+P('')
    if kind=='img': return P('[image]')
    if kind in ('para','greet','quote'): return ''.join(P(x) for x in v)
    if kind=='url': return P(v)
    if kind=='clip': return P('[[네이버 클립 삽입]] ')+f'<p><a href="{html.escape(v)}" style="color:#1155cc">{html.escape(v)}</a></p>'
    if kind=='big': return P(f'[[13pt:{v}]]')
    if kind=='h3c': return f'<h3 style="text-align:center;line-height:150%"><span style="font-size:14pt;font-weight:700">{inl(v)}</span></h3>'
    if kind=='h3': return f'<h3 style="line-height:150%">{inl(v)}</h3>'
    if kind=='q': return TB+'<tr><td>'+''.join(f'<h2 style="line-height:100%;margin:0">{inl(q)}</h2>' for q in v)+'</td></tr></table>'
    if kind=='summary':
        rows=v[0]; title,body=rows[0],rows[1:]; parts=[]
        for n,r in enumerate(body):
            if n: parts.append(P(''))
            parts+= [P(x) for x in r.split('⏎')]
        return TB+'<tr><td style="background-color:'+pal()[2]+f'"><h3 style="text-align:center;line-height:150%;margin:0">{inl(title)}</h3>'+P('')+''.join(parts)+'</td></tr></table>'
    if kind=='box_p':
        parts=[]
        for n,r in enumerate(v[0]):
            if n: parts.append(P('',';text-align:center'))
            parts+=[P(x,';text-align:center') for x in r.split('⏎')]
        return TB+'<tr><td style="background-color:'+CAUTION+'">'+''.join(parts)+'</td></tr></table>'
    if kind=='box_link':
        rows=v[0]; desc=[x for r in rows if not isurl(r) for x in r.split('⏎')]; us=[r for r in rows if isurl(r)]
        return TB+'<tr><td style="background-color:'+pal()[2]+'">'+''.join(P(x) for x in desc)+P('')+''.join(P(u) for u in us)+'</td></tr></table>'
    if kind=='box':
        rows,bg=v; return TB+'<tr>'+cell([x for r in rows for x in r.split('⏎')],'#f3f3f3' if bg=='gr' else pal()[2])+'</tr></table>'
    if kind=='rows':
        pm=pal()[1]; return TB+''.join('<tr>'+cell(r.split('⏎'),pm)+'</tr>' for r in v[0])+'</table>'
    if kind=='info':
        h=''; pm=pal()[1]
        for r in v[0]:
            lab,txt=r.split('|',1)
            h+='<tr><td style="background-color:'+pm+'">'+f'<h3 style="line-height:150%;margin:0"><b>{inl(lab)}</b></h3>'+''.join(P(x) for x in txt.split('⏎'))+'</td></tr>'
        return TB+h+'</table>'
    if kind=='grid':
        h=''; ps=pal()
        for ri,r in enumerate(v):
            h+='<tr>'+''.join(cell([f'[[12pt:{c.strip()}]]'] if ri==0 else c.strip().split('⏎'),ps[0] if ri==0 else ps[2],'c') for c in r)+'</tr>'
        return TB+h+'</table>'
    raise ValueError(kind)
# ---- 3) 간격 규칙 (261126 김민 대리 최종 업로드 형태: 19편 기준) ----
TABLES={'grid','rows','info','box','box_link'}
def txt(t): return ' '.join(t[1]) if isinstance(t[1],list) else str(t[1])
def gap(a,b,nxt):
    ka,kb=a[0],b[0]
    if ka=='title': return []
    if ka=='hrimg': return ['B'] if kb in ('summary','q') else ['B','B']
    if kb=='hrimg': return ['B']
    if ka=='greet' and kb=='quote': return ['B','HR']
    if ka=='quote' and kb=='quote': return ['B','B']
    if ka=='quote' and txt(a).startswith('{{q:>') and kb=='para' and intro_q[0]: intro_q[0]=False; return ['HR','B']
    if ka=='para' and kb=='big' and b[1].startswith('중요한 건'): return ['B','HR']
    if ka=='quote' and kb=='h3': return ['HR','B','B']
    if ka=='rows' and kb=='para' and txt(b).startswith('그리고 한 가지 더'): return ['HR','B']
    if ka=='para' and '신뢰할 수 있는 병원' in txt(a) and kb=='img': return ['B','HR','B']
    if ka in TABLES and kb=='img': return ['B']
    if ka=='img' or kb=='img': return ['B','B']
    if ka=='q': return ['B']
    if kb in TABLES: return ['B']
    if ka=='box_link': return ['B','B']
    if ka in TABLES: return ['B']
    if kb in ('url','clip') or ka in ('url','clip'): return ['B']
    if ka=='box_p': return ['B']
    if kb=='hr' and nxt and nxt[0]=='h3c': return []
    if ka=='hr' and kb=='h3c': return []
    if ka=='h3c': return ['B']
    if kb=='box_p': return ['B']
    return ['B','B']
intro_q=[True]
out=[]
for n,t in enumerate(toks):
    if n:
        for g in gap(toks[n-1],t,toks[n+1] if n+1<len(toks) else None):
            out.append(P('') if g=='B' else render('hrline',None))
    if t[0]=='hrimg' and n and toks[n-1][0]=='title': pass
    out.append(render(*t))
title=sys.argv[3]
doc=f'<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>{title}</title><style>p{{line-height:150%;margin:0}} table{{border-collapse:collapse;width:468pt}} td{{border:0.75pt solid #999999;padding:4.5pt;vertical-align:top}} h1,h3{{line-height:150%}}</style></head><body>\n'+'\n'.join(out)+'\n</body></html>\n'
open(sys.argv[2],'w',encoding='utf-8').write(doc)
