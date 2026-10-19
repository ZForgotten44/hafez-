(function(){
"use strict";
var $=function(i){return document.getElementById(i)};
var esc=function(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')};
var pad=function(h){return 'H'+String(h).padStart(6,'0')};
var fmt=function(n){return Number(n).toLocaleString('en-US')};
var toastT;var toast=function(m){var t=$('toast');t.textContent=m;t.classList.add('show');clearTimeout(toastT);toastT=setTimeout(function(){t.classList.remove('show')},1800)};
var SEC='ABCDEFGHIJKLM'.split('');
var COL=['#b4531f','#17496e','#2f6b46','#8a3b8f','#b8892f','#a23325','#3a7d8c','#6b5b95','#c27c0e','#4a6b2f','#7a4a3a','#2d5f9e','#8c6a5a'];
var scol=function(s){return COL[SEC.indexOf(s)]||'#888'};
var A=X.A, FWD=X.fwd.filter(function(r){return !/dr$/.test(r[1])}), W=X.W, TR=X.trace;
var FW={};FWD.forEach(function(r){FW[r[0]+'|'+r[1]]=r[2]});
function on(el,ev,fn){if(el)el.addEventListener(ev,fn)}
var css=function(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim()||'#888'};
var isDark=function(){return getComputedStyle(document.documentElement).colorScheme.indexOf('dark')===0};
var ramp=function(t){t=Math.max(0,Math.min(1,t));var l=isDark()?(16+t*70):(90-t*62);return 'hsl(40,'+(isDark()?'6%':'7%')+','+l.toFixed(1)+'%)'};
var redraws=[],rdT=0;function redrawAll(){redraws.forEach(function(f){try{f()}catch(e){}})}
/* a theme change repaints the pictures one after another, after the new colours are on screen, so the switch itself never stalls */
function scheduleRedraw(){clearTimeout(rdT);rdT=setTimeout(function(){var q=redraws.slice();(function next(){var f=q.shift();if(!f)return;try{f()}catch(e){}setTimeout(next,0)})()},60)}
function compile(decl){return new Function('S','L','var m,p,n,f,r,q,c,k,i,j,g,b,'+decl.replace(/;/g,',')+';return '+X.giant.expr+';')}
var GH=compile(X.giant.decl);
var RV=(function(){var m={};FWD.forEach(function(r){(m[r[2]]=m[r[2]]||[]).push(r[0]+'-'+r[1])});return m})();
var pf2=function(w1,w2,r){var s=0;for(var j=0;j<r-1;j++)s+=(w1[j]||0)+(w2[j]||0);return s};
var PASSES=[
 {n:1,secs:'B, A',lo:1,hi:836,how:'Level by level: one level of B, then the same level of A. 19 levels of 44 lots.'},
 {n:2,secs:'D, C',lo:837,hi:1871,how:'Row by row: row r of D, then row r of C. Rows are uneven, so offsets are running totals.'},
 {n:3,secs:'F, E',lo:1872,hi:2331,how:'Row by row: row r of F, then row r of E.'},
 {n:4,secs:'B, D, F margins; G, H',lo:2332,hi:2586,how:'Three margin lists in order (B 41 lots, D 29, F 12), then rows of G and H woven together.'},
 {n:5,secs:'M',lo:2587,hi:2835,how:'M: the first 51 lots come from a stored list, then lots 82 to 279 in order.'},
 {n:6,secs:'K, J, I, L',lo:2836,hi:3185,how:'K (a stored list of 115 lots), then J 1 to 132, I 1 to 64 and L 69 to 107.'}];
var LOTS=X.maplots.filter(function(l){return l[4]}).map(function(l){return {s:l[0],l:l[1],h:l[3],poly:l[4],cx:l[5],cy:l[6]}}).sort(function(a,b){return a.h-b.h});

/* ---------------- presentation controls ---------------- */
(function(){
  var root=document.documentElement,mq=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)'),curT=null;
  try{var s=localStorage.getItem('cg-theme');if(s==='light'||s==='dark')curT=s}catch(e){}
  if(!curT)curT=mq&&mq.matches?'dark':'light';
  function applyTheme(skip){root.setAttribute('data-theme',curT);var b=$('btheme');b.setAttribute('aria-pressed',curT==='dark');b.setAttribute('aria-label',curT==='dark'?'Switch to light theme':'Switch to dark theme');if(skip!==true)scheduleRedraw()}
  on($('btheme'),'click',function(){curT=curT==='dark'?'light':'dark';try{localStorage.setItem('cg-theme',curT)}catch(e){}applyTheme()});applyTheme(true);
  window.addEventListener('beforeprint',function(){root.setAttribute('data-theme','light');redrawAll()});
  window.addEventListener('afterprint',function(){applyTheme()});
  var lg=false;try{lg=localStorage.getItem('cg-size')==='lg'}catch(e){}
  function applySize(){if(lg)root.setAttribute('data-size','lg');else root.removeAttribute('data-size');$('bsize').setAttribute('aria-pressed',lg);$('bsize').title=lg?'Back to normal text':'Larger text for projection';$('bsize').textContent=lg?'Aa −':'Aa +';try{localStorage.setItem('cg-size',lg?'lg':'n')}catch(e){}}
  on($('bsize'),'click',function(){lg=!lg;applySize()});applySize();
  on($('bfs'),'click',function(){
    try{if(document.fullscreenElement){document.exitFullscreen()}else{var p=root.requestFullscreen();if(p&&p.catch)p.catch(function(){toast('Full screen is not available in this viewer')})}}catch(e){toast('Full screen is not available in this viewer')}});
  document.addEventListener('fullscreenchange',function(){$('bfs').textContent=document.fullscreenElement?'Exit full screen':'Full screen'});

  var ids=['raw','legacy','why','h','math','code','giant','compare','appendix'],els=ids.map($);
  var titles={raw:'The raw maps',legacy:'The old numbering',why:'Why it confuses',h:'The H-number idea',math:'The math, step by step',code:'The code',giant:'The giant formula',compare:'Old and new',appendix:'Checks and errata'};
  /* side menu: collapsed to numbers, expandable to titles and sub-headings */
  var list=$('railist'),subs={};
  ids.forEach(function(id,i){
    var sec=els[i],hs=[].slice.call(sec.querySelectorAll(':scope > h3, :scope > h4, :scope .demo > header > h3'));
    var n=0,li=document.createElement('li');li.className='sec'+(i===0?' x':'');li.setAttribute('data-id',id);
    var html='<a href="#'+id+'"><i>'+String(i+1).padStart(2,'0')+'</i><span>'+titles[id]+'</span><b aria-hidden="true">'+(hs.length?'+':'')+'</b></a>';
    if(hs.length){html+='<ul>';hs.forEach(function(h){if(!h.id)h.id=id+'-'+(++n);var t=h.textContent.replace(/\s+/g,' ').trim().replace(/^[ABC] /,'');html+='<li><a href="#'+h.id+'" data-h="'+h.id+'">'+esc(t.length>34?t.slice(0,32)+'…':t)+'</a></li>'});html+='</ul>'}
    li.innerHTML=html;list.appendChild(li);subs[id]=hs;
    li.querySelector('a').addEventListener('click',function(e){if(root.getAttribute('data-rail')==='open'&&hs.length){li.classList.toggle('x');li.setAttribute('data-u','1')}if(window.innerWidth<=980)setRail(false)});
    [].forEach.call(li.querySelectorAll('ul a'),function(a){a.addEventListener('click',function(){if(window.innerWidth<=980)setRail(false)})});
  });
  function setRail(open){if(open)root.setAttribute('data-rail','open');else root.removeAttribute('data-rail');$('bmenu').setAttribute('aria-expanded',open);try{if(window.innerWidth>980)localStorage.setItem('cg-rail',open?'1':'0')}catch(e){}}
  
  on($('bmenu'),'click',function(){setRail(root.getAttribute('data-rail')!=='open')});
  try{if(window.innerWidth>980&&localStorage.getItem('cg-rail')==='1')setRail(true)}catch(e){}
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&window.innerWidth<=980&&root.getAttribute('data-rail')==='open')setRail(false)});

  function cur(){var y=window.scrollY+110,c=-1;els.forEach(function(s,i){if(s.offsetTop<=y)c=i});return c}
  function go(i){if(i<0){window.scrollTo({top:0});return}if(i>=els.length)return;els[i].scrollIntoView()}
  
  
  var secs=[].slice.call(list.children);
  function mark(){var c=cur();secs.forEach(function(li,i){li.classList.toggle('on',i===c);if(i===c)li.classList.add('x');else if(!li.getAttribute('data-u'))li.classList.remove('x')});
    if(c>=0){var y=window.scrollY+120,best=null;subs[ids[c]].forEach(function(h){if(h.getBoundingClientRect().top+window.scrollY<=y)best=h.id});[].forEach.call(secs[c].querySelectorAll('ul a'),function(a){a.classList.toggle('on',a.getAttribute('data-h')===best)})}}
  window.addEventListener('scroll',mark,{passive:true});mark();
})();

