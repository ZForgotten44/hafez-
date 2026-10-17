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

/* ---------------- presentation controls ---------------- */
(function(){
  var root=document.documentElement,TH=['auto','light','dark'],ti=0;
  try{var s=localStorage.getItem('cg-theme');if(s&&TH.indexOf(s)>=0)ti=TH.indexOf(s)}catch(e){}
  function applyTheme(){var v=TH[ti];if(v==='auto')root.removeAttribute('data-theme');else root.setAttribute('data-theme',v);$('btheme').textContent='Theme: '+v;try{localStorage.setItem('cg-theme',v)}catch(e){}setTimeout(redrawAll,30)}
  on($('btheme'),'click',function(){ti=(ti+1)%3;applyTheme()});applyTheme();
  if(window.matchMedia)window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',function(){setTimeout(redrawAll,30)});
  var lg=false;try{lg=localStorage.getItem('cg-size')==='lg'}catch(e){}
  function applySize(){if(lg)root.setAttribute('data-size','lg');else root.removeAttribute('data-size');$('bsize').setAttribute('aria-pressed',lg);$('bsize').textContent=lg?'A− Normal text':'A+ Large text';try{localStorage.setItem('cg-size',lg?'lg':'n')}catch(e){}}
  on($('bsize'),'click',function(){lg=!lg;applySize()});applySize();
  on($('bfs'),'click',function(){
    try{if(document.fullscreenElement){document.exitFullscreen()}else{var p=root.requestFullscreen();if(p&&p.catch)p.catch(function(){toast('Full screen is not available in this viewer')})}}catch(e){toast('Full screen is not available in this viewer')}});
  document.addEventListener('fullscreenchange',function(){$('bfs').textContent=document.fullscreenElement?'Exit full screen':'Full screen'});
  var ids=['raw','legacy','why','h','math','code','giant','compare','appendix'],els=ids.map($);
  function cur(){var y=window.scrollY+110,c=-1;els.forEach(function(s,i){if(s.offsetTop<=y)c=i});return c}
  function go(i){if(i<0){window.scrollTo({top:0});return}if(i>=els.length)return;els[i].scrollIntoView()}
  on($('bprev'),'click',function(){go(cur()-1)});on($('bnext'),'click',function(){go(cur()+1)});
  var links=document.querySelectorAll('#rail a');
  function mark(){var c=cur();[].forEach.call(links,function(a,i){a.classList.toggle('on',i===c)})}
  window.addEventListener('scroll',mark,{passive:true});mark();
  document.addEventListener('keydown',function(e){if(e.target&&/INPUT|TEXTAREA|SELECT/.test(e.target.tagName))return;if(e.key==='ArrowRight'&&e.altKey)go(cur()+1);if(e.key==='ArrowLeft'&&e.altKey)go(cur()-1)});
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
  s+=' H-number <span class="gold"><b>'+pad(H)+'</b></span>.';
  if(t){s+=' Derived by '+TIERTXT[t[2]]+'.';if(t[0]!=null)s+=' Level '+t[0]+', place '+t[1]+' in the decoder\'s indexing.'}
  var o=RV[H];if(o&&o.length>1)s+=' Shares this H-number with '+o.filter(function(x){return x!==S+'-'+L}).map(esc).join(', ')+'.';
  return s;
}
function chipBtn(S,L,kind,target,group){var b=document.createElement('button');b.type='button';b.className='chip '+(kind==='plain'?'':kind);b.textContent=L||'?';b.setAttribute('aria-pressed','false');
  on(b,'click',function(){[].forEach.call(group.querySelectorAll('.chip'),function(x){x.setAttribute('aria-pressed','false')});(group._pressed&&group._pressed!==b)&&group._pressed.setAttribute('aria-pressed','false');b.setAttribute('aria-pressed','true');group._pressed=b;target.innerHTML=describe(S,L)});return b}

/* ---------------- section 2 ---------------- */
(function(){
  $('nPoly').textContent=fmt(X.maplots.length);
  var parts=[['A','Section','The section letter, A to M. Required: the same label exists in other sections.'],['13','Lot label','The number written on the lot. It restarts in every section and its counting rule differs by section.'],['H','Suffix','A legacy H-lot: a lot whose label ends in H, sitting next to the lot with the same number. What the H originally stood for is not confirmed. It has nothing to do with the new H-number prefix, which only happens to use the same letter.']];
  var addr=$('addr');parts.forEach(function(p,i){var b=document.createElement('button');b.type='button';b.setAttribute('aria-pressed',i===0?'true':'false');b.innerHTML='<b>'+p[0]+'</b><span>'+p[1]+'</span>';
    on(b,'click',function(){[].forEach.call(addr.children,function(x){x.setAttribute('aria-pressed','false')});b.setAttribute('aria-pressed','true');$('addrdetail').innerHTML='<b>'+p[1]+' '+p[0]+'.</b> '+p[2]+(i===2?' Full address: <b>A-13H</b> = '+pad(FW['A|13H'])+'.':'')});addr.appendChild(b)});
  $('addrdetail').innerHTML='<b>Section A.</b> '+parts[0][2];
  var sg=$('sampleChips'),picks=[['A','13H'],['B','19A'],['B','384HA'],['C','51'],['C','12B'],['D','1H'],['D','F1'],['E','199BH'],['G','19'],['K','57'],['M','61'],['B','B362'],['D','384A']];
  picks.forEach(function(p){if(FW[p[0]+'|'+p[1]]!=null){var b=chipBtn(p[0],p[1],kindOf(p[1]),$('sampledetail'),sg);b.textContent=p[0]+'-'+p[1];sg.appendChild(b)}});
  var an=$('anatomy'),names={A:'Section A',B:'Section B',C:'Section C',D:'Section D',E:'Section E',F:'Section F',G:'Section G',H:'Section H',I:'Section I',J:'Section J',K:'Section K',L:'Section L',M:'Section M'};
  SEC.forEach(function(s){var rows=X.chips[s];if(!rows)return;var d=document.createElement('div');d.className='anat';d.innerHTML='<h5>'+names[s]+'<small>first two rows</small></h5>';var c=document.createElement('div');
    rows.forEach(function(row,ri){var g=document.createElement('div');g.className='chips';g.style.margin='0 0 6px';var l=document.createElement('span');l.className='note';l.style.cssText='flex:0 0 3.2em;padding-top:5px';l.textContent='row '+(ri+1);g.appendChild(l);
      row.forEach(function(cc){if(cc[0]==null){var x=document.createElement('span');x.className='chip gap static';x.textContent='gap';g.appendChild(x);return}g.appendChild(chipBtn(s,cc[0],cc[1],$('anatdetail'),an))});c.appendChild(g)});d.appendChild(c);an.appendChild(d)});
})();

/* ---------------- section 3 ---------------- */
(function(){
  var st=[[fmt(A.lots-2),'legacy references the decoder accepts'],[A.distinct_labels,'distinct label strings among them'],[A.labels_in_2plus_sections,'labels used by two or more sections'],[Math.round(100*A.lots_with_shared_label/A.lots)+'%','of references share their label string with another section'],[A.max_sections_per_label,'sections that each have a lot labelled "19"'],[A.unlabeled_positions.count,'positions in the first sweep with no label at all']];
  $('stats').innerHTML=st.map(function(s){return '<div class="stat"><div class="n">'+s[0]+'</div><div class="l">'+s[1]+'</div></div>'}).join('');
  var byL={};FWD.forEach(function(r){(byL[r[1].toUpperCase()]=byL[r[1].toUpperCase()]||[]).push(r)});
  function show(){var q=$('lbl').value.trim().toUpperCase(),r=byL[q]||[];if(!q){$('lblout').innerHTML='';return}
    if(!r.length){$('lblout').innerHTML='<p class="note">No section has a lot labelled "'+esc(q)+'".</p>';return}
    $('lblout').innerHTML='<p><b>'+r.length+'</b> lot'+(r.length>1?'s':'')+' labelled "'+esc(q)+'"'+(r.length>1?', one per section:':':')+'</p><div class="chips">'+r.map(function(x){return '<span class="chip static" style="border-left:4px solid '+scol(x[0])+'">'+x[0]+'-'+esc(x[1])+' → '+pad(x[2])+'</span>'}).join('')+'</div>'+(r.length>1?'<p class="note" style="margin-top:8px">Each is a different complete address. To use the label you must also know the section and that section\'s rule.</p>':'')}
  on($('lbl'),'input',show);
  var multi=Object.keys(byL).filter(function(k){return byL[k].length>=3});
  on($('lblr'),'click',function(){$('lbl').value=multi[Math.floor(Math.random()*multi.length)];show()});show();
  var rules=[['A','19 per row, counted right to left','H-lots slipped in before places 13, 5 and 1 of every row'],['B','20 per row in the body, last column steps by 19','Columns 2 and 3 both claim 19; "19A" is an extra; a 41-lot margin is numbered 373 to 394 with letters'],['C','Row tops go 19, 38 … 247, then 16 at a time, then 19','Twin pairs (51 and its H-lot) and A/B/C trios on eight rows'],['D','20 per row for rows 2 to 15, then blocks that run both ways','H-lots at 20(r−1) and 20r−11; row 1 uses letters; a 29-lot margin numbered 542 to 563'],['E','19 per row with twins at places 13, 9 and 5','Rows 9 to 12 change shape; lots 152, 169 and 190 to 199 carry A/B suffixes'],['F','18 per row','Eleven rows; a margin of 12 lots numbered 199 to 210'],['G','19 per row for lots 1 to 57','58 to 60 and 61 to 75 are added on; the label 19 appears twice in row 1'],['H','23 per row','Four rows only'],['I','1 to 64 straight','Just a counter'],['J','1 to 132 straight','Just a counter'],['K','115 lots in an order no formula gives','1, 2, 3, 6, 7, 8, 9, 13 … stored as a list'],['L','Starts at 69 and ends at 107','Numbers 1 to 68 do not exist here'],['M','82 to 279 straight','The first 51 lots are in an irregular order and stored as a list']];
  var V=A.verify.per_section;
  var h='<table class="t"><tr><th>Section</th><th>How its labels are built</th><th>Special cases</th><th>Decoder coverage</th></tr>';
  rules.forEach(function(r){var v=V[r[0]]||{},tot=0;Object.keys(v).forEach(function(k){tot+=v[k]});
    var bars=[['closed','#2f6b46','arithmetic'],['rows','#b8892f','row constants'],['list','#a23325','explicit list'],['errata','#8a3b8f','errata']].map(function(b){return v[b[0]]?'<i title="'+b[2]+': '+v[b[0]]+'" style="display:inline-block;height:10px;width:'+Math.max(3,Math.round(140*v[b[0]]/Math.max(tot,1)))+'px;background:'+b[1]+'"></i>':''}).join('');
    var txt=['closed','rows','list','errata'].filter(function(k){return v[k]}).map(function(k){return v[k]+' '+({closed:'arithmetic',rows:'row constants',list:'list',errata:'errata'})[k]}).join(', ');
    h+='<tr><td><b>'+r[0]+'</b></td><td>'+r[1]+'</td><td>'+r[2]+'</td><td style="white-space:nowrap">'+bars+'<div class="note">'+txt+'</div></td></tr>'});
  $('rules').innerHTML=h+'</table>';
})();

/* map */
(function(){
  var bb=X.bbox,svg=$('mapsvg'),NS='http://www.w3.org/2000/svg',mode='n',polys=[];
  svg.setAttribute('viewBox',(bb[0]-6)+' '+(bb[1]-6)+' '+(bb[2]-bb[0]+12)+' '+(bb[3]-bb[1]+12));
  function color(l){if(mode==='s')return scol(l[0]);if(mode==='h')return 'hsl('+Math.round(240-240*(l[3]-1)/3184)+',65%,52%)';var n=parseInt(l[1].replace(/[^0-9]/g,''),10)||0;return 'hsl('+((n*47)%360)+',60%,'+(40+(n*13)%25)+'%)'}
  X.maplots.forEach(function(l){if(!l[4])return;var p=document.createElementNS(NS,'polygon');p.setAttribute('points',l[4].map(function(q){return q.join(',')}).join(' '));p._l=l;svg.appendChild(p);polys.push(p)});
  var acc={};X.maplots.forEach(function(l){if(l[5]!=null){(acc[l[0]]=acc[l[0]]||[]).push([l[5],l[6]])}});
  Object.keys(acc).forEach(function(s){var a=acc[s].sort(function(x,y){return x[0]-y[0]}),b=acc[s].slice().sort(function(x,y){return x[1]-y[1]});var t=document.createElementNS(NS,'text');t.setAttribute('x',a[a.length>>1][0]);t.setAttribute('y',b[b.length>>1][1]);t.setAttribute('text-anchor','middle');t.setAttribute('style','font:700 26px var(--sans);fill:var(--fg);stroke:var(--bg);stroke-width:5px;paint-order:stroke;pointer-events:none');t.textContent=s;t.setAttribute('class','seclab');svg.appendChild(t)});
  function paint(){polys.forEach(function(p){p.setAttribute('fill',color(p._l))});
    $('mapnote').textContent={n:'Colored by the number written on the lot. Neighbouring lots get unrelated colors because every section restarts and skips.',s:'Colored by old section letter. Section letters are drawn on the map.',h:'Colored by H-number: one smooth sweep from blue (H000001) to red (H003185).'}[mode];
    $('maplegend').innerHTML=mode==='s'?SEC.map(function(s){return '<span><i style="background:'+scol(s)+'"></i>'+s+'</span>'}).join(''):mode==='h'?'<span><i style="background:hsl(240,65%,52%)"></i>H000001</span><span><i style="background:hsl(120,65%,52%)"></i>middle</span><span><i style="background:hsl(0,65%,52%)"></i>H003185</span>':'<span>Each color is a label number. Colors repeat because label numbers repeat in every section.</span>'}
  [].forEach.call(document.querySelectorAll('button.seg[data-mode]'),function(b){on(b,'click',function(){mode=b.getAttribute('data-mode');[].forEach.call(document.querySelectorAll('button.seg[data-mode]'),function(x){x.classList.toggle('on',x===b)});paint()})});
  var tip=$('maptip'),box=$('mapbox');
  on(svg,'mousemove',function(e){var p=e.target;if(!p._l){tip.style.display='none';return}var l=p._l,r=box.getBoundingClientRect();tip.textContent=l[0]+'-'+l[1]+'  →  '+l[2];tip.style.display='block';tip.style.left=Math.min(e.clientX-r.left+12,r.width-170)+'px';tip.style.top=(e.clientY-r.top+14)+'px'});
  on(svg,'mouseleave',function(){tip.style.display='none'});paint();
})();

/* sawtooth */
(function(){
  var cv=$('saw'),cx=cv.getContext('2d'),S=A.saw;
  function draw(){
    var st=+$('sawstart').value,wd=+$('sawwidth').value;$('sawstartv').textContent=st;$('sawwidthv').textContent=wd;
    var pts=S.filter(function(r){return r[0]>=st&&r[0]<st+wd}),Wd=cv.width,Hh=cv.height,m=58,b=46;cx.clearRect(0,0,Wd,Hh);
    var mx=1;pts.forEach(function(r){if(r[2]>mx)mx=r[2]});mx=Math.ceil(mx/10)*10;
    var xs=function(h){return m+(h-st)/Math.max(wd-1,1)*(Wd-m-16)},ys=function(v){return Hh-b-(v/mx)*(Hh-b-26)};
    cx.font='500 13px "IBM Plex Mono",monospace';cx.fillStyle=css('--g5');cx.strokeStyle=css('--g3');cx.lineWidth=1;
    for(var i=0;i<=4;i++){var v=mx*i/4,y=ys(v);cx.beginPath();cx.moveTo(m,y);cx.lineTo(Wd-8,y);cx.stroke();cx.textAlign='right';cx.fillText(Math.round(v),m-8,y+4)}
    for(i=0;i<=4;i++){var h=st+Math.round((wd-1)*i/4),x=xs(h);cx.textAlign='center';cx.fillText(h,x,Hh-b+18)}
    cx.fillStyle=css('--g6');cx.font='600 13px "Space Grotesk",sans-serif';cx.textAlign='center';cx.fillText('H-number (position along the path) →',(Wd+m)/2,Hh-8);
    cx.save();cx.translate(14,(Hh-b)/2);cx.rotate(-Math.PI/2);cx.fillText('old label number →',0,0);cx.restore();
    cx.strokeStyle=css('--gold');cx.lineWidth=2;cx.globalAlpha=.9;cx.beginPath();cx.moveTo(m,Hh-b);cx.lineTo(Wd-16,26);cx.stroke();cx.globalAlpha=1;
    var rad=Math.max(1.8,Math.min(4.5,900/Math.max(pts.length,1)));
    pts.forEach(function(r){cx.fillStyle=scol(r[1]);cx.beginPath();cx.arc(xs(r[0]),ys(r[2]),rad,0,6.3);cx.fill()});
    var used={};pts.forEach(function(r){used[r[1]]=1});
    $('sawlegend').innerHTML='<span><i style="background:var(--gold)"></i>gold line: where the label number would sit if it matched H, scaled to fit</span>'+Object.keys(used).map(function(s){return '<span><i style="background:'+scol(s)+'"></i>section '+s+'</span>'}).join('');
  }
  on($('sawstart'),'input',draw);on($('sawwidth'),'input',draw);draw();redraws.push(draw);
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
