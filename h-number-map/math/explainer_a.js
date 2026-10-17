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
var redraws=[];function redrawAll(){redraws.forEach(function(f){try{f()}catch(e){}})}
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
  var root=document.documentElement,TH=['auto','light','dark'],ti=0;
  try{var s=localStorage.getItem('cg-theme');if(s&&TH.indexOf(s)>=0)ti=TH.indexOf(s)}catch(e){}
  function applyTheme(){var v=TH[ti];if(v==='auto')root.removeAttribute('data-theme');else root.setAttribute('data-theme',v);$('btheme').textContent='Theme: '+v;try{localStorage.setItem('cg-theme',v)}catch(e){}setTimeout(redrawAll,30)}
  on($('btheme'),'click',function(){ti=(ti+1)%3;applyTheme()});applyTheme();
  if(window.matchMedia)window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',function(){setTimeout(redrawAll,30)});
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

/* ---------------- walk the path, on the map from above ---------------- */
(function(){
  var NS='http://www.w3.org/2000/svg',cmode='n',playing=false,posF=0,seq=[],raf=0,lastT=0,speed=6;
  var ctl=$('walkctl');
  ctl.innerHTML='<div><label class="f">Color lots by</label><button class="btn seg on" data-c="n" type="button">Old label number</button><button class="btn seg" data-c="h" type="button">H-number</button></div>'
   +'<div><label class="f" for="wspeed">Walking speed</label><select id="wspeed" style="width:auto"><option value="3">Slow (3 lots/s)</option><option value="6" selected>Normal (6 lots/s)</option><option value="14">Fast (14 lots/s)</option></select></div>'
   +'<div><button class="btn fill" id="wplay" type="button">Walk the path</button> <button class="btn" id="wreset" type="button">Reset</button></div>';
  var svg=$('wmap'),polys=[],gW=document.createElementNS(NS,'g'),gT=document.createElementNS(NS,'g');
  var base=document.createElementNS(NS,'g');svg.appendChild(base);svg.appendChild(gW);svg.appendChild(gT);
  LOTS.forEach(function(l){var p=document.createElementNS(NS,'polygon');p.setAttribute('points',l.poly.map(function(q){return q.join(',')}).join(' '));p._l=l;base.appendChild(p);polys.push(p)});
  function num(l){return parseInt(l.replace(/[^0-9]/g,''),10)||0}
  function lotColor(l,st,wd,visited){if(cmode==='h')return 'hsl('+Math.round(240-240*(l.h-st)/Math.max(1,wd-1))+',68%,'+(visited?62:50)+'%)';var n=num(l.l);return 'hsl('+((n*47)%360)+',62%,'+(visited?(isDark()?42:66):(40+(n*13)%25))+'%)'}
  var B3=location.pathname.indexOf('/math/')>=0?'../site/3d.html':'3d.html';
  function set3d(st){$('w3dgo').href=B3+'#h='+st;$('w3dgo').textContent='Fly to H'+String(st).padStart(6,'0')+' in 3D';$('w3dall').href=B3+'#walk'}
  $('w3dp').innerHTML=[1,2,3,4,5,6].map(function(n){return '<a class="btn" style="text-decoration:none" href="'+B3+'#walk='+n+'">Walk pass '+n+'</a>'}).join('');
  function rebuild(){
    var st=+$('sawstart').value,wd=+$('sawwidth').value;$('sawstartv').textContent=st;$('sawwidthv').textContent=wd;
    seq=LOTS.filter(function(l){return l.h>=st&&l.h<st+wd});set3d(st);var mp=Math.max(0,seq.length-1);$('walkpos').max=mp;if(posF>mp)posF=mp;$('walkpos').value=Math.round(posF);
    var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;(seq.length?seq:LOTS).forEach(function(l){l.poly.forEach(function(q){if(q[0]<x0)x0=q[0];if(q[0]>x1)x1=q[0];if(q[1]<y0)y0=q[1];if(q[1]>y1)y1=q[1]})});
    svg.style.cssText='display:block;width:100%;height:min(66vh,620px)';var asp=(svg.clientWidth||1000)/(svg.clientHeight||520),w=Math.max(x1-x0+30,90*asp),h=Math.max(y1-y0+30,90),mx=(x0+x1)/2,my=(y0+y1)/2;if(w/h<asp)w=h*asp;else h=w/asp;
    svg.setAttribute('viewBox',(mx-w/2)+' '+(my-h/2)+' '+w+' '+h);
    var inW={};seq.forEach(function(l,i){inW[l.h]=i});
    polys.forEach(function(p){var l=p._l,i=inW[l.h];p._i=i;p.setAttribute('fill',i==null?css('--g3'):lotColor(l,st,wd,false));p.setAttribute('opacity',i==null?'.5':'1')});
    gW.innerHTML='';
    if(seq.length&&seq.length<=160){var fs=Math.max(2.2,Math.min(5,w/60));seq.forEach(function(l){var t=document.createElementNS(NS,'text');t.setAttribute('x',l.cx);t.setAttribute('y',l.cy);t.setAttribute('text-anchor','middle');t.setAttribute('style','font:600 '+fs+'px var(--mono);fill:#0b0b0a;pointer-events:none;paint-order:stroke;stroke:#fff;stroke-width:'+fs*0.28+'px');t.innerHTML='<tspan x="'+l.cx+'" dy="-0.15em">'+esc(l.l)+'</tspan><tspan x="'+l.cx+'" dy="1.05em" style="font-size:'+fs*0.78+'px;font-weight:500">'+l.h+'</tspan>';gW.appendChild(t)})}
    update();
  }
  function cpos(f){var i=Math.floor(f),a=seq[i],b=seq[Math.min(i+1,seq.length-1)];if(!a)return null;var t=f-i;return {x:a.cx+(b.cx-a.cx)*t,y:a.cy+(b.cy-a.cy)*t}}
  function update(){
    var st=+$('sawstart').value,wd=+$('sawwidth').value,i=Math.floor(posF),cur=seq[i];$('walkposv').textContent=(seq.length?Math.round(posF)+1:0)+' of '+seq.length;
    gT.innerHTML='';var cp=cpos(posF);
    if(cp){var vb=svg.getAttribute('viewBox').split(' '),u=+vb[2]/560,pts=[];for(var k=0;k<=i;k++)pts.push(seq[k].cx+','+seq[k].cy);pts.push(cp.x+','+cp.y);var pl=document.createElementNS(NS,'polyline');pl.setAttribute('points',pts.join(' '));pl.setAttribute('fill','none');pl.setAttribute('stroke','#0b0b0a');pl.setAttribute('stroke-width',u*.9);pl.setAttribute('stroke-opacity','.75');pl.setAttribute('stroke-linejoin','round');pl.setAttribute('stroke-linecap','round');gT.appendChild(pl);
      var c=document.createElementNS(NS,'circle');c.setAttribute('cx',cp.x);c.setAttribute('cy',cp.y);c.setAttribute('r',u*3.2);c.setAttribute('fill','#c5a448');c.setAttribute('stroke','#0b0b0a');c.setAttribute('stroke-width',u*.9);gT.appendChild(c)}
    polys.forEach(function(p){if(p._i!=null)p.setAttribute('fill',lotColor(p._l,st,wd,p._i<i))});
    var o=$('wnow');
    if(!cur){o.innerHTML='No lots with outlines in this range. Move the start.';$('wstrip').innerHTML=''}
    else{o.innerHTML='You are at <b>'+cur.s+'-'+esc(cur.l)+'</b>, which is <b>'+pad(cur.h)+'</b>. Lot '+(i+1)+' of '+seq.length+' in this walk. The old label on the lot jumps around. The H-number goes up by one each step.';
      var s='';for(var j=i;j<Math.min(seq.length,i+9);j++)s+='<div class="c'+(j===i?' cur':'')+'">'+seq[j].s+'-'+esc(seq[j].l)+'<small>'+pad(seq[j].h)+'</small></div>';$('wstrip').innerHTML=s}
  }
  [].forEach.call(ctl.querySelectorAll('[data-c]'),function(b){on(b,'click',function(){cmode=b.getAttribute('data-c');[].forEach.call(ctl.querySelectorAll('[data-c]'),function(x){x.classList.toggle('on',x===b)});update()})});
  function stop(){playing=false;if(raf)cancelAnimationFrame(raf);raf=0;var b=$('wplay');b.classList.remove('on');b.textContent='Walk the path'}
  function tick(t){if(!playing)return;var dt=Math.min(.1,(t-lastT)/1000);lastT=t;posF+=speed*dt;if(posF>=seq.length-1){posF=seq.length-1;stop();$('walkpos').value=Math.round(posF);update();return}$('walkpos').value=Math.round(posF);update();raf=requestAnimationFrame(tick)}
  on($('wplay'),'click',function(){if(playing){stop();return}if(posF>=seq.length-1)posF=0;playing=true;var b=$('wplay');b.classList.add('on');b.textContent='Pause';lastT=performance.now();raf=requestAnimationFrame(tick)});
  on($('wreset'),'click',function(){stop();$('sawstart').value=1;$('sawwidth').value=60;posF=0;rebuild();toast('Walk reset')});
  on($('wspeed'),'input',function(){speed=+$('wspeed').value});
  on($('walkpos'),'input',function(){posF=+$('walkpos').value;update()});
  on($('sawstart'),'input',function(){stop();rebuild()});on($('sawwidth'),'input',function(){stop();rebuild()});
  redraws.push(function(){rebuild()});
  rebuild();
})();