/* ---------------- lightbox ---------------- */
(function(){
  var lb=$('lb'),st=$('lbstage'),cp=$('lbcap'),last=null;
  function open(w){last=w;st.innerHTML='';var c=w.cloneNode(true);c.removeAttribute('tabindex');c.removeAttribute('role');st.appendChild(c);
    cp.innerHTML='<p>'+esc(w.getAttribute('data-cap')||'')+'</p>';var fig=w.closest('figure'),ol=fig&&fig.querySelector('ol.calls');if(ol)cp.appendChild(ol.cloneNode(true));
    lb.classList.add('on');document.body.style.overflow='hidden';$('lbclose').focus()}
  function close(){lb.classList.remove('on');document.body.style.overflow='';if(last)last.focus()}
  document.addEventListener('click',function(e){var w=e.target.closest&&e.target.closest('.imgwrap');if(w&&!lb.contains(w))open(w);else if(e.target===lb)close()});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&lb.classList.contains('on'))close();if((e.key==='Enter'||e.key===' ')&&e.target.classList&&e.target.classList.contains('imgwrap')&&!lb.contains(e.target)){e.preventDefault();open(e.target)}});
  on($('lbclose'),'click',close);
})();

/* ---------------- shared: label description ---------------- */
function kindOf(l){if(/^[A-Z]\d/.test(l)||!/^\d/.test(l))return 'odd';if(/^\d+H[AB]?$/.test(l))return 'h';if(/^\d+[A-Z]$/.test(l))return 'suffix';if(/^\d+$/.test(l))return 'plain';return 'odd'}
var KINDTXT={plain:'a plain number',h:'a legacy H-lot (label ends in H)',suffix:'a lot with a letter suffix',odd:'an unusual label'};
var TIERTXT=['arithmetic (one formula)','row constants (formula plus per-row numbers)','an explicit stored list','errata (known typo or duplicate)'];
function describe(S,L){
  var H=FW[S+'|'+L],t=TR[S+'|'+L],k=kindOf(L);
  var s='<b>'+S+'-'+esc(L)+'</b> is '+KINDTXT[k]+'.';
  if(k==='h')s+=' Here "H" is a legacy suffix. The new H-number prefix is a different thing.';
  if(H==null)return s+' The decoder does not list this label.';
  s+=' H-number <b>'+pad(H)+'</b>.';
  if(t){s+=' Derived by '+TIERTXT[t[2]]+'.';if(t[0]!=null)s+=' Level '+t[0]+', place '+t[1]+' in the decoder\'s indexing.'}
  var o=RV[H];if(o&&o.length>1)s+=' Shares this H-number with '+o.filter(function(x){return x!==S+'-'+L}).map(esc).join(', ')+'.';
  return s;
}
function chipBtn(S,L,kind,target,group){var b=document.createElement('button');b.type='button';b.className='chip '+(kind==='plain'?'':kind);b.textContent=L||'?';b.setAttribute('aria-pressed','false');
  on(b,'click',function(){if(group._pressed)group._pressed.setAttribute('aria-pressed','false');b.setAttribute('aria-pressed','true');group._pressed=b;target.innerHTML=describe(S,L)});return b}

