import json,re,shutil,html,os
S=".../scratchpad/"  # build-time paths of the original session; edit to rebuild
R=S+'deck2/project/'; OUT='/home/user/hafez-/h-number-map/deck-local/'
M='/home/user/hafez-/h-number-map/math/img/'; D=S+'deckimg/'
blob={'7f88fe87689c1d1cbb249b0ae8dbad26':M+'old_overview.jpg','0086e214b0347084ae3e26b5c1ace6cd':M+'new_overview.jpg','68fbaa84d86d1dca20c1df172685319f':M+'old_dense.jpg','453181d701621fa16eeccf98daf7bcfd':M+'new_dense.jpg','02742333b4defcf8c16e87e295d917d3':M+'old_curved.jpg','de3e0c55b5c21a1734aae83c96167eac':M+'new_curved.jpg','c85e2fc551b29d889f11a7c7bcf0f6cd':M+'oldpdf_overall_s.jpg','61be45157a6af9beb2cc36e456fff680':M+'oldpdf_B.jpg','64c68915f3bbb8dfd718e3733892a2d6':M+'oldpdf_B_zoom.jpg','87d67145c28658a40a6b71b63a45ef41':M+'raw_aerial.jpg','a20caf7d8795eaf3d2d9bb4ae4571a16':M+'raw_annotated.jpg','e97e4df0b87981e321ab3d6a3ee9be96':M+'raw_zoom.jpg',
'98baead63a47c4fabb8b476bbabe05be':'reg_screens','01a30da3a9adcd1a3bbe2d1240a6069d':'reg_matches','cff0b91817fb8a028b029c575078a195':'reg_overlay','6b6c65e1a83e32740d983ec8ca07b447':'tree_lawn','8db836fa4074b9d3c23006543ce98a5c':'tree_dark','88781e6b75eb6ed569e07483b537a650':'tree_peaks','d6821969c1e6f29f053518d933066604':'tree_final','e9dec3000a1fc23eadb433710e98fe75':'road_mask','16ccb116d4b855bcac2dfae39b3d5151':'stones_before_after','598cd6208031c72b01f20f8fddafefd2':'footprints_all','707f7971848c4b286f60035d36705a63':'3d_overview','1f8d7943f550e6d5c59f17a21ec1c1da':'3d_top','fb890a00cbe9ad0aeb3698893ee07534':'3d_walk','f7b2303aec8c56cf1d19d8e7e1a131a5':'3d_office','6f7c1c29b436d29c7c2d0863a2a59fef':'3d_mausoleum','f23e64b57d0377b9b658f634485d294b':'3d_house','5bbc0a4ee27e20c760cf741e238202fc':'3d_headstones','52165db68e9774a3746b8e16ee12df76':'3d_trees_west','7084fee906c6131086197bb5f16480b9':'3d_notredame_ave','68cb69a0616ed0a77ff78111f68b361c':'expl_passes','7091bef8f5d3ecf2ccf942e52cd7d569':'expl_walk','687f3a8c7a2aaa96bf5d22710eee5dd3':'expl_compare','987d1dadc1ac46c491c628499ab311e7':'atlas_lot','dde665860d5e13fd49065af051f4d79f':'atlas_3d_layers','58277d0c1d635d0bd3667b0037e3a723':'expl_why'}
names={}
for k,v in blob.items():
    src=v if v.startswith('/') else D+v+'.jpg'
    n=os.path.basename(src); shutil.copy(src,OUT+'images/'+n); names[k]=n
order=json.load(open(R+'deck.json'))['order']
slides=[];notes=[]
for sid in order:
    t=open(R+'slides/%s.html'%sid).read()
    t=re.sub(r'/_blob/([0-9a-f]{32})',lambda m:'images/'+names[m.group(1)],t)
    m=re.search(r'<aside>(.*?)</aside>',t,re.S); notes.append(html.unescape(m.group(1)) if m else '')
    t=re.sub(r'<aside>.*?</aside>','',t,flags=re.S)
    def emb(m):
        st,body=m.group(1),m.group(2)
        return '<iframe sandbox="allow-scripts" style="%s;border:0" srcdoc="%s"></iframe>'%(st,html.escape(body,quote=True))
    t=re.sub(r'<x-embed style="([^"]*)">(.*?)</x-embed>',emb,t,flags=re.S)
    t=re.sub(r'<section id="[^"]*"( data-transition="[^"]*")?',lambda m:'<section class="slide"',t,1)
    t=t.replace('style="','style="position:relative;width:1920px;height:1080px;overflow:hidden;flex-shrink:0;',1)
    slides.append(t)
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>How the Cedar Grove H-numbers were built</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>html,body{margin:0;height:100%;background:#0b0b0a;overflow:hidden;font-family:Arial,sans-serif}
#stage{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform-origin:0 0}
.slide{display:none !important}.slide.on{display:flex !important}
.slide table{border-collapse:collapse;width:100%}.slide th,.slide td{padding:.35em .6em;border-bottom:1px solid rgba(127,127,127,.35);vertical-align:top}
.slide p,.slide h1,.slide h2,.slide h3{margin:0}.slide ul,.slide ol{margin:0}
#bar{position:fixed;left:0;right:0;bottom:0;display:flex;gap:10px;align-items:center;justify-content:center;padding:8px;background:rgba(0,0,0,.6);color:#ddd;font:14px Arial;z-index:9}
#bar button{background:#24241f;color:#eee;border:1px solid #555;border-radius:6px;padding:6px 14px;cursor:pointer}
#notes{position:fixed;left:0;right:0;bottom:44px;max-height:30%;overflow:auto;background:#141413;color:#e8e6dc;padding:12px 24px;font:17px/1.45 Arial;display:none;z-index:9}</style></head><body>
<div id="stage">'''+'\n'.join(slides)+'''</div><div id="notes"></div>
<div id="bar"><button id="p">&larr; Prev</button><span id="c"></span><button id="n">Next &rarr;</button><button id="t">Notes (N)</button><button id="f">Full screen (F)</button></div>
<script>var N='''+json.dumps(notes)+''';var S=[].slice.call(document.querySelectorAll('.slide')),i=0;
function fit(){var s=Math.min(innerWidth/1920,(innerHeight-44)/1080),st=document.getElementById('stage');st.style.transform='scale('+s+')';st.style.marginLeft=(-960*s)+'px';st.style.marginTop=(-540*s-22)+'px'}
function show(k){i=Math.max(0,Math.min(S.length-1,k));S.forEach(function(e,j){e.classList.toggle('on',j==i)});document.getElementById('c').textContent=(i+1)+' / '+S.length;document.getElementById('notes').textContent=N[i];location.hash=i+1}
function nt(){var e=document.getElementById('notes');e.style.display=e.style.display=='block'?'none':'block'}
function fs(){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}
document.getElementById('p').onclick=function(){show(i-1)};document.getElementById('n').onclick=function(){show(i+1)};document.getElementById('t').onclick=nt;document.getElementById('f').onclick=fs;
addEventListener('keydown',function(e){if(e.key=='ArrowRight'||e.key==' '||e.key=='PageDown')show(i+1);else if(e.key=='ArrowLeft'||e.key=='PageUp')show(i-1);else if(e.key=='n'||e.key=='N')nt();else if(e.key=='f'||e.key=='F')fs()});
addEventListener('resize',fit);fit();show((parseInt(location.hash.slice(1))||1)-1);</script></body></html>'''
open(OUT+'index.html','w').write(page)
print(len(slides),len(page))