/* ---------------- hero illustration: a path that numbers twelve stones ---------------- */
(function(){
  var host=$('heroart');if(!host)return;var NS='http://www.w3.org/2000/svg',Wd=1000,Hh=330;
  var st=[],N=3,R=2,cw=84,ch=88;
  for(var r=0;r<R;r++)['B','A'].forEach(function(s){for(var c=0;c<N;c++){var x0=s==='B'?130:560;st.push({x:x0+c*cw,y:96+r*(ch+28)})}});
  var pts=st.map(function(p){return [p.x+27,p.y+56]});
  function smooth(p){var d='M'+p[0][0]+' '+p[0][1];for(var i=0;i<p.length-1;i++){var a=p[i-1]||p[i],b=p[i],c=p[i+1],e=p[i+2]||c;d+=' C'+(b[0]+(c[0]-a[0])/6)+' '+(b[1]+(c[1]-a[1])/6)+' '+(c[0]-(e[0]-b[0])/6)+' '+(c[1]-(e[1]-b[1])/6)+' '+c[0]+' '+c[1]}return d}
  var h='<svg viewBox="0 0 '+Wd+' '+Hh+'" xmlns="http://www.w3.org/2000/svg">'
   +'<circle class="hart-sun" cx="880" cy="70" r="38"/>'
   +'<path class="hart-hill2" d="M0 262 C150 204 300 232 460 247 S780 212 1000 237 V330 H0Z"/>'
   +'<path class="hart-hill1" d="M0 292 C170 246 330 288 520 276 S850 256 1000 282 V330 H0Z"/>';
  [[70,226,30,70],[960,224,26,62],[470,246,22,48]].forEach(function(t){h+='<ellipse class="hart-tree" cx="'+t[0]+'" cy="'+t[1]+'" rx="'+t[2]+'" ry="'+t[3]+'"/>'});
  h+='<text class="hart-label" x="'+(130+cw)+'" y="84">Section B</text><text class="hart-label" x="'+(560+cw)+'" y="84">Section A</text>';
  st.forEach(function(p){h+='<path class="hart-stone" d="M'+p.x+' '+(p.y+62)+' V'+(p.y+24)+' a27 24 0 0 1 54 0 V'+(p.y+62)+' Z"/>'});
  h+='<path class="hart-path" id="hartpath" d="'+smooth(pts)+'"/>';
  st.forEach(function(p,i){h+='<text class="hart-num" x="'+(p.x+27)+'" y="'+(p.y+46)+'" style="animation-delay:'+(0.25+i*0.42).toFixed(2)+'s">'+(i+1)+'</text>'});
  h+='</svg><button class="btn sm replay" type="button" id="hartreplay">Replay</button>';
  host.innerHTML=h;
  var path=$('hartpath');try{var L=path.getTotalLength();host.style.setProperty('--len',Math.ceil(L)+2);path.style.strokeDasharray=Math.ceil(L)+2;path.style.strokeDashoffset=Math.ceil(L)+2}catch(e){}
  function go(){host.classList.remove('go','static');void host.offsetWidth;host.classList.add('go')}
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduce)host.classList.add('static');else go();
  on($('hartreplay'),'click',function(){host.classList.remove('static');go()});
})();