/* ---------------- section 2 ---------------- */
(function(){
  $('nPoly').textContent=fmt(X.maplots.length);
  var parts=[['A','Section','The section letter, A to M. Required: the same label exists in other sections.'],['13','Lot label','The number written on the lot. It restarts in every section and its counting rule differs by section.'],['H','Suffix','A legacy H-lot: a lot whose label ends in H, sitting next to the lot with the same number. What the H originally stood for is not confirmed. It has nothing to do with the new H-number prefix, which only happens to use the same letter.']];
  var addr=$('addr');parts.forEach(function(p,i){var b=document.createElement('button');b.type='button';b.setAttribute('aria-pressed',i===0?'true':'false');b.innerHTML='<b>'+p[0]+'</b><span>'+p[1]+'</span>';
    on(b,'click',function(){[].forEach.call(addr.children,function(x){x.setAttribute('aria-pressed','false')});b.setAttribute('aria-pressed','true');$('addrdetail').innerHTML='<b>'+p[1]+' '+p[0]+'.</b> '+p[2]+(i===2?' Full address: <b>A-13H</b> = '+pad(FW['A|13H'])+'.':'')});addr.appendChild(b)});
  $('addrdetail').innerHTML='<b>Section A.</b> '+parts[0][2]+' The full address of this lot is <b>A-13H</b>.';
  var sg=$('sampleChips'),picks=[['A','13H'],['B','19A'],['B','384HA'],['C','51'],['C','12B'],['D','1H'],['D','F1'],['E','199BH'],['G','19'],['K','57'],['M','61'],['B','B362'],['D','384A']];
  picks.forEach(function(p){if(FW[p[0]+'|'+p[1]]!=null){var b=chipBtn(p[0],p[1],kindOf(p[1]),$('sampledetail'),sg);b.textContent=p[0]+'-'+p[1];sg.appendChild(b)}});
  var an=$('anatomy');
  SEC.forEach(function(s){var rows=X.chips[s];if(!rows)return;var d=document.createElement('div');d.className='anat';d.innerHTML='<h5>Section '+s+'<small>first two rows, in walking order</small></h5>';
    var w=document.createElement('div');w.className='rowsc';w.innerHTML='<div class="sbtn"><button type="button" aria-label="Scroll left">←</button><button type="button" aria-label="Scroll right">→</button></div>';var sc=document.createElement('div');sc.className='sc';
    rows.forEach(function(row,ri){var g=document.createElement('div');g.className='line';var l=document.createElement('span');l.className='rl';l.textContent='row '+(ri+1);g.appendChild(l);
      row.forEach(function(cc){if(cc[0]==null){var x=document.createElement('span');x.className='chip gap static';x.textContent='gap';g.appendChild(x);return}g.appendChild(chipBtn(s,cc[0],cc[1],$('anatdetail'),an))});sc.appendChild(g)});
    w.appendChild(sc);var bs=w.querySelectorAll('.sbtn button');on(bs[0],'click',function(){sc.scrollBy({left:-320,behavior:'smooth'})});on(bs[1],'click',function(){sc.scrollBy({left:320,behavior:'smooth'})});
    d.appendChild(w);an.appendChild(d)});
})();

/* ---------------- section 3 ---------------- */
var emphStats;
(function(){
  var st=[[fmt(A.lots-2),'legacy references the decoder accepts',''],[A.distinct_labels,'distinct label strings among them',''],[A.labels_in_2plus_sections,'labels used by two or more sections','rep'],[Math.round(100*A.lots_with_shared_label/A.lots)+'%','of references share their label string with another section','rep'],[A.max_sections_per_label,'sections that each have a lot labelled "19"','rep'],[A.unlabeled_positions.count,'positions in the first sweep with no label at all','']];
  $('stats').innerHTML=st.map(function(s){return '<tr data-k="'+s[2]+'"><td class="n">'+s[0]+'</td><td class="l">'+s[1]+'</td></tr>'}).join('');
  emphStats=function(k){[].forEach.call($('stats').rows,function(r){r.classList.toggle('em',!!k&&r.getAttribute('data-k')===k)})};
  var byL={};FWD.forEach(function(r){(byL[r[1].toUpperCase()]=byL[r[1].toUpperCase()]||[]).push(r)});
  function show(){var q=$('lbl').value.trim().toUpperCase(),r=byL[q]||[];emphStats(r.length>1?'rep':'');if(!q){$('lblout').innerHTML='';return}
    if(!r.length){$('lblout').innerHTML='<p class="note">No section has a lot labelled "'+esc(q)+'".</p>';return}
    $('lblout').innerHTML='<p><b>'+r.length+'</b> lot'+(r.length>1?'s':'')+' labelled "'+esc(q)+'"'+(r.length>1?', one per section:':':')+'</p><div class="chips">'+r.map(function(x){return '<span class="chip static" style="border-left:4px solid '+scol(x[0])+'">'+x[0]+'-'+esc(x[1])+' → '+pad(x[2])+'</span>'}).join('')+'</div>'+(r.length>1?'<p class="note" style="margin-top:8px">Each is a different complete address. To use the label you must also know the section and that section\'s rule.</p>':'')}
  on($('lbl'),'input',show);
  var multi=Object.keys(byL).filter(function(k){return byL[k].length>=3});
  on($('lblr'),'click',function(){$('lbl').value=multi[Math.floor(Math.random()*multi.length)];show()});show();
  var rules=[['A','19 per row, counted right to left','H-lots slipped in before places 13, 5 and 1 of every row'],['B','20 per row in the body, last column steps by 19','Columns 2 and 3 both claim 19; "19A" is an extra; a 41-lot margin is numbered 373 to 394 with letters'],['C','Row tops go 19, 38 … 247, then 16 at a time, then 19','Twin pairs (51 and its H-lot) and A/B/C trios on eight rows'],['D','20 per row for rows 2 to 15, then blocks that run both ways','H-lots at 20(r−1) and 20r−11; row 1 uses letters; a 29-lot margin numbered 542 to 563'],['E','19 per row with twins at places 13, 9 and 5','Rows 9 to 12 change shape; lots 152, 169 and 190 to 199 carry A/B suffixes'],['F','18 per row','Eleven rows; a margin of 12 lots numbered 199 to 210'],['G','19 per row for lots 1 to 57','58 to 60 and 61 to 75 are added on; the label 19 appears twice in row 1'],['H','23 per row','Four rows only'],['I','1 to 64 straight','Just a counter'],['J','1 to 132 straight','Just a counter'],['K','115 lots in an order no formula gives','1, 2, 3, 6, 7, 8, 9, 13 … stored as a list'],['L','Starts at 69 and ends at 107','Numbers 1 to 68 do not exist here'],['M','82 to 279 straight','The first 51 lots are in an irregular order and stored as a list']];
  var V=A.verify.per_section;
  var h='<table class="t"><tr><th>Section</th><th>How its labels are built</th><th>Special cases</th><th>Decoder coverage</th></tr>';
  rules.forEach(function(r){var v=V[r[0]]||{},tot=0;Object.keys(v).forEach(function(k){tot+=v[k]});
    var bars=[['closed','#2f8f5a','arithmetic'],['rows','#c9a227','row constants'],['list','#c0392b','explicit list'],['errata','#9b59b6','errata']].map(function(b){return v[b[0]]?'<i title="'+b[2]+': '+v[b[0]]+'" style="display:inline-block;height:10px;width:'+Math.max(3,Math.round(140*v[b[0]]/Math.max(tot,1)))+'px;background:'+b[1]+'"></i>':''}).join('');
    var txt=['closed','rows','list','errata'].filter(function(k){return v[k]}).map(function(k){return v[k]+' '+({closed:'arithmetic',rows:'row constants',list:'list',errata:'errata'})[k]}).join(', ');
    h+='<tr><td><b>'+r[0]+'</b></td><td>'+r[1]+'</td><td>'+r[2]+'</td><td style="white-space:nowrap">'+bars+'<div class="note">'+txt+'</div></td></tr>'});
  $('rules').innerHTML=h+'</table>';
})();

