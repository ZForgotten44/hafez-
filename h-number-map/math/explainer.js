(function(){
"use strict";
var $=function(i){return document.getElementById(i)};
var esc=function(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')};
var pad=function(h){return 'H'+String(h).padStart(6,'0')};
var toast=function(m){var t=$('toast');t.textContent=m;t.classList.add('show');setTimeout(function(){t.classList.remove('show')},1600)};
var SEC='ABCDEFGHIJKLM'.split('');
var COL=['#b4531f','#17496e','#2f6b46','#8a3b8f','#b8892f','#a23325','#3a7d8c','#6b5b95','#c27c0e','#4a6b2f','#7a4a3a','#2d5f9e','#8c6a5a'];
var scol=function(s){return COL[SEC.indexOf(s)]||'#888'};
var A=X.A, FWD=X.fwd.filter(function(r){return !/dr$/.test(r[1])}), W=X.W;
var FW={};FWD.forEach(function(r){FW[r[0]+'|'+r[1]]=r[2]});
function on(el,ev,fn){if(el)el.addEventListener(ev,fn)}

/* ---- giant formula, compiled from data ---- */
function compile(decl){return new Function('S','L','var m,p,n,f,r,q,c,k,i,j,g,b,'+decl.replace(/;/g,',')+';return '+X.giant.expr+';')}
var GH=compile(X.giant.decl);

/* ---- section 2: chips and anatomy ---- */
(function(){
  var picks=[['A','13H'],['B','19A'],['B','384HA'],['C','51'],['C','12B'],['D','1H'],['D','F1'],['E','199BH'],['G','19'],['K','57'],['M','61'],['B','B362']];
  var html='';picks.forEach(function(p){if(FW[p[0]+'|'+p[1]]!=null)html+='<span class="chip" title="'+pad(FW[p[0]+'|'+p[1]])+'">'+p[0]+'-'+esc(p[1])+'</span>'});
  $('sampleChips').innerHTML=html;
  var h='';
  SEC.forEach(function(s){var rows=X.chips[s];if(!rows)return;
    h+='<div style="margin:10px 0"><b>Section '+s+'</b> <span class="note">first two rows, walked in order</span>';
    rows.forEach(function(row,ri){h+='<div class="chips">'+row.map(function(c){var k=c[1];return '<span class="chip '+(k==='plain'?'':k)+'" title="'+(c[2]?pad(c[2]):'no H')+'">'+esc(c[0]||'?')+'</span>'}).join('')+'</div>'});
    h+='</div>'});
  $('anatomy').innerHTML=h;
})();

/* ---- section 3: stats, explorer, rules ---- */
(function(){
  var st=[[A.lots.toLocaleString(),'(section, label) pairs the decoder accepts'],[A.distinct_labels,'distinct labels among them'],[A.labels_in_2plus_sections,'labels used by two or more sections'],[Math.round(100*A.lots_with_shared_label/A.lots)+'%','of lots share their label with a lot elsewhere'],[A.max_sections_per_label,'sections that all have a lot called "19"'],[A.unlabeled_positions.count,'grid positions in Sections B and A with no label at all']];
  $('stats').innerHTML=st.map(function(s){return '<div class="stat"><div class="n">'+s[0]+'</div><div class="l">'+s[1]+'</div></div>'}).join('');
  var byL={};FWD.forEach(function(r){(byL[r[1].toUpperCase()]=byL[r[1].toUpperCase()]||[]).push(r)});
  function show(){var q=$('lbl').value.trim().toUpperCase(),r=byL[q]||[];
    if(!q){$('lblout').innerHTML='';return}
    if(!r.length){$('lblout').innerHTML='<p class="note">No section has a lot labelled "'+esc(q)+'".</p>';return}
    $('lblout').innerHTML='<p><b>'+r.length+'</b> lot'+(r.length>1?'s':'')+' labelled "'+esc(q)+'"'+(r.length>1?', each in a different place:':':')+'</p><div class="chips">'+r.map(function(x){return '<span class="chip" style="border-left:4px solid '+scol(x[0])+'">'+x[0]+'-'+esc(x[1])+' → '+pad(x[2])+'</span>'}).join('')+'</div>'+(r.length>1?'<p class="note">The H-numbers are '+r.map(function(x){return x[2]}).join(', ')+': all different, so the name is never ambiguous.</p>':'')}
  on($('lbl'),'input',show);
  var multi=Object.keys(byL).filter(function(k){return byL[k].length>=3});
  on($('lblr'),'click',function(){$('lbl').value=multi[Math.floor(Math.random()*multi.length)];show()});
  show();
  var rules=[['A','19 per row, counted right to left','H-lots slipped in at places 13, 5 and 1 of every row'],['B','20 per row in the body, but the last column steps by 19','Column 2 and 3 both claim 19; the last label of a row repeats a body label; "19A" is an extra; a 41-lot margin is numbered 373 to 394 with letters'],['C','Row tops go 19, 38 … 247, then 16 at a time, then 19, 19 …','Twin pairs (51 and its H-lot) and A/B/C trios on eight rows; the row size changes six times'],['D','20 per row for rows 2 to 15, then blocks that run both ways','H-lots at 20(r−1) and 20r−11; row 1 uses letters 1H to 1U and 1A to 1G; a 22-lot margin numbered 542 to 563'],['E','19 per row with twins at places 13, 9 and 5','Rows 9 to 12 change shape; the lots 152, 169 and 190 to 199 carry A/B suffixes'],['F','18 per row','Eleven rows; a margin of 12 lots numbered 199 to 210'],['G','19 per row for lots 1 to 57','58 to 60 and 61 to 75 are tacked on; the label 19 appears twice in the first row'],['H','23 per row','Four rows only'],['I','1 to 64 straight','No rules, just a counter'],['J','1 to 132 straight','No rules, just a counter'],['K','115 lots in an order no formula gives','1, 2, 3, 6, 7, 8, 9, 13 …: stored as a list'],['L','Starts at 69 and ends at 107','The numbers 1 to 68 are not here at all'],['M','82 to 279 straight','The first 51 lots are in an irregular order and are stored as a list']];
  var V=A.verify.per_section;
  var h='<table class="t"><tr><th>Section</th><th>How its labels are built</th><th>Special cases</th><th>Decoder coverage</th></tr>';
  rules.forEach(function(r){var v=V[r[0]]||{},tot=0;Object.keys(v).forEach(function(k){tot+=v[k]});
    var bars=[['closed','#2f6b46','arithmetic'],['rows','#b8892f','row constants'],['list','#a23325','list'],['errata','#8a3b8f','errata']].map(function(b){return v[b[0]]?'<i title="'+b[2]+': '+v[b[0]]+'" style="display:inline-block;height:10px;width:'+Math.max(2,Math.round(140*v[b[0]]/Math.max(tot,1)))+'px;background:'+b[1]+'"></i>':''}).join('');
    h+='<tr><td><b>'+r[0]+'</b></td><td>'+r[1]+'</td><td>'+r[2]+'</td><td style="white-space:nowrap">'+bars+' <span class="note">'+tot+'</span></td></tr>'});
  h+='</table><div class="legend"><span><i style="background:#2f6b46"></i>pure arithmetic</span><span><i style="background:#b8892f"></i>arithmetic plus row constants</span><span><i style="background:#a23325"></i>explicit list</span><span><i style="background:#8a3b8f"></i>errata</span></div>';
  $('rules').innerHTML=h;
})();

/* ---- map ---- */
(function(){
  var bb=X.bbox,svg=$('mapsvg'),NS='http://www.w3.org/2000/svg',mode='n',polys=[];
  svg.setAttribute('viewBox',(bb[0]-6)+' '+(bb[1]-6)+' '+(bb[2]-bb[0]+12)+' '+(bb[3]-bb[1]+12));
  var maxN=1;X.maplots.forEach(function(l){var n=parseInt(l[1],10);if(n>maxN&&n<500)maxN=n});
  function color(l){
    if(mode==='s')return scol(l[0]);
    if(mode==='h')return 'hsl('+Math.round(240-240*(l[3]-1)/3184)+',65%,52%)';
    var n=parseInt(l[1].replace(/[^0-9]/g,''),10)||0;return 'hsl('+((n*47)%360)+',60%,'+(40+(n*13)%25)+'%)';
  }
  X.maplots.forEach(function(l){if(!l[4])return;var p=document.createElementNS(NS,'polygon');p.setAttribute('points',l[4].map(function(q){return q.join(',')}).join(' '));p._l=l;svg.appendChild(p);polys.push(p)});
  function paint(){polys.forEach(function(p){p.setAttribute('fill',color(p._l))});
    $('mapnote').textContent={n:'Colored by the number written on the lot. Neighbouring lots get unrelated colors because every section restarts and skips.',s:'Colored by old section letter. Notice that H-lots and margins break the pattern at section edges.',h:'Colored by H-number. One smooth sweep from blue (H000001) to red (H003185).'}[mode];
    var lg=$('maplegend');lg.innerHTML=mode==='s'?SEC.map(function(s){return '<span><i style="background:'+scol(s)+'"></i>'+s+'</span>'}).join(''):mode==='h'?'<span><i style="background:hsl(240,65%,52%)"></i>H000001</span><span><i style="background:hsl(120,65%,52%)"></i>middle</span><span><i style="background:hsl(0,65%,52%)"></i>H003185</span>':'<span>color = old label number (it repeats in every section)</span>'}
  Array.prototype.forEach.call(document.querySelectorAll('button.seg[data-mode]'),function(b){on(b,'click',function(){mode=b.getAttribute('data-mode');Array.prototype.forEach.call(document.querySelectorAll('button.seg[data-mode]'),function(x){x.classList.toggle('on',x===b)});paint()})});
  var tip=$('maptip'),box=$('mapbox');
  on(svg,'mousemove',function(e){var p=e.target;if(!p._l){tip.style.display='none';return}var l=p._l,r=box.getBoundingClientRect();tip.textContent=l[0]+'-'+l[1]+'  →  '+l[2];tip.style.display='block';tip.style.left=Math.min(e.clientX-r.left+12,r.width-170)+'px';tip.style.top=(e.clientY-r.top+14)+'px'});
  on(svg,'mouseleave',function(){tip.style.display='none'});
  paint();
})();

/* ---- sawtooth ---- */
(function(){
  var cv=$('saw'),cx=cv.getContext('2d'),S=A.saw;
  var css=function(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim()||'#888'};
  function draw(){
    var st=+$('sawstart').value,wd=+$('sawwidth').value;$('sawstartv').textContent=st;$('sawwidthv').textContent=wd;
    var pts=S.filter(function(r){return r[0]>=st&&r[0]<st+wd});
    var Wd=cv.width,Hh=cv.height,m=44;cx.clearRect(0,0,Wd,Hh);
    var mx=1;pts.forEach(function(r){if(r[2]>mx)mx=r[2]});
    cx.font='12px sans-serif';cx.fillStyle=css('--mid');cx.strokeStyle=css('--line2');
    cx.beginPath();cx.moveTo(m,8);cx.lineTo(m,Hh-m);cx.lineTo(Wd-8,Hh-m);cx.stroke();
    cx.fillText('old label number (0 to '+mx+')',m+4,18);cx.fillText('H-number '+st+' to '+(st+wd-1)+' along the path →',Wd-250,Hh-14);
    var xs=function(h){return m+(h-st)/Math.max(wd-1,1)*(Wd-m-14)},ys=function(v){return Hh-m-(v/mx)*(Hh-m-30)};
    cx.strokeStyle=css('--h');cx.globalAlpha=.5;cx.beginPath();cx.moveTo(m,Hh-m);cx.lineTo(Wd-14,30);cx.stroke();cx.globalAlpha=1;
    var rad=Math.max(1.6,Math.min(4,900/Math.max(pts.length,1)));
    pts.forEach(function(r){cx.fillStyle=scol(r[1]);cx.beginPath();cx.arc(xs(r[0]),ys(r[2]),rad,0,6.3);cx.fill()});
    var used={};pts.forEach(function(r){used[r[1]]=1});$('sawlegend').innerHTML='<span><i style="background:var(--h)"></i>H-number (diagonal, scaled)</span>'+Object.keys(used).map(function(s){return '<span><i style="background:'+scol(s)+'"></i>section '+s+'</span>'}).join('');
  }
  on($('sawstart'),'input',draw);on($('sawwidth'),'input',draw);draw();
  if(window.matchMedia)window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',draw);
})();

/* ---- defects ---- */
(function(){
  var d=[['B','Labels shadowed by the margin','The grid rule gives lots 373 to 379 a place in the main block, but the margin list claims the same labels; the later rule overwrites the earlier one, so '+A.B_grid_labels_shadowed_by_margin.length+' grid labels cannot be reached.'],['A, B','Positions with no label',A.unlabeled_positions.count+' places in the first sweep (for example H010, H046, H055) have no old label at all, so a person could not name them.'],['D, G','Duplicate keys in the decoder table','Section D lists 274 twice and Section G lists 19 twice in row 1. The formula resolves each to one lot and records the other as errata.'],['C','A typo in a row table','Row 8 of C lists "124H" where the pattern requires "142H". The decoder kept it; the formula maps it to the lot it was meant to be.'],['B, A','The documents disagree with the code','The PDF and docstring say the sweep alternates B column 1, A column 1, B column 2 and so on; the code numbers the whole level of B first and then A. Step 1 below lets you flip between them.'],['C','The idealised grid is not the real grid','The reference sheet assumes 22 lots in every row and ends at C-417 = H001672. The real rows have 19 to 22 lots, so the real C-417 is H001871.']];
  $('defects').innerHTML=d.map(function(x){return '<div class="card"><span class="pill bad">Section '+x[0]+'</span> <b>'+x[1]+'</b><p style="margin:6px 0 0">'+x[2]+'</p></div>'}).join('');
})();

/* ---- passes ---- */
(function(){
  var P=[['Pass 1','B, A',1,836],['Pass 2','D, C',837,1871],['Pass 3','F, E',1872,2331],['Pass 4','B, D, F margins; G, H',2332,2585],['Pass 5','M',2586,2835],['Pass 6','K, J, I, L',2836,3185]];
  $('passes').innerHTML=P.map(function(p,i){var w=(p[3]-p[2]+1)/3185*100;return '<div style="display:flex;align-items:center;gap:10px;margin:6px 0"><div style="flex:0 0 130px"><b>'+p[0]+'</b><br><span class="note">'+p[1]+'</span></div><div style="flex:1;background:var(--surface2);border-radius:6px;height:26px;position:relative"><div style="position:absolute;left:'+((p[2]-1)/3185*100)+'%;width:'+w+'%;height:100%;border-radius:6px;background:'+COL[i]+'"></div></div><div class="note" style="flex:0 0 150px">'+pad(p[2])+' – '+pad(p[3])+'</div></div>'}).join('');
})();

/* ---- P1 ---- */
(function(){
  var ord='blocks';
  function Hf(sec,r,c,N){var SW=2*N;return ord==='blocks'?SW*(r-1)+(sec==='B'?0:N)+c:SW*(r-1)+2*c-(sec==='B'?1:0)}
  function run(){
    var N=+$('p1n').value,R=+$('p1r').value;$('p1nv').textContent=N;$('p1rv').textContent=R;
    var sec=$('p1sec').value,r=Math.min(Math.max(1,+$('p1lv').value||1),R),c=Math.min(Math.max(1,+$('p1c').value||1),N);
    $('p1out').innerHTML='SWEEP = <b>'+2*N+'</b>   OFFSET = <b>'+2*N*R+'</b> lots before pass 2<br>H('+sec+', level '+r+', column '+c+') = <span class="h">'+Hf(sec,r,c,N)+'</span>  →  '+pad(Hf(sec,r,c,N));
    var cv=$('p1cv'),cx=cv.getContext('2d');cx.clearRect(0,0,cv.width,cv.height);
    var cw=(cv.width-60)/N,ch=Math.min(18,(cv.height-20)/(2*R+1));cv._g={cw:cw,ch:ch,N:N,R:R};
    ['B','A'].forEach(function(s,si){for(var rr=1;rr<=R;rr++)for(var cc=1;cc<=N;cc++){var h=Hf(s,rr,cc,N);cx.fillStyle='hsl('+Math.round(240-240*(h-1)/(2*N*R))+',60%,'+(s==='B'?50:62)+'%)';cx.fillRect(40+(cc-1)*cw,10+(si*(R+1)+rr-1)*ch,cw-1,ch-1)}});
    cx.fillStyle='#888';cx.font='11px sans-serif';cx.fillText('B',14,10+ch);cx.fillText('A',14,10+(R+1)*ch+ch);
  }
  ['p1n','p1r','p1sec','p1lv','p1c'].forEach(function(i){on($(i),'input',run)});
  Array.prototype.forEach.call(document.querySelectorAll('button[data-ord]'),function(b){on(b,'click',function(){ord=b.getAttribute('data-ord');Array.prototype.forEach.call(document.querySelectorAll('button[data-ord]'),function(x){x.classList.toggle('on',x===b)});run()})});
  on($('p1cv'),'mousemove',function(e){var cv=this,g=cv._g;if(!g)return;var r=cv.getBoundingClientRect(),x=(e.clientX-r.left)*cv.width/r.width-40,y=(e.clientY-r.top)*cv.height/r.height-10;var cc=Math.floor(x/g.cw)+1,row=Math.floor(y/g.ch),si=row>=g.R+1?1:0,rr=row-si*(g.R+1)+1;if(cc<1||cc>g.N||rr<1||rr>g.R){cv.title='';return}cv.title=(si?'A':'B')+' level '+rr+', column '+cc+' = '+Hf(si?'A':'B',rr,cc,g.N)});
  run();
})();

/* ---- P2 ---- */
(function(){
  function a(){
    var st=+$('p2inc').value,rows=Math.min(4,Math.max(1,+$('p2rows').value||1));$('p2incv').textContent=st;
    var tw=$('p2tw').value.split(',').map(function(x){return +x.trim()}).filter(function(x){return x>0&&x<=st});
    var out='',all={},bad=0;
    for(var r=1;r<=rows;r++){var cells=[];
      for(var q=1;q<=st;q++){var n=st*(r-1)+q,c=20-q,nt=tw.filter(function(t){return q<=t}).length;c+=nt;
        cells.push({c:c,l:String(n),h:44*(r-1)+22+c,q:q});
        if(tw.indexOf(q)>=0)cells.push({c:c-1,l:n+'H',h:44*(r-1)+22+c-1,q:q,hl:1})}
      cells.sort(function(x,y){return x.h-y.h});
      var seen={},html='<div class="note">Row '+r+', in H order</div><div class="chips">';
      cells.forEach(function(x){var dup=seen[x.h];seen[x.h]=1;if(dup)bad++;html+='<span class="chip '+(dup?'odd':x.hl?'h':'')+'" title="column '+x.c+'">'+x.l+' → '+x.h+'</span>'});
      out+=html+'</div>';
      var cs=cells.map(function(x){return x.c}).sort(function(x,y){return x-y});var gaps=0;for(var i=1;i<cs.length;i++)gaps+=Math.max(0,cs[i]-cs[i-1]-1);
      if(gaps)out+='<div class="note bad">'+gaps+' column(s) left empty in row '+r+'</div>'}
    if(bad)out+='<div class="note bad">'+bad+' clash(es): two lots got the same H-number. With the real rule (step 19, twins at 13, 5, 1) there are none.</div>';
    else out+='<div class="note good">No clashes.</div>';
    $('p2out').innerHTML=out;
  }
  ['p2inc','p2tw','p2rows'].forEach(function(i){on($(i),'input',a)});a();
  function b(){
    var s1=+$('p2b1').value,s2=+$('p2b2').value,f=+$('p2b3').value;$('p2b1v').textContent=s1;$('p2b2v').textContent=s2;$('p2b3v').textContent=f;
    var body={},last={},coll=[],ex='';
    for(var r=1;r<=19;r++){for(var q=1;q<s1;q++)body[s1*(r-1)+q]=r;last[f+s2*(r-1)]=r}
    Object.keys(last).forEach(function(l){if(body[l])coll.push(l)});
    ex='row 1 body labels: 1 … '+(s1-1)+'<br>row 1 last column: '+f+'<br>row 2 last column: '+(f+s2)+'<br>row 19 last column: '+(f+18*s2)+'<br>';
    $('p2bout').innerHTML=ex+(coll.length?'<span class="bad">'+coll.length+' last-column labels collide with a body label ('+coll.slice(0,6).join(', ')+(coll.length>6?' …':'')+')</span>':'<span class="good">No label is used twice.</span>')+'<br>real values (20, 19, 12): collisions are resolved by "later rule wins".';
  }
  ['p2b1','p2b2','p2b3'].forEach(function(i){on($(i),'input',b)});b();
})();

/* ---- P3 ---- */
(function(){
  var mode='real',wd=W.WD.slice(),wc=W.WC.slice();
  function pf(w1,w2,r){var s=0;for(var j=0;j<r-1;j++)s+=(w1[j]||0)+(w2[j]||0);return s}
  function tab(){
    var h='<tr><th>Row</th><th>W<sub>D</sub></th><th>W<sub>C</sub></th><th>lots before row</th></tr>';
    for(var r=1;r<=24;r++)h+='<tr><td>'+r+'</td><td><input type="number" min="0" data-s="d" data-r="'+(r-1)+'" value="'+(wd[r-1]||0)+'" style="width:76px"></td><td><input type="number" min="0" data-s="c" data-r="'+(r-1)+'" value="'+wc[r-1]+'" style="width:76px"></td><td class="num">'+pf(wd,wc,r)+'</td></tr>';
    $('p3tab').innerHTML=h;
    Array.prototype.forEach.call($('p3tab').querySelectorAll('input'),function(i){on(i,'change',function(){(i.getAttribute('data-s')==='d'?wd:wc)[+i.getAttribute('data-r')]=+i.value||0;tab();out()})});
  }
  function out(){
    var s=$('p3sec').value,r=Math.min(24,Math.max(1,+$('p3r').value||1)),k=Math.max(1,+$('p3k').value||1);
    var H=836+pf(wd,wc,r)+(s==='C'?(wd[r-1]||0):0)+k,end=836+wd.reduce(function(a,b){return a+b},0)+wc.reduce(function(a,b){return a+b},0);
    $('p3out').innerHTML='H('+s+', row '+r+', place '+k+') = 836 + '+pf(wd,wc,r)+(s==='C'?' + '+(wd[r-1]||0):'')+' + '+k+' = <span class="h">'+H+'</span> → '+pad(H)+'<br>Pass 2 ends at <b>'+end+'</b>'+(end!==1871?' <span class="bad">(real value 1871: every later pass would shift by '+(end-1871)+')</span>':' (matches the real 1871)');
  }
  Array.prototype.forEach.call(document.querySelectorAll('button[data-w]'),function(b){on(b,'click',function(){mode=b.getAttribute('data-w');Array.prototype.forEach.call(document.querySelectorAll('button[data-w]'),function(x){x.classList.toggle('on',x===b)});
    if(mode==='ideal'){wd=[];wc=[];for(var i=0;i<24;i++){wd.push(i<19?22:0);wc.push(i<19?22:0)}}else{wd=W.WD.slice();wc=W.WC.slice()}tab();out()})});
  ['p3sec','p3r','p3k'].forEach(function(i){on($(i),'input',out)});tab();out();
})();

/* ---- P4 ---- */
var P4=(function(){
  var WD=W.WD.slice(),WC=W.WC.slice();
  function pf(r){var s=0;for(var j=0;j<r-1;j++)s+=(WD[j]||0)+WC[j];return s}
  function calc(row,tw,trio){
    var top=W.CT[row-1],lo=row>1?W.CT[row-2]+1:1,base=836+pf(row)+(WD[row-1]||0),L=[];
    function cnt(n){return tw.filter(function(w){return w[0]>n||(w[0]===n&&!w[1])}).length}
    for(var n=top;n>=lo;n--){var k=top-n+1+(trio?3:0)+cnt(n);L.push([String(n),base+k]);
      var t=tw.filter(function(w){return w[0]===n})[0];if(t)L.push([n+'H',base+k+(t[1]?1:-1)])}
    if(trio)['C','B','A'].forEach(function(s,i){L.push([top+s,base+i+1])});
    return L.sort(function(a,b){return a[1]-b[1]});
  }
  function run(){
    var row=Math.min(24,Math.max(1,+$('p4row').value||1)),trio=$('p4trio').value==='1';
    var tw=$('p4tw').value.split(',').map(function(s){s=s.trim();var m=/^(\d+)([ab]?)$/.exec(s);return m?[+m[1],m[2]==='a'?1:0]:null}).filter(Boolean);
    var L=calc(row,tw,trio),seen={},dup=0;
    var h='<div class="note">Row '+row+' of C: top lot '+W.CT[row-1]+'. Lots in H order:</div><div class="chips">'+L.map(function(x){var d=seen[x[1]];seen[x[1]]=1;if(d)dup++;return '<span class="chip '+(/H$/.test(x[0])?'h':/[ABC]$/.test(x[0])?'suffix':'')+(d?' odd':'')+'" title="'+pad(x[1])+'">'+x[0]+' → '+x[1]+'</span>'}).join('')+'</div>';
    var real=0,mis=0;L.forEach(function(x){var v=FW['C|'+x[0]];if(v!=null){real++;if(v!==x[1])mis++}});
    h+='<div class="note">'+(real?real+' of these labels exist in the decoder; '+(mis?'<span class="bad">'+mis+' differ from it</span>':'<span class="good">all agree with it</span>'):'None of these labels exist in the real section C, so this is a what-if.')+(dup?' <span class="bad">'+dup+' clash(es)</span>':'')+'</div>';
    $('p4out').innerHTML=h;
  }
  ['p4row','p4tw','p4trio'].forEach(function(i){on($(i),'input',run)});
  var rowTw=function(r){return W.CTW[r]||[]};
  run();return {calc:calc,rowTw:rowTw};
})();

/* ---- P5, P6 ---- */
(function(){
  function p5(){
    var s=$('p5sec').value,n=+$('p5n').value,H=NaN;
    if(s==='J'&&n>=1&&n<=132)H=2950+n;else if(s==='I'&&n>=1&&n<=64)H=3082+n;else if(s==='L'&&n>=69&&n<=107)H=3146+n-68;else if(s==='M'&&n>=82&&n<=279)H=n+2556;else if(s==='F'&&n>=199&&n<=210)H=n+2203;else if(s==='F'&&n>=1&&n<=198){var r=Math.floor((n-1)/18)+1;H=1871+(function(){var t=0;for(var j=0;j<r-1;j++)t+=W.WF[j]+W.WE[j];return t})()+19-(n-18*(r-1))}
    $('p5out').innerHTML=isNaN(H)?'Section '+s+' has no lot '+n+' in the closed-form range.':'H('+s+', '+n+') = <span class="h">'+H+'</span> → '+pad(H)+(GH(s,String(n))===H?'  <span class="good">matches the giant formula</span>':'');
  }
  ['p5sec','p5n'].forEach(function(i){on($(i),'input',p5)});p5();
  function p6(){var h=Math.max(1,Math.round(+$('p6h').value||1)),g=Math.min(9,Math.max(1,+$('p6g').value||1)),sf=$('p6s').value;
    $('p6out').innerHTML='lot '+pad(h)+sf+'  +  grave '+g+'  =  <span class="h">'+pad(h)+sf+g+'</span><br>numeric form: 10 × '+h+' + '+g+' = '+(10*h+g)}
  ['p6h','p6g','p6s'].forEach(function(i){on($(i),'input',p6)});p6();
})();

/* ---- snippets ---- */
(function(){
  var KW='def|return|if|elif|else|for|in|not|and|or|is|None|True|False|import|from|lambda|while|raise|sum|range|len|dict|list|tuple|set|class|continue|break';
  var rx=new RegExp('(#[^\\n]*)|("""[\\s\\S]*?"""|\'[^\'\\n]*\'|"[^"\\n]*")|\\b('+KW+')\\b|\\b(\\d+)\\b','g');
  function hl(c){return esc(c).replace(/(#[^\n]*)|(&quot;|"""[\s\S]*?"""|'[^'\n]*'|"[^"\n]*")|\b(def|return|if|elif|else|for|in|not|and|or|is|None|True|False|import|from|lambda|while|raise|sum|range|len|class|continue|break)\b|\b(\d+)\b/g,function(m,cm,st,kw,nu){return cm?'<span class="c">'+cm+'</span>':st?'<span class="s">'+st+'</span>':kw?'<span class="k">'+kw+'</span>':'<span class="n">'+nu+'</span>'})}
  var h='';
  X.snips.forEach(function(g){h+='<h3>'+esc(g.title)+'</h3><p class="note">'+esc(g.note)+'</p>';g.items.forEach(function(s,i){h+='<details'+(i<1?' open':'')+'><summary>'+esc(s.name)+' <span class="note">· '+esc(s.file)+'</span></summary><pre class="code">'+hl(s.src)+'</pre></details>'})});
  $('snips').innerHTML=h;
})();

/* ---- giant calculator ---- */
var RV=null;
(function(){
  var gs=$('gs');gs.innerHTML=SEC.map(function(s){return '<option>'+s+'</option>'}).join('');gs.value='B';
  function run(){
    var S=gs.value,L=$('gl').value.trim(),m=/^([A-Z]?)([0-9]+)(.*)$/.exec(L);
    var v=GH(S,L),exp=FW[S+'|'+L];
    var o;
    if(typeof v==='number'&&!isNaN(v)){o='H('+S+', "'+esc(L)+'") = <span class="h">'+v+'</span> → <span class="h">'+pad(v)+'</span><br>first grave: '+pad(v)+'1 … last: '+pad(v)+'9'+(exp===v?'<br><span class="good">The decoder returns the same value.</span>':exp==null?'<br><span class="bad">The decoder does not know this label.</span>':'<br><span class="bad">The decoder returns '+exp+'.</span>')}
    else o='<span class="bad">No lot '+esc(S)+'-'+esc(L)+' exists in the formula\'s ranges.</span>'+(exp!=null?' (the decoder lists it as '+exp+')':'');
    $('gout').innerHTML=o;
    var br=X.giant.parts?X.giant.parts[S]:'';
    $('gtrace').innerHTML='<details><summary>Show the working</summary><div class="out">parse "'+esc(L)+'": prefix = "'+(m?esc(m[1]):'')+'", number n = '+(m?+m[2]:'none')+', suffix = "'+(m?esc(m[3]):'')+'"<br>section switch picks the branch for <b>'+S+'</b>:</div><pre class="code" style="white-space:pre-wrap;word-break:break-all">'+esc(br||'')+'</pre></details>';
  }
  on(gs,'change',run);on($('gl'),'input',run);
  var ex=[['B','20H'],['A','1'],['C','417'],['D','1H'],['E','199BH'],['G','61'],['K','57'],['M','100'],['J','132'],['L','107'],['F','210'],['B','384HA'],['D','563']];var ei=0;
  on($('gex'),'click',function(){var e=ex[ei++%ex.length];gs.value=e[0];$('gl').value=e[1];run()});
  run();
  function rev(){var h=+$('gh').value;if(!RV){RV={};FWD.forEach(function(r){var v=GH(r[0],r[1]);(RV[v]=RV[v]||[]).push(r[0]+'-'+r[1])})}
    var r=RV[h];$('grev').innerHTML=r?pad(h)+'  =  '+r.map(esc).join('  ·  '):'No old label maps to '+h+' (it is one of the '+(3185-Object.keys(RV).length)+' H-numbers the decoder has no old name for).'}
  on($('gh'),'input',rev);rev();
  var K=[['A','n → r = ⌈n/19⌉, q = n − 19(r−1); c = 20 − q + [q≤13] + [q≤5] + [q≤1] − [H-lot]','44(r−1) + 22 + c'],['B','body: n → r = ⌈n/20⌉, c = 20r − n; last column: r = (n−12)/19 + 1','44(r−1) + 22 + c; H-lot 20r: 44(r−1) + 1'],['C','k = (top_r − n) + 1 + 3·[trio] + #twins above','836 + Σ(W_D+W_C) + W_D(r) + k'],['D','by block (r, k₀, hi, lo): k = k₀ + hi − n; H-lots by row','836 + Σ(W_D+W_C) + k'],['E','k = 20 − q + [q≤13] + [q≤9] + [q≤5]; blocks in rows 9 to 12','1871 + Σ(W_F+W_E) + W_F(r) + k'],['F','k = 19 − (n − 18(r−1))','1871 + Σ(W_F+W_E) + k'],['G','k = 19r − n + (3 or 4) by side of H-lots','2413 + Σ(W_G+W_H) + k'],['H','k = 23r + 1 − n','2413 + Σ(W_G+W_H) + W_G(r) + k'],['M','n + 2556 for n ≥ 82; position in list otherwise','2586 + position'],['K','position of n in an ordered list of 115','2835 + position'],['J','n','2950 + n'],['I','n','3082 + n'],['L','n − 68','3146 + n − 68']];
  $('kappa').innerHTML='<tr><th>Section</th><th>place on the row κ(ℓ)</th><th>H</th></tr>'+K.map(function(k){return '<tr><td><b>'+k[0]+'</b></td><td>'+esc(k[1])+'</td><td>'+esc(k[2])+'</td></tr>'}).join('');
  var full='H = (S, L) => {\n  var m,p,n,f,r,q,c,k,i,j,g,b;\n'+X.giant.decl.split(';').map(function(d){return '  '+d+';'}).join('\n')+'\n  return '+X.giant.expr+';\n}';
  $('giantsrc').textContent=full;
  on($('cpg'),'click',function(){var t=full;if(navigator.clipboard)navigator.clipboard.writeText(t).then(function(){toast('Copied')},function(){toast('Select the text and copy')});else toast('Select the text and copy')});
  var dec0=X.giant.decl.split(';').join('\n');$('consts').value=dec0;
  function chk(decl){var fn,moved=0,nan=0,ex=[];try{fn=compile(decl.replace(/\n/g,';'))}catch(e){return '<span class="bad">Syntax error: '+esc(e.message)+'</span>'}
    FWD.forEach(function(r){var v;try{v=fn(r[0],r[1])}catch(e){v=NaN}if(v!==r[2]){if(typeof v!=='number'||isNaN(v))nan++;else moved++;if(ex.length<8)ex.push(r[0]+'-'+r[1]+': '+r[2]+' → '+v)}});
    return moved+nan===0?'<span class="good">All '+FWD.length+' labels still match the decoder.</span>':'<span class="bad">'+moved+' H-numbers moved, '+nan+' labels no longer resolve</span> (of '+FWD.length+').<br>'+ex.map(esc).join('<br>')}
  on($('capply'),'click',function(){$('cres').innerHTML=chk($('consts').value.trim())});
  on($('creset'),'click',function(){$('consts').value=dec0;$('cres').innerHTML=chk(dec0)});
  $('cres').innerHTML=chk(dec0);
})();

/* ---- compare, verify, errata ---- */
(function(){
  var rows=[['One name per lot','No: '+A.distinct_labels+' labels for '+A.lots.toLocaleString()+' lots','Yes: 1 to 3185, plus a grave digit'],['Same rule everywhere','No: 13 sections, 13 different rules','One rule: position along the path'],['Predictable neighbours','Neighbours differ by 1 only about 90% of the time, and steps of 19 or 20 across rows','Neighbours on the path differ by exactly 1'],['Reading it on the map','Tiny, sideways, with other sections\' letters mixed in','Large, upright in the lot, one per lot'],['Finding a lot from the number','Need the section, then the section\'s own rules','Numeric: H tells you which pass and which part of it'],['Graves','Not defined','Lot H × 10 + g'],['Machine-readable','Needs the 1,800-line decoder','One expression; a spreadsheet can hold it']];
  $('cmp').innerHTML='<tr><th>Question</th><th>Legacy labels</th><th>H-numbers</th></tr>'+rows.map(function(r){return '<tr><td><b>'+r[0]+'</b></td><td>'+r[1]+'</td><td>'+r[2]+'</td></tr>'}).join('');
  var v=A.verify,t=v.tiers;
  $('verify').innerHTML='<div class="grid3"><div class="stat"><div class="n">'+v.matched.toLocaleString()+' / '+v.total.toLocaleString()+'</div><div class="l">labels where the Python formulas equal the decoder</div></div><div class="stat"><div class="n">3,197 / 3,197</div><div class="l">labels where the one-line JavaScript equals the decoder (two internal keys excluded)</div></div><div class="stat"><div class="n" id="livechk">…</div><div class="l">checked in your browser just now</div></div></div><p class="note">Coverage by kind: '+t.closed+' closed-form, '+t.rows+' with per-row constants, '+t.list+' from ordered lists, '+t.errata+' errata.</p>';
  var ok=0;FWD.forEach(function(r){if(GH(r[0],r[1])===r[2])ok++});$('livechk').textContent=ok+' / '+FWD.length;
  $('errata').innerHTML=['Section D lists the label 274 twice and Section G lists 19 twice in its first row; the decoder keeps the later entry.','Section C row 8 lists "124H"; the pattern needs "142H". The formula answers for the typo and notes it.','The decoder keeps two internal keys, 152dr and 169dr, that are not real labels.','The reference PDF and the decoder docstring describe B and A as alternating columns; the code and all verified numbers use whole levels of B followed by A.','The reference PDF assumes a 22 by 19 grid; real rows are uneven, so its end-of-pass numbers differ from the real ones.'].map(function(s){return '<div class="card" style="margin:8px 0"><span class="pill bad">Note</span> '+s+'</div>'}).join('');
})();

/* ---- rail highlight ---- */
(function(){var links=document.querySelectorAll('#rail a'),secs=[].map.call(links,function(a){return document.querySelector(a.getAttribute('href'))});
  function f(){var y=window.scrollY+120,cur=0;secs.forEach(function(s,i){if(s&&s.offsetTop<=y)cur=i});[].forEach.call(links,function(a,i){a.classList.toggle('on',i===cur)})}
  window.addEventListener('scroll',f,{passive:true});f()})();
})();