/* defects */
(function(){
  var oth=A.B_grid_labels_shadowed_by_margin||[],hmax=Math.max.apply(null,FWD.filter(function(r){return r[0]==='H'}).map(function(r){return r[2]}));
  var d=[['B','Labels claimed twice','Section B\'s grid rule and its margin list both use the labels '+oth[0]+' to '+oth[oth.length-1]+'.','B-373 resolves to the margin position '+pad(FW['B|373'])+'.','The grid places that would carry these '+oth.length+' numbers have no label of their own.','The decoder lets the later rule win. Open: someone has to say which lot each label means.'],
   ['B, A','Positions with no old label','In the first sweep, 44 H-numbers have no legacy reference.','H000010, H000046 and H000055 are the first three.','These lots can only be found by H-number or by counting on the ground.','Listed in section 09. Open: a field check to see whether a physical lot sits at each position.'],
   ['D, G','Duplicate keys in the decoder tables','Section D lists 274 twice and Section G lists 19 twice in its first row.','G row 1 reads 19, 19 where one should be 19H.','One of each pair is shadowed, so one lot cannot be reached by its label.','The decoder keeps the later entry and the formula follows it. Open: decide which lot each entry meant.'],
   ['C','A typo in a row table','Row 8 of C lists "124H" where the pattern requires "142H".','C-142H '+(FW['C|142H']!=null?'is':'is not')+' in the decoder; C-124H is.','A lookup for the lot the pattern calls 142H fails. A lookup for 124H lands on that position.','The formula maps the typo to the intended position. Open: confirm on the map.'],
   ['B, A','The documents and the code disagree on the order','The reference PDF and decoder docstring say the sweep alternates B column 1, A column 1, and so on. The code visits a whole level of B, then the same level of A.','Under the document\'s order, A column 1 of level 1 would be H000002, not H000023.','Every H-number in B and A after the first lot would change (step 1 shows this).','All checks here follow the code. Open: choose the authoritative traversal order.'],
   ['C','The idealised grid is not the real grid','The reference sheet assumes 22 lots in every row.','It ends C-417 at H001672. The real rows give H001871.','Anyone using the sheet gets wrong numbers after the first uneven row.','Resolved in the decoder. The sheet should be retired or updated.'],
   ['H, M','Where H ends and M begins','Section H ends at '+pad(hmax)+' and M begins at '+pad(FW['M|11'])+'. Earlier summaries put M at H002586.','Pass 5 runs H002587 to H002835.','Quoting the older boundary puts the last lot of H and the first lot of M in the wrong passes.','Corrected on this page, which computes pass ranges from the data. Open: check any other document that quotes the boundary.']];
  $('defects').innerHTML=d.map(function(x){return '<div class="def"><span class="tag bad">Section '+x[0]+'</span> <b>'+x[1]+'</b><div class="f4"><div><em>Finding</em>'+x[2]+'</div><div><em>Example</em>'+x[3]+'</div><div><em>Consequence</em>'+x[4]+'</div><div><em>Status</em>'+x[5]+'</div></div></div>'}).join('');
})();