/* whole-cemetery map */
(function(){
  var bb=X.bbox,svg=$('mapsvg'),NS='http://www.w3.org/2000/svg',mode='n',polys=[],labs=[];
  svg.setAttribute('viewBox',(bb[0]-6)+' '+(bb[1]-6)+' '+(bb[2]-bb[0]+12)+' '+(bb[3]-bb[1]+12));
  function color(l){if(mode==='s')return scol(l[0]);if(mode==='h')return 'hsl('+Math.round(240-240*(l[3]-1)/3184)+',65%,52%)';var n=parseInt(l[1].replace(/[^0-9]/g,''),10)||0;return 'hsl('+((n*47)%360)+',60%,'+(40+(n*13)%25)+'%)'}
  X.maplots.forEach(function(l){if(!l[4])return;var p=document.createElementNS(NS,'polygon');p.setAttribute('points',l[4].map(function(q){return q.join(',')}).join(' '));p._l=l;svg.appendChild(p);polys.push(p)});
  var acc={};X.maplots.forEach(function(l){if(l[5]!=null){(acc[l[0]]=acc[l[0]]||[]).push([l[5],l[6]])}});
  Object.keys(acc).forEach(function(s){var a=acc[s].sort(function(x,y){return x[0]-y[0]}),b=acc[s].slice().sort(function(x,y){return x[1]-y[1]});var t=document.createElementNS(NS,'text');t.setAttribute('x',a[a.length>>1][0]);t.setAttribute('y',b[b.length>>1][1]);t.setAttribute('text-anchor','middle');t.setAttribute('style','font:700 26px var(--sans);fill:var(--fg);stroke:var(--bg);stroke-width:5px;paint-order:stroke;pointer-events:none');t.textContent=s;svg.appendChild(t);labs.push(t)});
  function paint(){polys.forEach(function(p){p.setAttribute('fill',color(p._l))});labs.forEach(function(t){t.style.display=mode==='h'?'none':''});
    $('mapnote').textContent={n:'Colored by the number written on the lot. Neighbouring lots get unrelated colors because every section restarts and skips.',s:'Colored by old section letter. Section letters are drawn on the map.',h:'Colored by H-number: one smooth sweep from blue (H000001) to red (H003185). There are no sections here, only one numbered path.'}[mode];
    $('maplegend').innerHTML=mode==='s'?SEC.map(function(s){return '<span><i style="background:'+scol(s)+'"></i>'+s+'</span>'}).join(''):mode==='h'?'<span><i style="background:hsl(240,65%,52%)"></i>H000001</span><span><i style="background:hsl(120,65%,52%)"></i>middle</span><span><i style="background:hsl(0,65%,52%)"></i>H003185</span>':'<span>Each color is a label number. Colors repeat because label numbers repeat in every section.</span>'}
  [].forEach.call(document.querySelectorAll('button.seg[data-mode]'),function(b){on(b,'click',function(){mode=b.getAttribute('data-mode');[].forEach.call(document.querySelectorAll('button.seg[data-mode]'),function(x){x.classList.toggle('on',x===b)});paint()})});
  var tip=$('maptip'),box=$('mapbox');
  on(svg,'mousemove',function(e){var p=e.target;if(!p._l){tip.style.display='none';return}var l=p._l,r=box.getBoundingClientRect();tip.textContent=l[0]+'-'+l[1]+'  →  '+l[2];tip.style.display='block';tip.style.left=Math.min(e.clientX-r.left+12,r.width-170)+'px';tip.style.top=(e.clientY-r.top+14)+'px'});
  on(svg,'mouseleave',function(){tip.style.display='none'});paint();
})();

/* ---------------- walk both numbering systems on the map ---------------- */
(function(){
  var cv=$('wcv');if(!cv)return;var cx=cv.getContext('2d');
  var bb=X.bbox,bw=bb[2]-bb[0]+14,bh=bb[3]-bb[1]+14,W0=1100,H0=Math.round(W0*bh/bw),ox=bb[0]-7,oy=bb[1]-7,sc=W0/bw;cv.width=W0;cv.height=H0;
  var mode='old',focus='',f=0,playing=false,raf=0,t0=0,f0=0,dur=15000;
  function trace(c,l){c.beginPath();l.poly.forEach(function(q,i){var x=(q[0]-ox)*sc,y=(q[1]-oy)*sc;if(i)c.lineTo(x,y);else c.moveTo(x,y)});c.closePath()}
  function numOf(l){var m=/\d+/.exec(l);return m?+m[0]:0}
  function sufOf(l){return l.replace(/^[A-Z]?\d+/,'')}
  /* the old order inside one section: label number ascending, a suffix after its plain lot (13, 13A, 13B, 13H) */
  var ORD={};SEC.forEach(function(s){ORD[s]=LOTS.filter(function(l){return l.s===s}).sort(function(a,b){return numOf(a.l)-numOf(b.l)||sufOf(a.l).localeCompare(sufOf(b.l))})});
  var SECS=SEC.filter(function(s){return ORD[s].length});
  var HUE={A:28,B:210,C:140,D:300,E:48,F:0,G:185,H:255,I:88,J:12,K:330,L:165,M:230};
  function scol2(s,t){return 'hsl('+HUE[s]+',62%,'+(isDark()?(34+t*30):(74-t*38)).toFixed(0)+'%)'}
  function hcol(t){return 'hsl('+(50-34*t).toFixed(0)+',82%,'+(isDark()?58:46)+'%)'}
  var base=document.createElement('canvas'),lay=document.createElement('canvas');base.width=lay.width=W0;base.height=lay.height=H0;
  var ptr={},hptr=0;
  function drawBase(){var c=base.getContext('2d');c.clearRect(0,0,W0,H0);c.fillStyle=css('--g3');LOTS.forEach(function(l){trace(c,l);c.fill()})}
  function reset(){lay.getContext('2d').clearRect(0,0,W0,H0);ptr={};hptr=0;SECS.forEach(function(s){ptr[s]=0})}
  function targetIdx(s){var n=ORD[s].length;return Math.max(0,Math.min(n,Math.ceil(f*n)))}
  function paintTo(){
    var c=lay.getContext('2d');
    if(mode==='old'){var back=false;SECS.forEach(function(s){if(targetIdx(s)<ptr[s])back=true});if(back)reset();
      SECS.forEach(function(s){var n=ORD[s].length,tg=targetIdx(s);if(focus&&s!==focus)return;for(;ptr[s]<tg;ptr[s]++){c.fillStyle=scol2(s,ptr[s]/Math.max(1,n-1));trace(c,ORD[s][ptr[s]]);c.fill()}})}
    else{var tg=Math.max(0,Math.min(LOTS.length,Math.ceil(f*LOTS.length)));if(tg<hptr)reset();for(;hptr<tg;hptr++){c.fillStyle=hcol(hptr/(LOTS.length-1));trace(c,LOTS[hptr]);c.fill()}}
  }
  function head(c,l,col,r){var x=(l.cx-ox)*sc,y=(l.cy-oy)*sc;c.fillStyle=col;c.strokeStyle=isDark()?'#f4f2ec':'#0b0b0a';c.lineWidth=3;c.beginPath();c.arc(x,y,r,0,7);c.fill();c.stroke()}
  function tail(c,arr,i,col){var a=Math.max(0,i-45);c.strokeStyle=col;c.lineWidth=2.6;c.lineJoin='round';c.lineCap='round';c.beginPath();for(var k=a;k<=i;k++){var l=arr[k],x=(l.cx-ox)*sc,y=(l.cy-oy)*sc;if(k===a)c.moveTo(x,y);else c.lineTo(x,y)}c.stroke()}
  var side=$('wside');
  function draw(){
    paintTo();cx.clearRect(0,0,W0,H0);cx.drawImage(base,0,0);cx.drawImage(lay,0,0);
    if(mode==='old'){
      var h='';SECS.forEach(function(s){if(focus&&s!==focus)return;var arr=ORD[s],n=arr.length,i=Math.max(0,Math.min(n-1,targetIdx(s)-1)),l=arr[i];
        tail(cx,arr,i,'rgba('+(isDark()?'244,242,236':'11,11,10')+',.45)');head(cx,l,'hsl('+HUE[s]+',70%,52%)',9);
        cx.font='700 17px "IBM Plex Mono",monospace';cx.textAlign='center';cx.fillStyle=isDark()?'#f4f2ec':'#0b0b0a';cx.strokeStyle=isDark()?'#0b0b0a':'#fff';cx.lineWidth=4;cx.strokeText(s,(l.cx-ox)*sc,(l.cy-oy)*sc-16);cx.fillText(s,(l.cx-ox)*sc,(l.cy-oy)*sc-16)});
      SECS.forEach(function(s){var arr=ORD[s],n=arr.length,k=targetIdx(s),i=Math.max(0,Math.min(n-1,k-1)),l=arr[i];
        h+='<div class="wrow'+(focus&&s!==focus?' dim':'')+'"><b style="background:hsl('+HUE[s]+',55%,42%)">'+s+'</b><div><div class="bar2"><i style="width:'+(100*k/n).toFixed(1)+'%;background:hsl('+HUE[s]+',62%,50%)"></i></div><span class="lbl" title="first lot '+esc(arr[0].l)+', last lot '+esc(arr[n-1].l)+'">at <b>'+s+'-'+esc(l.l)+'</b></span></div><span class="pos">'+k+' / '+n+'</span></div>'});
      side.innerHTML='<div class="whs"><b>'+(focus?'Section '+focus:'All 13 sections at once')+'.</b> Each section counts from its own first label, so they walk in different directions at the same time. Dark means near the end.</div>'+h;
    }else{
      var i2=Math.max(0,Math.min(LOTS.length-1,Math.ceil(f*LOTS.length)-1)),l2=LOTS[i2];tail(cx,LOTS,i2,'rgba('+(isDark()?'244,242,236':'11,11,10')+',.5)');head(cx,l2,'#c5a448',11);
      var pp=PASSES.filter(function(q){return l2.h>=q.lo&&l2.h<=q.hi})[0];
      side.innerHTML='<div class="whs">One walker. One direction. Every step adds one.</div><div class="whb">'+pad(l2.h)+'</div><div class="whs">Pass <b>'+(pp?pp.n:'')+'</b> of 6 · sections '+(pp?esc(pp.secs):'')+'</div><div class="wpass">'+PASSES.map(function(q){return '<i'+(q.n===(pp&&pp.n)?' class="on"':'')+'></i>'}).join('')+'</div><div class="whs" style="margin-top:14px">The old label on this lot is <b>'+l2.s+'-'+esc(l2.l)+'</b>. Along the path it jumps around; the H-number never does.</div>';
      set3d(l2.h);
    }
    $('wscrub').value=Math.round(f*1000);
  }
  function setMode(m){mode=m;focus='';reset();[].forEach.call(document.querySelectorAll('[data-wm]'),function(b){b.classList.toggle('on',b.getAttribute('data-wm')===m)});
    $('wcap').textContent=m==='old'?'The old way. A is numbered on its own, B on its own, and so on. Every section starts again at its own first lot, so the walkers run side by side and never agree.':'The H-number way. One path through every lot, in one fixed order. The first lot is H000001, the next is H000002, all the way to H003185.';
    $('wfocus').style.display=m==='old'?'flex':'none';
    $('wkey').innerHTML=m==='old'?'<span><i style="background:linear-gradient(90deg,hsl(210,62%,74%),hsl(210,62%,36%))"></i>start → end of one section (each section has its own colour)</span>':'<span><i style="background:linear-gradient(90deg,'+hcol(0)+','+hcol(.5)+','+hcol(1)+')"></i>H000001 → H003185</span>';
    buildFocus();draw()}
  function buildFocus(){var w=$('wfocus');w.innerHTML='<span class="note" style="align-self:center;margin:0 6px 0 0">Show only</span>'+['All'].concat(SECS).map(function(s){return '<button class="chip" type="button" data-f="'+(s==='All'?'':s)+'" aria-pressed="'+((s==='All'?'':s)===focus)+'">'+(s==='All'?'All sections':s)+'</button>'}).join('');
    [].forEach.call(w.querySelectorAll('[data-f]'),function(b){on(b,'click',function(){focus=b.getAttribute('data-f');reset();buildFocus();draw()})})}
  var B3=location.pathname.indexOf('/math/')>=0?'../site/3d.html':'3d.html';
  function set3d(h){var g=$('w3dgo');if(!g)return;g.href=B3+'#h='+h;g.textContent='Fly to H'+String(h).padStart(6,'0')+' in 3D'}
  $('w3dall').href=B3+'#walk';$('w3dp').innerHTML=[1,2,3,4,5,6].map(function(n){return '<a class="btn" style="text-decoration:none" href="'+B3+'#walk='+n+'">Walk pass '+n+'</a>'}).join('');
  function tick(now){var e=f0+(now-t0)/dur;if(e>=1){f=1;stop();draw();return}f=e;draw();raf=requestAnimationFrame(tick)}
  function stop(){playing=false;if(raf)cancelAnimationFrame(raf);raf=0;$('wplay').textContent=f>=1?'Replay':'Play'}
  function play(){if(f>=1){f=0;reset()}playing=true;f0=f;t0=performance.now();$('wplay').textContent='Pause';raf=requestAnimationFrame(tick)}
  on($('wplay'),'click',function(){if(playing){stop()}else play()});
  on($('wscrub'),'input',function(){if(playing)stop();f=+$('wscrub').value/1000;draw()});
  on($('wspeed'),'input',function(){dur=+$('wspeed').value;if(playing){f0=f;t0=performance.now()}});
  [].forEach.call(document.querySelectorAll('[data-wm]'),function(b){on(b,'click',function(){if(playing)stop();f=0;setMode(b.getAttribute('data-wm'))})});
  drawBase();reset();redraws.push(function(){drawBase();reset();draw()});
  window.addEventListener('beforeprint',function(){if(playing)stop();f=1;drawBase();reset();draw()});
  var started=false;if('IntersectionObserver' in window){new IntersectionObserver(function(es){if(es[0].isIntersecting&&!started){started=true;if(!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches))play()}},{threshold:.35}).observe(cv)}
  setMode('old');f=.0;draw();
})();

/* ---------------- hero: the same cemetery twice, once by old number and once by H-number ---------------- */
(function(){
  var cvO=$('h2old'),cvN=$('h2new');if(!cvO||!cvN)return;
  var bb=X.bbox,bw=bb[2]-bb[0]+14,bh=bb[3]-bb[1]+14,W0=900,H0=Math.round(W0*bh/bw),ox=bb[0]-7,oy=bb[1]-7,sc=W0/bw,N=LOTS.length;
  [cvO,cvN].forEach(function(c){c.width=W0;c.height=H0});
  function trace(cx,l){cx.beginPath();l.poly.forEach(function(q,i){var x=(q[0]-ox)*sc,y=(q[1]-oy)*sc;if(i)cx.lineTo(x,y);else cx.moveTo(x,y)});cx.closePath()}
  function numOf(l){return parseInt(l.l.replace(/[^0-9]/g,''),10)||0}
  function drawOld(){var cx=cvO.getContext('2d');cx.clearRect(0,0,W0,H0);LOTS.forEach(function(l){var n=numOf(l);cx.fillStyle='hsl('+((n*47)%360)+',56%,'+(isDark()?44+(n*13)%12:52+(n*13)%16)+'%)';trace(cx,l);cx.fill()})}
  var base=document.createElement('canvas'),paint=document.createElement('canvas');base.width=paint.width=W0;base.height=paint.height=H0;
  function drawBase(){var cx=base.getContext('2d');cx.clearRect(0,0,W0,H0);cx.fillStyle=css('--g3');LOTS.forEach(function(l){trace(cx,l);cx.fill()})}
  function ramp(t){return 'hsl('+(50-34*t).toFixed(0)+',82%,'+(isDark()?58:46)+'%)'}
  var pi=0,t0=0,raf=0,fr=0,DUR=12000,reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function advance(to){var cx=paint.getContext('2d');for(;pi<to;pi++){cx.fillStyle=ramp(pi/(N-1));trace(cx,LOTS[pi]);cx.fill()}}
  function repaint(){var keep=pi;paint.getContext('2d').clearRect(0,0,W0,H0);pi=0;advance(keep)}
  function show(){var cx=cvN.getContext('2d');cx.clearRect(0,0,W0,H0);cx.drawImage(base,0,0);cx.drawImage(paint,0,0);
    var i=Math.max(0,Math.min(N-1,pi-1)),l=LOTS[i];
    cx.lineJoin='round';cx.lineCap='round';cx.strokeStyle=isDark()?'#f4f2ec':'#0b0b0a';cx.lineWidth=2.4;cx.globalAlpha=.55;cx.beginPath();for(var k=Math.max(0,i-60);k<=i;k++){var q=LOTS[k],x=(q.cx-ox)*sc,y=(q.cy-oy)*sc;if(k===Math.max(0,i-60))cx.moveTo(x,y);else cx.lineTo(x,y)}cx.stroke();cx.globalAlpha=1;
    var hx=(l.cx-ox)*sc,hy=(l.cy-oy)*sc;cx.fillStyle='#c5a448';cx.strokeStyle='#0b0b0a';cx.lineWidth=3;cx.beginPath();cx.arc(hx,hy,11,0,7);cx.fill();cx.stroke();
    $('h2big').innerHTML=pad(l.h)+'<small>of 3,185</small>';var p=PASSES.filter(function(q){return l.h>=q.lo&&l.h<=q.hi})[0];$('h2pass').textContent=p?'Pass '+p.n+' of 6 · sections '+p.secs.replace(/ margins;?/,'')+'':'';
    if(fr++%5===0||pi>=N){var h='';for(var k2=Math.max(0,i-5);k2<=i;k2++)h+='<span>'+LOTS[k2].s+'-'+esc(LOTS[k2].l)+'</span>';$('h2oldlab').innerHTML=h}}
  function tick(now){var f=Math.min(1,(now-t0)/DUR),e=f<.5?2*f*f:1-Math.pow(-2*f+2,2)/2;advance(Math.max(pi,Math.floor(e*N)));if(f>=1)advance(N);show();if(f<1)raf=requestAnimationFrame(tick);else raf=0;$('h2play').textContent='Replay'}
  function play(){if(raf)cancelAnimationFrame(raf);paint.getContext('2d').clearRect(0,0,W0,H0);pi=0;fr=0;if(reduce){advance(N);show();return}t0=performance.now();$('h2play').textContent='Restart';raf=requestAnimationFrame(tick)}
  drawOld();drawBase();on($('h2play'),'click',play);
  window.addEventListener('beforeprint',function(){if(raf)cancelAnimationFrame(raf);advance(N);drawOld();drawBase();repaint();show()});
  redraws.push(function(){drawOld();drawBase();repaint();show()});
  var started=false;function maybe(){if(started)return;var r=cvN.getBoundingClientRect();if(r.top<innerHeight&&r.bottom>0){started=true;play()}}
  if('IntersectionObserver' in window){new IntersectionObserver(function(es){if(es[0].isIntersecting)maybe()},{threshold:.2}).observe(cvN)}else play();
  advance(0);show();
})();

/* data inconsistencies: seven problems, each with a picture of what goes wrong */
(function(){
  var oth=A.B_grid_labels_shadowed_by_margin||[],hmax=Math.max.apply(null,FWD.filter(function(r){return r[0]==='H'}).map(function(r){return r[2]}));
  var cell=function(t,c){return '<span class="dc '+(c||'')+'">'+t+'</span>'};
  /* 1 labels claimed twice */
  function v1(){var lo=oth[0]||373,hi=oth[oth.length-1]||379,a=372,b=395,pc=function(n){return ((n-a)/(b-a)*100).toFixed(2)+'%'};
    function bar(x0,x1,cls,txt){return '<div class="rb '+cls+'" style="left:'+pc(x0)+';width:calc('+pc(x1+1)+' - '+pc(x0)+')"><span>'+txt+'</span></div>'}
    return '<div class="rng"><b>Grid rule</b><div class="rt">'+bar(lo,hi,'g','labels '+lo+' to '+hi)+'</div><b>Margin list</b><div class="rt">'+bar(373,394,'m','labels 373 to 394')+'</div><div class="rt ov"><div class="rb clash" style="left:'+pc(lo)+';width:calc('+pc(hi+1)+' - '+pc(lo)+')"><span>claimed twice</span></div></div></div><p class="dcap"><i class="sw clash"></i>'+oth.length+' labels ('+lo+' to '+hi+') appear in both lists</p>'}
  /* 2 positions without a label */
  function v2(){var n=3185,w=1000,t='';X.missingH.forEach(function(h){t+='<rect x="'+(h/n*w).toFixed(1)+'" y="8" width="3" height="34" rx="1.5" fill="var(--bad)"/>'});
    PASSES.forEach(function(p){t+='<rect x="'+(p.lo/n*w).toFixed(1)+'" y="46" width="'+((p.hi-p.lo+1)/n*w-2).toFixed(1)+'" height="10" rx="5" fill="var(--g3)"/><text x="'+((p.lo+p.hi)/2/n*w).toFixed(1)+'" y="78" text-anchor="middle" font-size="22" fill="var(--g5)" font-family="IBM Plex Mono,monospace">'+p.n+'</text>'});
    return '<svg viewBox="0 0 1000 86" class="dsvg" role="img" aria-label="Positions along the path with no old label">'+t+'</svg><p class="dcap"><i class="sw bad"></i>each red mark is a position on the path (H000001 to H003185) with no old label, '+X.missingH.length+' in all</p>'}
  /* 3 duplicate keys */
  function v3(){return '<div class="dl"><b>Section G, row 1</b><div class="dr">'+cell('17')+cell('18')+cell('19','clash on')+cell('19','clash on')+cell('20')+cell('19H?','ghost')+'</div></div><div class="dl"><b>Section D table</b><div class="dr">'+cell('273')+cell('274','clash on')+cell('274','clash on')+cell('275')+'</div></div><p class="dcap"><i class="sw clash"></i>two lots answer to one label, so the software can only reach one of them</p>'}
  /* 4 typo */
  function v4(){return '<div class="dl"><b>Pattern says</b><div class="dr">'+cell('143')+cell('142')+cell('142H','on g')+cell('141')+'</div></div><div class="dl"><b>Table says</b><div class="dr">'+cell('143')+cell('142')+cell('124H','clash on')+cell('141')+'</div></div><p class="dcap"><i class="sw clash"></i>two digits swapped in row 8 of Section C</p>'}
  /* 5 documents vs code */
  function grid(order){var b='',a='';order.B.forEach(function(n,i){b+=cell(n,'g on'+(n!==i+1?' clash':''))});order.A.forEach(function(n,i){a+=cell(n,'m on'+(n!==i+4?' clash':''))});return '<div class="dr"><span class="dsec">B</span>'+b+'</div><div class="dr"><span class="dsec">A</span>'+a+'</div>'}
  function v5(){return '<div class="dtwo"><div><b>The document says: alternate</b>'+grid({B:[1,3,5],A:[2,4,6]})+'</div><div><b>The code does: all of B, then all of A</b>'+grid({B:[1,2,3],A:[4,5,6]})+'</div></div><p class="dcap"><i class="sw clash"></i>the numbers in red land on different lots depending on which order is right</p>'}
  /* 6 idealised grid */
  function v6(){return '<div class="dl"><b>Reference sheet</b><div class="dbar"><i style="width:'+(1672/1871*100)+'%"></i><span>C-417 = H001672</span></div></div><div class="dl"><b>Real decoder</b><div class="dbar real"><i style="width:100%"></i><span>C-417 = H001871</span></div></div><p class="dcap"><i class="sw clash"></i>the sheet is 199 lots short, because it assumes every row has 22 lots</p>'}
  /* 7 H / M boundary */
  function v7(){var m=FW['M|11']||2587;return '<div class="dl"><b>What the data says</b><div class="dr"><span class="dsec">H</span>'+cell('ends '+pad(hmax),'g on')+cell('M starts '+pad(m),'m on')+'</div></div><div class="dl"><b>What older notes said</b><div class="dr">'+cell('M starts '+pad(m-1),'clash on')+'</div></div><p class="dcap"><i class="sw clash"></i>one position off, so the last lot of H lands in the wrong pass</p>'}
  var d=[
   {sec:'B',open:1,t:'Two lists use the same labels',v:v1(),w:'Section B counts its grid and its margin with overlapping numbers. B-373 means a lot in the margin, not the grid.',n:'Which lot does each of these '+oth.length+' labels belong to?'},
   {sec:'B, A',open:1,t:'Positions with no old label',v:v2(),w:X.missingH.length+' places on the path have no old label. They can only be found by H-number or by counting on the ground.',n:'Does a real lot stand at each of these positions?'},
   {sec:'D, G',open:1,t:'One label, two lots',v:v3(),w:'Two entries in the old tables share a label, so one lot can never be looked up.',n:'Which lot did each entry mean?'},
   {sec:'C',open:1,t:'A typo in a row table',v:v4(),w:'Row 8 lists 124H where the pattern needs 142H. A search for 142H finds nothing.',n:'Is the lot on the map really 142H?'},
   {sec:'B, A',open:1,t:'The paper and the code disagree',v:v5(),w:'The reference PDF alternates B and A column by column. The code does a whole level of B first. Every H-number after the first lot depends on this.',n:'Which order is the official one?'},
   {sec:'C',open:0,t:'The idealised grid is wrong',v:v6(),w:'The reference sheet assumes 22 lots in every row. Real rows vary. The decoder already uses the real rows.',n:'Retire or correct the old sheet.'},
   {sec:'H, M',open:0,t:'Where H ends and M begins',v:v7(),w:'Section H ends at '+pad(hmax)+' and M starts at '+pad(FW['M|11'])+'. Earlier summaries quoted M at H002586.',n:'Check any document that quotes the old boundary.'}];
  var no=d.filter(function(x){return x.open}).length;
  $('defects').innerHTML='<div class="dsum"><span><b>'+d.length+'</b> problems found</span><span class="o"><b>'+no+'</b> need a decision</span><span class="r"><b>'+(d.length-no)+'</b> handled</span><span class="dfil"><button class="chip" data-df="" aria-pressed="true" type="button">All</button><button class="chip" data-df="1" aria-pressed="false" type="button">Need a decision</button><button class="chip" data-df="0" aria-pressed="false" type="button">Handled</button></span></div><div class="defgrid">'+d.map(function(x){return '<article class="defc" data-o="'+x.open+'"><div class="dh"><span class="pill '+(x.open?'open':'done')+'">'+(x.open?'Needs a decision':'Handled')+'</span><span class="tag bad">Section '+x.sec+'</span></div><h4>'+x.t+'</h4><div class="defv">'+x.v+'</div><p class="dw">'+x.w+'</p><p class="dn"><b>'+(x.open?'We need to know:':'Still to do:')+'</b> '+x.n+'</p></article>'}).join('')+'</div>';
  [].forEach.call($('defects').querySelectorAll('[data-df]'),function(b){on(b,'click',function(){var v=b.getAttribute('data-df');[].forEach.call($('defects').querySelectorAll('[data-df]'),function(x){x.setAttribute('aria-pressed',x===b)});[].forEach.call($('defects').querySelectorAll('.defc'),function(c){c.style.display=(v===''||c.getAttribute('data-o')===v)?'':'none'})})});
})();
