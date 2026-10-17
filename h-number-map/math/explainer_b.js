
/* ---------------- section 4 ---------------- */
/* animated example */
(function(){
  var cv=$('ancv'),cx=cv.getContext('2d'),s=0,timer=null,N=3,R=2;
  function geom(sec,r,c){var cw=120,ch=96,gx=70,x0=sec==='B'?60:60+N*cw+gx;return {x:x0+(c-1)*cw,y:56+(r-1)*(ch+22),w:cw-8,h:ch}}
  function info(t){var r=Math.ceil(t/(2*N)),w=t-2*N*(r-1),sec=w<=N?'B':'A',k=sec==='B'?w:w-N;return {r:r,sec:sec,k:k,H:t}}
  function draw(){
    cx.clearRect(0,0,cv.width,cv.height);cx.font='500 15px "IBM Plex Mono",monospace';cx.textAlign='center';
    cx.fillStyle=css('--g5');cx.fillText('Section B',60+N*60-4,32);cx.fillText('Section A',60+N*120+70+N*60-4,32);
    for(var t=1;t<=2*N*R;t++){var i=info(t),g=geom(i.sec,i.r,i.k),seen=t<=s,now=t===s;
      cx.fillStyle=seen?(now?css('--gold'):css('--surf')):css('--card');cx.strokeStyle=now?css('--fg'):css('--g4');cx.lineWidth=now?3:1.5;
      cx.beginPath();cx.roundRect?cx.roundRect(g.x,g.y,g.w,g.h,10):cx.rect(g.x,g.y,g.w,g.h);cx.fill();cx.stroke();
      cx.fillStyle=now?'#0b0b0a':seen?css('--fg'):css('--g4');cx.font='600 26px "IBM Plex Mono",monospace';cx.fillText(seen?String(t):'?',g.x+g.w/2,g.y+g.h/2+9)}
    if(s>1){var a=info(s-1),b=info(s),ga=geom(a.sec,a.r,a.k),gb=geom(b.sec,b.r,b.k);cx.strokeStyle=css('--gold');cx.lineWidth=3;cx.beginPath();cx.moveTo(ga.x+ga.w/2,ga.y+ga.h/2);cx.lineTo(gb.x+gb.w/2,gb.y+gb.h/2);cx.stroke()}
    cx.fillStyle=css('--g5');cx.font='500 13px "IBM Plex Mono",monospace';cx.fillText('level 1',30,56+48);cx.fillText('level 2',30,56+96+22+48);
    var o=$('anout');if(s===0)o.innerHTML='Press Play or Step. Two sections (B, A) of 3 columns, 2 levels: 12 lots.';
    else{var i2=info(s),before=2*N*(i2.r-1),sig=i2.sec==='A'?N:0;o.innerHTML='Lot '+s+': level '+i2.r+', section '+i2.sec+', place '+i2.k+'<br>H = '+before+' (lots on earlier levels) + '+sig+' (lots of B on this level, if A) + '+i2.k+' = <span class="hv">'+i2.H+'</span>'+(s===12?'<br>Done. Every lot has exactly one number, in path order.':'')}
  }
  function stop(){if(timer){clearInterval(timer);timer=null}$('anplay').textContent='Play'}
  function step(){s=s>=12?0:s+1;draw()}
  on($('anstep'),'click',function(){stop();step()});
  on($('anplay'),'click',function(){if(timer){stop();return}if(s>=12)s=0;$('anplay').textContent='Pause';step();timer=setInterval(function(){if(s>=12){stop();return}step()},750)});
  on($('anreset'),'click',function(){stop();s=0;draw()});
  draw();redraws.push(draw);
})();

/* passes */
(function(){
  var bb=X.bbox,svg=$('passsvg'),NS='http://www.w3.org/2000/svg',polys=[],sel=0;
  svg.setAttribute('viewBox',(bb[0]-6)+' '+(bb[1]-6)+' '+(bb[2]-bb[0]+12)+' '+(bb[3]-bb[1]+12));
  X.maplots.forEach(function(l){if(!l[4])return;var p=document.createElementNS(NS,'polygon');p.setAttribute('points',l[4].map(function(q){return q.join(',')}).join(' '));p._l=l;svg.appendChild(p);polys.push(p)});
  var g=document.createElementNS(NS,'g');svg.appendChild(g);
  var btns=$('passbtns');
  PASSES.forEach(function(p,i){var b=document.createElement('button');b.type='button';b.className='btn seg'+(i===0?' on':'');b.textContent='Pass '+p.n;on(b,'click',function(){sel=i;[].forEach.call(btns.children,function(x,j){x.classList.toggle('on',j===i)});paint()});btns.appendChild(b)});
  function paint(){
    var p=PASSES[sel],inr=[],drawn=0;
    polys.forEach(function(q){var h=q._l[3];if(h>=p.lo&&h<=p.hi){inr.push(q);drawn++;q.setAttribute('fill','hsl(40,62%,'+(82-52*(h-p.lo)/Math.max(1,p.hi-p.lo))+'%)')}else q.setAttribute('fill',css('--g3'))});
    g.innerHTML='';var lo=null,hi=null;inr.forEach(function(q){if(!lo||q._l[3]<lo._l[3])lo=q;if(!hi||q._l[3]>hi._l[3])hi=q});
    [[lo,'first'],[hi,'last']].forEach(function(e){if(!e[0])return;var c=document.createElementNS(NS,'circle');c.setAttribute('cx',e[0]._l[5]);c.setAttribute('cy',e[0]._l[6]);c.setAttribute('r',7);c.setAttribute('fill','#c5a448');c.setAttribute('stroke','#0b0b0a');c.setAttribute('stroke-width',2);g.appendChild(c);
      var t=document.createElementNS(NS,'text');t.setAttribute('x',e[0]._l[5]+10);t.setAttribute('y',e[0]._l[6]-10);t.setAttribute('style','font:700 22px var(--mono);fill:var(--fg);stroke:var(--bg);stroke-width:5px;paint-order:stroke');t.textContent=e[1]+' '+pad(e[0]._l[3]);g.appendChild(t)});
    $('passinfo').innerHTML='<h4 style="margin-top:0">Pass '+p.n+' · sections '+esc(p.secs)+'</h4><div class="out">'+pad(p.lo)+' to '+pad(p.hi)+'<br>'+fmt(p.hi-p.lo+1)+' positions<br>'+fmt(drawn)+' have an outline on the map</div><p>'+esc(p.how)+'</p><p class="note">Direction: light is the first lot, dark is the last. Inside the pass the path runs level by level, so color changes in bands across the section rather than along one line.</p>';
  }
  paint();redraws.push(paint);
  $('passes').innerHTML=PASSES.map(function(p,i){var w=(p.hi-p.lo+1)/3185*100;return '<div style="display:flex;align-items:center;gap:12px;margin:7px 0;flex-wrap:wrap"><div style="flex:0 0 150px"><b>Pass '+p.n+'</b><br><span class="note">'+esc(p.secs)+'</span></div><div style="flex:1 1 200px;background:var(--surf);border-radius:6px;height:22px;position:relative;border:1px solid var(--g3)"><div style="position:absolute;left:'+((p.lo-1)/3185*100)+'%;width:'+w+'%;height:100%;border-radius:5px;background:var(--gold);opacity:'+(.45+.1*i)+'"></div></div><div class="note mono" style="flex:0 0 190px">'+pad(p.lo)+' – '+pad(p.hi)+'</div></div>'}).join('')+'<p class="note">Where two sections share a pass, their levels are woven: level 1 of the first section, level 1 of the second, then level 2 of each. That is why one section\'s H-numbers are not one block. Pass 4 holds three margin lists and the G/H rows; the margins are numbered before G and H.</p>';
})();

/* address breakdown */
(function(){
  var inp=$('addrin'),def=inp.value;
  function run(){
    var v=inp.value.trim().toUpperCase().replace(/\s+/g,''),m=/^H(\d{6})([AB]?)(\d)?$/.exec(v),o=$('addrparts');
    if(!m){o.innerHTML='<p class="bad">Use the form H + six digits + optional A or B + optional grave digit, for example H001698A3.</p>';return}
    var lot=+m[1],refs=RV[lot],h='<div class="addr"><div class="p"><b>H</b><span>prefix</span></div><div class="p"><b>'+m[1]+'</b><span>lot (H-number)</span></div>'+(m[2]?'<div class="p"><b>'+m[2]+'</b><span>double-row half</span></div>':'')+(m[3]?'<div class="p"><b>'+m[3]+'</b><span>grave 1 to 9</span></div>':'')+'</div>';
    h+='<p>Lot '+pad(lot)+(lot>=1&&lot<=3185?' is position '+lot+' of 3,185 on the path.':' is outside the range 1 to 3,185.')+(refs?' Old references: '+refs.map(esc).join(', ')+'.':(lot>=1&&lot<=3185?' No legacy reference maps here.':''))+'</p>';
    if(m[3]&&!m[2])h+='<p class="note">Numeric form: 10 × '+lot+' + '+m[3]+' = '+(10*lot+ +m[3])+'.</p>';else if(m[2])h+='<p class="note">The numeric form 10 × lot + g would give '+(m[3]?10*lot+ +m[3]:'…')+', which has lost the letter '+m[2]+'. Keep the letter in the address.</p>';
    o.innerHTML=h}
  on(inp,'input',run);on($('addrreset'),'click',function(){inp.value=def;run()});run();
})();

/* ---------------- section 5: demo helper ---------------- */
function demo(id,ctrls,extraDirty,extraReset,rerun){
  var els=ctrls.map($),defs=els.map(function(e){return e.value}),tag=$(id+'mode');
  function upd(){var d=els.some(function(e,i){return e.value!==defs[i]})||(extraDirty&&extraDirty());tag.textContent=d?'Experiment':'Actual system';tag.classList.toggle('exp',!!d)}
  on($(id+'reset'),'click',function(){els.forEach(function(e,i){e.value=defs[i]});if(extraReset)extraReset();rerun();upd();toast('Example reset')});
  return {upd:upd};
}

/* P1 */
(function(){
  var ord='blocks',R0=19;
  function Hf(sec,r,c,N){var SW=2*N;return ord==='blocks'?SW*(r-1)+(sec==='B'?0:N)+c:SW*(r-1)+2*c-(sec==='B'?1:0)}
  var d;
  function run(){
    var N=+$('p1n').value,R=+$('p1r').value;$('p1nv').textContent=N;$('p1rv').textContent=R;
    var sec=$('p1sec').value,r0=+$('p1lv').value||1,c0=+$('p1c').value||1,r=Math.min(Math.max(1,r0),R),c=Math.min(Math.max(1,c0),N),clamp=(r!==r0||c!==c0);
    $('p1lv').max=R;$('p1c').max=N;
    var SW=2*N,Hs=Hf(sec,r,c,N);
    $('p1eqn').innerHTML=ord==='blocks'?'<span class="lbl">SWEEP  = </span>N<sub>B</sub> + N<sub>A</sub> = '+SW+'<br><span class="lbl">OFFSET = </span>SWEEP × R = '+SW*R+'<br><span class="lbl">H(B, r, c) = </span>SWEEP × (r − 1) + c<br><span class="lbl">H(A, r, c) = </span>SWEEP × (r − 1) + N<sub>B</sub> + c'
      :'<span class="lbl">SWEEP  = </span>N<sub>B</sub> + N<sub>A</sub> = '+SW+'<br><span class="lbl">OFFSET = </span>SWEEP × R = '+SW*R+'<br><span class="lbl">H(B, r, c) = </span>SWEEP × (r − 1) + 2c − 1<br><span class="lbl">H(A, r, c) = </span>SWEEP × (r − 1) + 2c';
    $('p1out').innerHTML='H('+sec+', level '+r+', column '+c+') = '+SW+' × '+(r-1)+(ord==='blocks'?(sec==='A'?' + '+N:''):'')+' + '+(ord==='blocks'?c:(sec==='B'?'2×'+c+'−1':'2×'+c))+' = <span class="hv">'+Hs+'</span> → '+pad(Hs)+'<br>Visited as lot '+Hs+' of '+SW*R+' in this pass.'+(clamp?'<br><span class="gold">Level and column were limited to 1–'+R+' and 1–'+N+'.</span>':'')+(ord==='blocks'&&N===22&&R===19&&!clamp?'':'');
    var cv=$('p1cv'),cx=cv.getContext('2d');cx.clearRect(0,0,cv.width,cv.height);
    var cw=(cv.width-60)/N,ch=Math.min(18,(cv.height-20)/(2*R+1));cv._g={cw:cw,ch:ch,N:N,R:R};
    ['B','A'].forEach(function(s,si){for(var rr=1;rr<=R;rr++)for(var cc=1;cc<=N;cc++){var h=Hf(s,rr,cc,N);cx.fillStyle='hsl('+Math.round(240-240*(h-1)/(2*N*R))+',60%,'+(s==='B'?50:62)+'%)';cx.fillRect(40+(cc-1)*cw,10+(si*(R+1)+rr-1)*ch,cw-1.5,ch-1.5)}});
    var si=sec==='B'?0:1;cx.strokeStyle=css('--fg');cx.lineWidth=4;cx.strokeRect(40+(c-1)*cw-1,10+(si*(R+1)+r-1)*ch-1,cw+1,ch+1);cx.strokeStyle='#c5a448';cx.lineWidth=2;cx.strokeRect(40+(c-1)*cw-1,10+(si*(R+1)+r-1)*ch-1,cw+1,ch+1);
    cx.fillStyle=css('--g5');cx.font='600 12px "IBM Plex Mono",monospace';cx.textAlign='left';cx.fillText('B',14,10+ch);cx.fillText('A',14,10+(R+1)*ch+ch);
    d.upd();
  }
  d=demo('p1',['p1n','p1r','p1sec','p1lv','p1c'],function(){return ord!=='blocks'},function(){ord='blocks';[].forEach.call(document.querySelectorAll('button[data-ord]'),function(x){x.classList.toggle('on',x.getAttribute('data-ord')==='blocks')})},run);
  ['p1n','p1r','p1sec','p1lv','p1c'].forEach(function(i){on($(i),'input',run)});
  [].forEach.call(document.querySelectorAll('button[data-ord]'),function(b){on(b,'click',function(){ord=b.getAttribute('data-ord');[].forEach.call(document.querySelectorAll('button[data-ord]'),function(x){x.classList.toggle('on',x===b)});run()})});
  on($('p1cv'),'mousemove',function(e){var cv=this,g=cv._g;if(!g)return;var r=cv.getBoundingClientRect(),x=(e.clientX-r.left)*cv.width/r.width-40,y=(e.clientY-r.top)*cv.height/r.height-10;var cc=Math.floor(x/g.cw)+1,row=Math.floor(y/g.ch),si=row>=g.R+1?1:0,rr=row-si*(g.R+1)+1;if(cc<1||cc>g.N||rr<1||rr>g.R){cv.title='';return}cv.title=(si?'A':'B')+' level '+rr+', column '+cc+' = '+Hf(si?'A':'B',rr,cc,g.N)});
  on($('p1cv'),'click',function(e){var cv=this,g=cv._g;if(!g)return;var r=cv.getBoundingClientRect(),x=(e.clientX-r.left)*cv.width/r.width-40,y=(e.clientY-r.top)*cv.height/r.height-10;var cc=Math.floor(x/g.cw)+1,row=Math.floor(y/g.ch),si=row>=g.R+1?1:0,rr=row-si*(g.R+1)+1;if(cc<1||cc>g.N||rr<1||rr>g.R)return;$('p1sec').value=si?'A':'B';$('p1lv').value=rr;$('p1c').value=cc;run()});
  run();redraws.push(run);
})();

/* P2 */
(function(){
  var d;
  function a(){
    var st=+$('p2inc').value,rows=Math.min(4,Math.max(1,+$('p2rows').value||1));$('p2incv').textContent=st;
    var tw=$('p2tw').value.split(',').map(function(x){return +x.trim()}).filter(function(x){return x>0&&x<=st}),out='',bad=0;
    for(var r=1;r<=rows;r++){var cells=[],plain=[];
      for(var q=1;q<=st;q++){var n=st*(r-1)+q,c0=20-q,c=c0+tw.filter(function(t){return q<=t}).length;plain.push({l:String(n),c:c0});cells.push({c:c,c0:c0,l:String(n),h:44*(r-1)+22+c});if(tw.indexOf(q)>=0)cells.push({c:c-1,l:n+'H',h:44*(r-1)+22+c-1,hl:1})}
      cells.sort(function(x,y){return x.h-y.h});var seen={};
      out+='<div class="note" style="margin-top:8px">Row '+r+', without H-lots: label at column</div><div class="chips">'+plain.sort(function(x,y){return x.c-y.c}).map(function(x){return '<span class="chip static">'+x.l+'@c'+x.c+'</span>'}).join('')+'</div>';
      out+='<div class="note" style="margin-top:8px">Row '+r+', with H-lots inserted (gold ◆), in H order. Blue ▲ marks a label pushed one column over.</div><div class="chips">'+cells.map(function(x){var dup=seen[x.h];seen[x.h]=1;if(dup)bad++;return '<span class="chip static '+(dup?'clash':x.hl?'h':x.c!==x.c0?'suffix':'')+'">'+x.l+'@c'+x.c+' → '+x.h+'</span>'}).join('')+'</div>'}
    out+=bad?'<p class="bad" style="margin-top:8px">'+bad+' clash(es): two lots got the same H-number. With the real rule (step 19, H-lots before places 13, 5 and 1) there are none.</p>':'<p class="good" style="margin-top:8px">No two lots share an H-number.</p>';
    $('p2out').innerHTML=out;d.upd();
  }
  d=demo('p2',['p2inc','p2tw','p2rows'],null,null,a);['p2inc','p2tw','p2rows'].forEach(function(i){on($(i),'input',a)});a();
  var d2;
  function b(){var s1=+$('p2b1').value,s2=+$('p2b2').value,f=+$('p2b3').value;$('p2b1v').textContent=s1;$('p2b2v').textContent=s2;$('p2b3v').textContent=f;
    var body={},last={},coll=[];for(var r=1;r<=19;r++){for(var q=1;q<s1;q++)body[s1*(r-1)+q]=r;last[f+s2*(r-1)]=r}
    Object.keys(last).forEach(function(l){if(body[l])coll.push(l)});
    $('p2bout').innerHTML='row 1 body labels: 1 … '+(s1-1)+'<br>last column: '+f+', '+(f+s2)+', … , '+(f+18*s2)+'<br>'+(coll.length?'<span class="bad">'+coll.length+' last-column labels collide with a body label ('+coll.slice(0,6).join(', ')+(coll.length>6?' …':'')+')</span>':'<span class="good">No label is used twice.</span>')+'<br>Real values are 20, 19 and 12; collisions there are resolved by "later rule wins".'}
  ['p2b1','p2b2','p2b3'].forEach(function(i){on($(i),'input',b)});b();
  on($('p2reset'),'click',function(){$('p2b1').value=20;$('p2b2').value=19;$('p2b3').value=12;b()});
})();

/* P3 */
(function(){
  var mode='real',wd=W.WD.concat([0]).slice(0,24),wc=W.WC.slice(),d;
  function start(r,s){return 837+pf2(wd,wc,r)+(s==='C'?(wd[r-1]||0):0)}
  function realStart(r,s){return 837+pf2(W.WD.concat([0]),W.WC,r)+(s==='C'?(W.WD[r-1]||0):0)}
  function tab(){
    var h='<tr><th>Row</th><th>W<sub>D</sub></th><th>W<sub>C</sub></th><th>D starts at</th><th>C starts at</th></tr>';
    for(var r=1;r<=24;r++){var sd=start(r,'D'),sc=start(r,'C');h+='<tr><td>'+r+'</td><td><input type="number" min="0" data-s="d" data-r="'+(r-1)+'" value="'+(wd[r-1]||0)+'" style="width:76px;min-height:34px"></td><td><input type="number" min="0" data-s="c" data-r="'+(r-1)+'" value="'+wc[r-1]+'" style="width:76px;min-height:34px"></td><td class="num'+(sd!==realStart(r,'D')?' shift':'')+'">'+sd+'</td><td class="num'+(sc!==realStart(r,'C')?' shift':'')+'">'+sc+'</td></tr>'}
    $('p3tab').innerHTML=h;
    [].forEach.call($('p3tab').querySelectorAll('input'),function(i){on(i,'change',function(){(i.getAttribute('data-s')==='d'?wd:wc)[+i.getAttribute('data-r')]=+i.value||0;tab();out()})});
  }
  function dirty(){return mode!=='real'||W.WD.concat([0]).some(function(v,i){return v!==wd[i]})||W.WC.some(function(v,i){return v!==wc[i]})}
  function out(){
    var s=$('p3sec').value,r=Math.min(24,Math.max(1,+$('p3r').value||1)),k=Math.max(1,+$('p3k').value||1),w=(s==='C'?wc[r-1]:wd[r-1])||0;
    $('p3kmax').textContent='(row has '+w+' places)';
    var H=start(r,s)-1+k,end=836+wd.reduce(function(a,b){return a+b},0)+wc.reduce(function(a,b){return a+b},0);
    $('p3out').innerHTML='H('+s+', row '+r+', place '+k+') = 836 + '+pf2(wd,wc,r)+(s==='C'?' + '+(wd[r-1]||0):'')+' + '+k+' = <span class="hv">'+H+'</span> → '+pad(H)+(k>w?'<br><span class="bad">Row '+r+' of '+s+' has only '+w+' places, so place '+k+' is past the end of the row.</span>':'')+'<br>Pass 2 ends at <b>'+end+'</b>'+(end!==1871?' <span class="bad">(real value 1871; every later pass would shift by '+(end-1871)+')</span>':' (matches the real 1871)');
    d.upd();
  }
  function setW(m){mode=m;[].forEach.call(document.querySelectorAll('button[data-w]'),function(x){x.classList.toggle('on',x.getAttribute('data-w')===m)});
    if(m==='ideal'){wd=[];wc=[];for(var i=0;i<24;i++){wd.push(i<19?22:0);wc.push(i<19?22:0)}}else{wd=W.WD.concat([0]).slice(0,24);wc=W.WC.slice()}}
  function run(){tab();out()}
  d=demo('p3',['p3sec','p3r','p3k'],dirty,function(){setW('real')},run);
  [].forEach.call(document.querySelectorAll('button[data-w]'),function(b){on(b,'click',function(){setW(b.getAttribute('data-w'));run()})});
  ['p3sec','p3r','p3k'].forEach(function(i){on($(i),'input',out)});run();
})();

/* P4 */
(function(){
  var d,CT=W.CT;
  function realTw(r){return (W.CTW[r]||[]).map(function(x){return x[0]+x[1]}).join(',')}
  function realTrio(r){return W.TR.indexOf(r)>=0?'1':'0'}
  function load(r){$('p4tw').value=realTw(r);$('p4trio').value=realTrio(r)}
  function calc(row,tw,trio){
    var top=CT[row-1],lo=row>1?CT[row-2]+1:1,base=836+pf2(W.WD.concat([0]),W.WC,row)+(W.WD[row-1]||0),L=[];
    function cnt(n){return tw.filter(function(w){return w[0]>n||(w[0]===n&&!w[1])}).length}
    for(var n=top;n>=lo;n--){var k=top-n+1+(trio?3:0)+cnt(n);L.push([String(n),base+k]);var t=tw.filter(function(w){return w[0]===n})[0];if(t)L.push([n+'H',base+k+(t[1]?1:-1)])}
    if(trio)['C','B','A'].forEach(function(s,i){L.push([top+s,base+i+1])});
    return L.sort(function(a,b){return a[1]-b[1]});
  }
  function run(){
    var row=Math.min(24,Math.max(1,+$('p4row').value||1)),trio=$('p4trio').value==='1';
    var tw=$('p4tw').value.split(',').map(function(s){s=s.trim();var m=/^(\d+)([ab]?)$/.exec(s);return m?[+m[1],m[2]==='a'?1:0]:null}).filter(Boolean);
    var L=calc(row,tw,trio),seen={},dup=0;
    var h='<div class="note">Row '+row+' of C, top lot '+CT[row-1]+', in H order. Gold ◆ = H-lot, blue ▲ = trio lot.</div><div class="chips" style="margin-top:6px">'+L.map(function(x){var dd=seen[x[1]];seen[x[1]]=1;if(dd)dup++;return '<span class="chip static '+(dd?'clash':/H$/.test(x[0])?'h':/[ABC]$/.test(x[0])?'suffix':'')+'">'+x[0]+' → '+x[1]+'</span>'}).join('')+'</div>';
    var real=0,mis=0;L.forEach(function(x){var v=FW['C|'+x[0]];if(v!=null){real++;if(v!==x[1])mis++}});
    h+='<p class="note" style="margin-top:8px">'+(real?real+' of these labels exist in the decoder; '+(mis?'<span class="bad">'+mis+' differ from it</span>':'<span class="good">all agree with it</span>'):'None of these labels exist in the real section C, so this is a what-if.')+(dup?' <span class="bad">'+dup+' clash(es)</span>':'')+'</p>';
    $('p4out').innerHTML=h;
    var dirty=$('p4tw').value.replace(/\s/g,'')!==realTw(row)||$('p4trio').value!==realTrio(row)||row!==3;var t=$('p4mode');t.textContent=($('p4tw').value.replace(/\s/g,'')!==realTw(row)||$('p4trio').value!==realTrio(row))?'Experiment':'Actual system';t.classList.toggle('exp',t.textContent==='Experiment');
  }
  on($('p4row'),'input',function(){var r=Math.min(24,Math.max(1,+$('p4row').value||1));load(r);run()});
  ['p4tw','p4trio'].forEach(function(i){on($(i),'input',run)});
  on($('p4reset'),'click',function(){$('p4row').value=3;load(3);run();toast('Example reset')});
  load(3);run();
})();

/* P5 */
(function(){
  var R={J:[1,132,57,'2950 + n'],I:[1,64,30,'3082 + n'],L:[69,107,80,'3146 + (n − 68)'],M:[82,279,100,'n + 2556'],F:[1,210,100,'1871 + earlier rows + k  (margin 199 to 210: n + 2203)']};
  function setRange(){var s=$('p5sec').value;$('p5range').textContent='(valid: '+R[s][0]+' to '+R[s][1]+(s==='M'?', and 51 listed lots below 82':'')+')'}
  function run(){var s=$('p5sec').value,n=$('p5n').value.trim(),H=GH(s,n),t=TR[s+'|'+n];setRange();
    $('p5out').innerHTML=(typeof H==='number'&&!isNaN(H))?'H('+s+', '+esc(n)+') = <span class="hv">'+H+'</span> → '+pad(H)+'<br>rule: '+R[s][3]+(t?'<br>derived by '+TIERTXT[t[2]]:'')+(FW[s+'|'+n]===H?'<br><span class="good">The decoder returns the same value.</span>':'<br><span class="bad">The decoder does not list this label.</span>'):'<span class="bad">Section '+s+' has no lot '+esc(n)+'. Valid range: '+R[s][0]+' to '+R[s][1]+'.</span>';
    var t2=$('p5mode');t2.textContent='Actual system';t2.classList.remove('exp')}
  on($('p5sec'),'input',function(){$('p5n').value=R[$('p5sec').value][2];run()});on($('p5n'),'input',run);
  on($('p5reset'),'click',function(){$('p5sec').value='J';$('p5n').value=57;run();toast('Example reset')});run();
})();

/* P6 */
(function(){
  var d;
  function run(){var h=Math.max(1,Math.min(3185,Math.round(+$('p6h').value||1))),g=Math.min(9,Math.max(1,Math.round(+$('p6g').value||1))),sf=$('p6s').value,hp=String(h).padStart(6,'0');
    $('p6parts').innerHTML='<div class="addr"><div class="p"><b>H</b><span>prefix</span></div><div class="p"><b>'+hp+'</b><span>lot (H-number)</span></div>'+(sf?'<div class="p"><b>'+sf+'</b><span>double-row half</span></div>':'')+'<div class="p"><b>'+g+'</b><span>grave</span></div></div>';
    $('p6out').innerHTML='address: <span class="hv">H'+hp+sf+g+'</span>'+(sf?'<br>numeric form 10 × '+h+' + '+g+' = '+(10*h+g)+' drops the letter '+sf+'; keep it in the address.':'<br>numeric form: 10 × '+h+' + '+g+' = <b>'+(10*h+g)+'</b>')+(RV[h]?'<br>old references to this lot: '+RV[h].map(esc).join(', '):'');d.upd()}
  d=demo('p6',['p6h','p6g','p6s'],null,null,run);['p6h','p6g','p6s'].forEach(function(i){on($(i),'input',run)});run();
})();

/* ---------------- section 6: snippets ---------------- */
(function(){
  var inDoc;
  function hlLine(l){var e=esc(l);if(inDoc){if(/"""/.test(l))inDoc=false;return '<span class="c">'+e+'</span>'}
    if((l.match(/"""/g)||[]).length===1){inDoc=true;return e.replace(/("""[\s\S]*)/,'<span class="c">$1</span>')}
    return e.replace(/(#.*$)|(&quot;[^&]*?&quot;|"[^"]*"|'[^']*')|\b(def|return|if|elif|else|for|in|not|and|or|is|None|True|False|import|from|lambda|while|raise|class|continue|break)\b|\b(\d+)\b/g,function(m,cm,st,kw,nu){return cm?'<span class="c">'+cm+'</span>':st?'<span class="s">'+st+'</span>':kw?'<span class="k">'+kw+'</span>':'<span class="n">'+nu+'</span>'})}
  var h='',all=[];
  X.snips.forEach(function(g){h+='<h3><i class="tri"></i>'+esc(g.title)+'</h3><p class="note">'+esc(g.note)+'</p>';
    g.items.forEach(function(s,i){var idx=all.push(s.src)-1;inDoc=false;var body=s.src.split('\n').map(function(l){return '<span class="ln">'+hlLine(l)+'</span>'}).join('');
      h+='<div class="snip"><header><div><b>'+esc(s.name)+'</b> <span class="tag">'+esc(s.file)+'</span><p>'+esc(s.desc||'')+'</p>'+(s.demo?'<p class="note">Implements: <a href="'+esc(s.demo[1])+'">'+esc(s.demo[0])+'</a></p>':'')+'</div><button class="btn sm" type="button" data-cp="'+idx+'">Copy</button></header><details'+(i<1?' open':'')+' style="border:0;border-top:1px solid var(--g3);border-radius:0;margin:0;padding:0"><summary style="padding:8px 14px">'+(s.src.split('\n').length)+' lines</summary><pre class="code">'+body+'</pre></details></div>'})});
  $('snips').innerHTML=h;
  [].forEach.call($('snips').querySelectorAll('[data-cp]'),function(b){on(b,'click',function(){copyText(all[+b.getAttribute('data-cp')])})});
})();
function copyText(t){
  function fb(){var ta=document.createElement('textarea');ta.value=t;ta.style.cssText='position:fixed;left:-999px';document.body.appendChild(ta);ta.select();var ok=false;try{ok=document.execCommand('copy')}catch(e){}document.body.removeChild(ta);toast(ok?'Copied':'Select the text and copy')}
  try{if(navigator.clipboard){navigator.clipboard.writeText(t).then(function(){toast('Copied')},fb)}else fb()}catch(e){fb()}
}

/* ---------------- section 7 ---------------- */
(function(){
  var gs=$('gs');gs.innerHTML=SEC.map(function(s){return '<option>'+s+'</option>'}).join('');gs.value='B';
  var RULE={A:'Section A: 19 labels per row, counted right to left; H-lots before places 13, 5 and 1.',B:'Section B: body of 20 per row; last column steps by 19; margin labels come from a stored list.',C:'Section C: row tops, twins and trios from per-row tables.',D:'Section D: 20 per row, blocks in rows 16 to 23, letter labels in row 1, margin from a list.',E:'Section E: 19 per row with twins, plus lettered lots in rows 9 to 12.',F:'Section F: 18 per row; margin 199 to 210.',G:'Section G: 19 per row, plus lots 58 to 75.',H:'Section H: 23 per row.',I:'Section I: straight run 1 to 64.',J:'Section J: straight run 1 to 132.',K:'Section K: a stored list of 115 lots.',L:'Section L: straight run 69 to 107.',M:'Section M: first 51 lots from a list, then 82 to 279 straight.'};
  var BASE={A:'22 (the A half of each 44-lot level)',B:'0',C:'836',D:'836',E:'1871',F:'1871',G:'2413',H:'2413',I:'3082',J:'2950',K:'2835',L:'3078',M:'2556 or 2586'};
  function offsetText(S,H,t){
    var r=t&&t[0],k=t&&t[1];if(r==null||k==null)return 'H − place = '+(t&&t[1]!=null?H-t[1]:'—')+' lots visited before this lot (a straight run or a stored list, so no per-level table is involved).';
    var off=H-k,note='';
    if(S==='A'||(S==='B'&&H<=836))note='44 × '+(r-1)+' + '+(S==='A'?22:0);
    else if(S==='D'||S==='C'){var e=836+pf2(W.WD.concat([0]),W.WC,r)+(S==='C'?(W.WD[r-1]||0):0);if(e===off)note='836 + '+pf2(W.WD.concat([0]),W.WC,r)+(S==='C'?' + '+W.WD[r-1]:'')+': base, earlier levels'+(S==='C'?', and this level of D':'')}
    else if(S==='F'||S==='E'){var e2=1871+pf2(W.WF,W.WE,r)+(S==='E'?(W.WF[r-1]||0):0);if(e2===off)note='1871 + '+pf2(W.WF,W.WE,r)+(S==='E'?' + '+W.WF[r-1]:'')+': base, earlier levels'+(S==='E'?', and this level of F':'')}
    else if(S==='G'||S==='H'){var e3=2413+pf2(W.WG,W.WH,r)+(S==='H'?(W.WG[r-1]||0):0);if(e3===off)note='2413 + '+pf2(W.WG,W.WH,r)+(S==='H'?' + '+W.WG[r-1]:'')+': base, earlier levels'+(S==='H'?', and this level of G':'')}
    return 'Offset = H − place = <b>'+off+'</b> lots visited before this level'+(note?' ('+note+')':'')+'.';
  }
  function run(){
    var S=gs.value,L=$('gl').value.trim(),m=/^([A-Z]?)([0-9]+)(.*)$/.exec(L.toUpperCase()),v=GH(S,L.toUpperCase()),exp=FW[S+'|'+L.toUpperCase()],ok=typeof v==='number'&&!isNaN(v),res;
    if(ok&&exp===v)res='<div class="big">'+pad(v)+'<small>'+v+' of 3,185</small></div><p><span class="tag ok">Accepted decoder label</span> The decoder lists '+S+'-'+esc(L.toUpperCase())+' and gives the same number.</p><p class="note">Graves: '+pad(v)+'1 to '+pad(v)+'9.</p>';
    else if(ok)res='<div class="big">'+pad(v)+'<small>'+v+'</small></div><p><span class="tag gold">In range only</span> The formula returns a number, but the decoder does not list '+S+'-'+esc(L.toUpperCase())+'. Treat this as a calculation, not as a confirmed lot.</p>';
    else res='<p><span class="tag bad">No result</span> No lot '+S+'-'+esc(L)+' exists in the formula\'s ranges'+(exp!=null?' (but the decoder lists it as '+exp+')':'')+'.</p>';
    $('gres').innerHTML=res;
    var t=TR[S+'|'+L.toUpperCase()],tr='<details'+(ok?' open':'')+'><summary>Show the working</summary><ol class="trace">';
    tr+='<li><div><b>Parse the label</b>prefix "'+(m?esc(m[1]):'')+'", number '+(m?+m[2]:'none')+', suffix "'+(m?esc(m[3]):'')+'"'+(m&&m[1]?' (a letter in front means the label borrows another section\'s letter)':'')+'</div></li>';
    tr+='<li><div><b>Pick the section rule</b>'+esc(RULE[S])+(t?' This label is handled by '+TIERTXT[t[2]]+'.':'')+'</div></li>';
    tr+='<li><div><b>Find the level and position</b>'+(t&&t[0]!=null?'level '+t[0]+', place '+t[1]+' (decoder indexing)':(t?'place '+t[1]+' along the run':(ok?'computed directly':'not found'))+'')+'</div></li>';
    tr+='<li><div><b>Add the offset</b>'+(ok&&t?offsetText(S,v,t):ok?'The label is not in the decoder table, so there is no stored place to show.':'—')+'</div></li>';
    tr+='<li><div><b>Result</b>'+(ok?'H = offset + place = <b>'+v+'</b>, written '+pad(v):'no H-number')+'</div></li></ol><details style="margin-top:8px"><summary>Show this section\'s raw expression</summary><pre class="code" style="white-space:pre-wrap;word-break:break-all"><span class="ln">'+esc(X.giant.parts[S]||'')+'</span></pre></details></details>';
    $('gtrace').innerHTML=tr;
  }
  on(gs,'change',run);on($('gl'),'input',run);
  var ex=[['B','20H'],['A','1'],['C','417'],['D','1H'],['E','199BH'],['G','61'],['K','57'],['M','100'],['J','132'],['L','107'],['F','210'],['B','384HA'],['D','563']],ei=0;
  on($('gex'),'click',function(){var e=ex[ei++%ex.length];gs.value=e[0];$('gl').value=e[1];run()});
  on($('greset'),'click',function(){gs.value='B';$('gl').value='20H';ei=0;run()});run();
  function rev(){var h=Math.round(+$('gh').value),r=RV[h];
    if(!(h>=1&&h<=3185)){$('grev').innerHTML='<p class="bad">H-numbers run from 1 to 3,185.</p>';return}
    if(!r){$('grev').innerHTML='<div class="big">'+pad(h)+'</div><p><span class="tag bad">No old reference</span> This position has no legacy label. It is one of the '+X.missingH.length+' gaps listed in section 09.</p>';return}
    var nums=r.map(function(x){return x.split('-').slice(1).join('-')}),base=nums[0].replace(/[AB]$/,''),halves=r.length>1&&nums.every(function(x){return x.replace(/[AB]$/,'')===base});
    $('grev').innerHTML='<div class="big">'+pad(h)+'</div><div class="chips" style="margin:8px 0">'+r.map(function(x){return '<span class="chip static">'+esc(x)+'</span>'}).join('')+'</div>'+(r.length===1?'<p>One legacy reference.</p>':halves?'<p>'+r.length+' references share this number. They differ only by an A or B suffix. In the decoder they are the two halves of one double-row lot and its plain label. Graves keep the letter: '+pad(h)+'A1, '+pad(h)+'B1.</p>':'<p>'+r.length+' references share this number. They are not simple A/B halves, so confirm in the field whether they are aliases of one lot.</p>')}
  on($('gh'),'input',rev);rev();
  var K=[['A','n → r = ⌈n/19⌉, q = n − 19(r−1); c = 20 − q + [q≤13] + [q≤5] + [q≤1] − [H-lot]','44(r−1) + 22 + c'],['B','body: r = ⌈n/20⌉, c = 20r − n; last column: r = (n−12)/19 + 1','44(r−1) + 22 + c; H-lot 20r: 44(r−1) + 1'],['C','k = (top_r − n) + 1 + 3·[trio] + #twins above','836 + Σ(W_D+W_C) + W_D(r) + k'],['D','by block (r, k₀, hi, lo): k = k₀ + hi − n; H-lots by row','836 + Σ(W_D+W_C) + k'],['E','k = 20 − q + [q≤13] + [q≤9] + [q≤5]; blocks in rows 9 to 12','1871 + Σ(W_F+W_E) + W_F(r) + k'],['F','k = 19 − (n − 18(r−1))','1871 + Σ(W_F+W_E) + k'],['G','k = 19r − n + (3 or 4) by side of H-lots','2413 + Σ(W_G+W_H) + k'],['H','k = 23r + 1 − n','2413 + Σ(W_G+W_H) + W_G(r) + k'],['M','n + 2556 for n ≥ 82; position in list otherwise','2586 + position'],['K','position of n in an ordered list of 115','2835 + position'],['J','n','2950 + n'],['I','n','3082 + n'],['L','n − 68','3146 + n − 68']];
  $('kappa').innerHTML='<tr><th>Section</th><th>place on the level κ(ℓ)</th><th>H</th></tr>'+K.map(function(k){return '<tr><td><b>'+k[0]+'</b></td><td>'+esc(k[1])+'</td><td>'+esc(k[2])+'</td></tr>'}).join('');
  var full='H = (S, L) => {\n  var m,p,n,f,r,q,c,k,i,j,g,b;\n'+X.giant.decl.split(';').map(function(d){return '  '+d+';'}).join('\n')+'\n  return '+X.giant.expr+';\n}';
  $('giantsrc').textContent=full;on($('cpg'),'click',function(){copyText(full)});
  var dec0=X.giant.decl.split(';').join('\n');$('consts').value=dec0;
  function chk(decl){var fn,moved=0,nan=0,ex=[];try{fn=compile(decl.replace(/\n/g,';'))}catch(e){return '<span class="bad">Syntax error: '+esc(e.message)+'</span>'}
    FWD.forEach(function(r){var v;try{v=fn(r[0],r[1])}catch(e){v=NaN}if(v!==r[2]){if(typeof v!=='number'||isNaN(v))nan++;else moved++;if(ex.length<8)ex.push(r[0]+'-'+r[1]+': '+r[2]+' → '+v)}});
    return moved+nan===0?'<span class="good">All '+fmt(FWD.length)+' real labels still match the decoder.</span>':'<span class="bad">'+moved+' H-numbers moved, '+nan+' labels no longer resolve</span> (of '+fmt(FWD.length)+').<br>'+ex.map(esc).join('<br>')}
  on($('capply'),'click',function(){$('cres').innerHTML=chk($('consts').value.trim())});
  on($('creset'),'click',function(){$('consts').value=dec0;$('cres').innerHTML=chk(dec0)});
  $('cres').innerHTML=chk(dec0);
})();

/* ---------------- section 8 ---------------- */
(function(){
  var pairs=[['overview','Whole map','1200 / 630',['Before: dark title blocks sit on top of the lots they name, and the legacy notes crowd the margins.','After: no title blocks over lots. Roads, buildings and lot outlines are kept in muted colors.','Outlines are thin, so the lot grid is readable at this scale.']],
    ['dense','Straight rows','1000 / 640',['Before: each number is drawn as an outlined shape, and the old and new numbers overlap (look at 2193 and 2033).','After: one number per lot, in a clean typeface, inside the lot outline.','Contrast improved: dark numerals on a plain lot face. Small lots get smaller numbers.']],
    ['curved','Curved rows and a section title','1000 / 640',['Before: the section title ("SECTION") runs across the numbers, and numbers cross lot edges.','After: the title is gone and each number sits inside its lot.','In the straight blocks the numbers read left to right. In curved rows they turn with the lot, so the reading direction follows the row.']]];
  var h='';pairs.forEach(function(p,i){h+='<div class="cmp" id="cmp'+i+'"><h3 style="margin-top:0"><i class="tri"></i>'+p[1]+'</h3>'
    +'<div class="row" style="margin:0 0 10px"><div style="flex:0 0 auto"><button class="btn seg on" data-m="slide" type="button">Slider</button><button class="btn seg" data-m="side" type="button">Side by side</button></div><div class="slideonly"><label class="f" for="rv'+i+'">Divider: left is before, right is after</label><input id="rv'+i+'" type="range" min="0" max="100" value="50"></div><div class="slideonly"><label class="f" for="zm'+i+'">Zoom <span id="zv'+i+'">1×</span></label><input id="zm'+i+'" type="range" min="1" max="4" step="0.25" value="1"></div><div style="flex:0 0 auto"><button class="btn sm" data-r="1" type="button">Reset view</button></div></div>'
    +'<div class="cmpview" style="aspect-ratio:'+p[2]+'"><div class="pan"><img src="'+IMG['new_'+p[0]]+'" alt="After: '+p[1]+'"><div class="top"><img src="'+IMG['old_'+p[0]]+'" alt="Before: '+p[1]+'"></div></div><div class="dv"></div><span class="lab" style="left:8px">Before</span><span class="lab" style="right:8px">After</span></div>'
    +'<div class="sidebox"><div><span class="tag legacy">Before</span><img src="'+IMG['old_'+p[0]]+'" alt="Before: '+p[1]+'"></div><div><span class="tag gold">After</span><img src="'+IMG['new_'+p[0]]+'" alt="After: '+p[1]+'"></div></div>'
    +'<ul class="calls" style="margin-top:10px">'+p[3].map(function(t,j){return '<li><i>'+(j+1)+'</i>'+esc(t)+'</li>'}).join('')+'</ul></div>'});
  $('cmps').innerHTML=h;
  pairs.forEach(function(p,i){var box=$('cmp'+i),view=box.querySelector('.cmpview'),pan=view.querySelector('.pan'),top=view.querySelector('.top'),dv=view.querySelector('.dv'),rv=$('rv'+i),zm=$('zm'+i),z=1,tx=0,ty=0,drag=null;
    function clamp(){var w=view.clientWidth,hh=view.clientHeight;tx=Math.min(0,Math.max(w-w*z,tx));ty=Math.min(0,Math.max(hh-hh*z,ty))}
    function apply(){clamp();pan.style.transform='translate('+tx+'px,'+ty+'px) scale('+z+')';$('zv'+i).textContent=z+'×';var v=+rv.value;top.style.clipPath='inset(0 '+(100-v)+'% 0 0)';dv.style.left=Math.max(0,Math.min(100,(tx+(v/100)*view.clientWidth*z)/view.clientWidth*100))+'%'}
    on(rv,'input',apply);on(zm,'input',function(){var w=view.clientWidth,hh=view.clientHeight,cx=(w/2-tx)/z,cy=(hh/2-ty)/z;z=+zm.value;tx=w/2-cx*z;ty=hh/2-cy*z;apply()});
    on(view,'pointerdown',function(e){drag={x:e.clientX,y:e.clientY,tx:tx,ty:ty,moved:false,rx:view.getBoundingClientRect()};view.setPointerCapture(e.pointerId);view.style.cursor='grabbing'});
    on(view,'pointermove',function(e){if(!drag)return;var dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.abs(dx)+Math.abs(dy)>3)drag.moved=true;if(z>1){tx=drag.tx+dx;ty=drag.ty+dy;apply()}else{var r=view.getBoundingClientRect();rv.value=Math.max(0,Math.min(100,(e.clientX-r.left)/r.width*100));apply()}});
    on(view,'pointerup',function(e){if(drag&&!drag.moved){var r=view.getBoundingClientRect(),vx=(e.clientX-r.left-tx)/z/r.width*100;rv.value=Math.max(0,Math.min(100,vx));apply()}drag=null;view.style.cursor='grab'});
    on(view,'keydown',function(){});
    [].forEach.call(box.querySelectorAll('[data-m]'),function(b){on(b,'click',function(){box.classList.toggle('side',b.getAttribute('data-m')==='side');[].forEach.call(box.querySelectorAll('[data-m]'),function(x){x.classList.toggle('on',x===b)})})});
    on(box.querySelector('[data-r]'),'click',function(){z=1;tx=ty=0;zm.value=1;rv.value=50;apply()});apply();window.addEventListener('resize',apply)});
  var rows=[['One name per lot','A section plus a label names a lot. The label alone does not: '+A.labels_in_2plus_sections+' of '+A.distinct_labels+' label strings are used by two or more sections.','One number from 1 to 3,185 names a position. Graves add one digit, and a double-row half adds A or B.'],
   ['Same rule everywhere','No. Each of the 13 sections counts in its own way (section 03).','One rule: position along the path.'],
   ['Order','Restarts in every section and jumps within one.','Rises by 1 along the path, by construction.'],
   ['Reading it on the map','Tiny, sideways, sometimes carrying another section\'s letter. The overall map has no lot numbers.','Larger, inside the lot, with the section titles removed.'],
   ['Finding a lot from the number','Needs the section, then that section\'s rule.','A single numeric lookup. Expected to be faster; not measured.'],
   ['Fewer mistakes','Several known ambiguities (section 03, C).','Expected to help, since there is one format. Not measured.'],
   ['Where the complexity lives','In the labels people read.','In the conversion tables that map old labels to H-numbers (section 07). Those tables still hold the exceptions.']];
  $('cmpt').innerHTML='<tr><th>Question</th><th>Legacy labels</th><th>H-numbers</th></tr>'+rows.map(function(r){return '<tr><td><b>'+r[0]+'</b></td><td>'+r[1]+'</td><td>'+r[2]+'</td></tr>'}).join('');
})();

/* ---------------- section 9 ---------------- */
(function(){
  var v=A.verify,t=v.tiers,ok=0,okAll;FWD.forEach(function(r){if(GH(r[0],r[1])===r[2])ok++});
  $('verify').innerHTML='<div class="grid3"><div class="stat"><span class="tag">Stored result · Python</span><div class="n" style="margin-top:6px">'+fmt(v.matched)+' / '+fmt(v.total)+'</div><div class="l">entries where hformula.py equals the decoder. Counts both internal keys. Run by verify.py.</div></div><div class="stat"><span class="tag">Stored result · Node</span><div class="n" style="margin-top:6px">3,197 / 3,197</div><div class="l">real labels where the one-line JavaScript equals the decoder. The two internal keys are left out. Run by test_giant.js.</div></div><div class="stat"><span class="tag ok">Live · this page</span><div class="n" style="margin-top:6px" id="livechk">'+fmt(ok)+' / '+fmt(FWD.length)+'</div><div class="l">real labels checked in your browser just now with the formula above.</div></div></div><p class="note">Coverage by kind: '+t.closed+' arithmetic, '+t.rows+' row constants, '+t.list+' stored lists, '+t.errata+' errata (3,199 entries).</p><p>The two internal keys are <code>152dr</code> and <code>169dr</code> in Section E. They are bookkeeping entries, not lots.</p>';
  var miss=X.missingH,p1=new Set(A.unlabeled_positions.pass1),extra=miss.filter(function(h){return !p1.has(h)}),mult=Object.keys(RV).filter(function(h){return RV[h].length>1}),tri=mult.filter(function(h){return RV[h].length===3}).length;
  $('complete').innerHTML='<p>The decoder has <b>'+fmt(FWD.length)+'</b> real labels (3,199 entries with the two internal keys). They map to <b>'+fmt(Object.keys(RV).length)+'</b> distinct H-numbers, because '+mult.length+' H-numbers have more than one reference: '+tri+' double-row lots with three references each (n, nA, nB) and '+(mult.length-tri)+' with two. Out of 3,185 positions, <b>'+miss.length+'</b> have no legacy reference.</p><div class="grid2"><div class="card"><b>'+p1.size+'</b> are the unlabeled grid positions in the B/A sweep found by the analysis.<div class="chips" style="margin-top:8px">'+A.unlabeled_positions.pass1.map(function(h){return '<span class="chip static">'+h+'</span>'}).join('')+'</div></div><div class="card"><b>'+extra.length+'</b> more, so the 36 are only part of the total.<div class="chips" style="margin-top:8px">'+extra.map(function(h){return '<span class="chip static">'+h+'</span>'}).join('')+'</div><p class="note" style="margin-top:8px">H000793 and H000795 to H000801 sit at the end of pass 1. H001473 is in C and H002416 is in the G margin.</p></div></div>';
  var er=[['Duplicate keys','D-274, G-19','One of each pair is shadowed','Decoder keeps the later entry; formula follows it','Decide which lot each entry meant'],['Typo in a row table','C-124H (pattern says 142H)','A lookup for C-142H finds nothing','Formula maps 124H to the 142H position','Confirm on the map'],['Labels claimed twice','B-373 to B-379','Grid positions lose their own label','Later rule (the margin list) wins','Rule which lot each label means'],['Internal keys','E-152dr, E-169dr','Counted in 3,199, not real lots','Left out of the live check','Remove from the decoder or document them'],['Traversal order','B and A, pass 1','Document says alternate columns; code does whole levels','Code order used; every verified number follows it','Choose the authoritative order'],['Idealised grid','C, reference sheet','C-417 is H001672 on the sheet and H001871 in the decoder','Decoder uses the real rows','Retire or update the sheet'],['Pass boundary','H and M','Earlier summaries put M at H002586; it begins at H002587','This page computes pass ranges from the data','Check other documents that quote it']];
  $('errata').innerHTML='<table class="t"><tr><th>Issue</th><th>Affected references</th><th>Consequence</th><th>Current handling</th><th>Decision needed</th></tr>'+er.map(function(r){return '<tr>'+r.map(function(c,i){return '<td'+(i===0?' style="white-space:nowrap"><b>'+c+'</b>':'>'+c)+'</td>'}).join('')+'</tr>'}).join('')+'</table><p class="note" style="margin-top:10px">"Later entry wins" describes what the software does. It does not show that the underlying conflict is settled.</p>';
  var dec=[['Which traversal order is authoritative?','Whole level of B then A (what the code does) or alternating columns (what the reference PDF says). Everything in pass 1 depends on this.'],['Which exceptions get reviewed first?','Suggested order: the 5 label conflicts in the errata table, then the 46 positions with no reference, then the double-row lots.'],['How will the numbers be verified on the ground?','Agreement with the decoder is done. Someone has to walk a sample of lots in each pass and confirm the H-number sits on the right lot.'],['What are the rules for future additions?','How a new lot or a re-cut lot gets a number without disturbing the order: append after H003185, insert and renumber, or reserve gaps.']];
  $('decisions').innerHTML=dec.map(function(d,i){return '<div class="def"><span class="tag gold">Decision '+(i+1)+'</span> <b>'+d[0]+'</b><p style="margin:6px 0 0">'+d[1]+'</p></div>'}).join('');
})();
})();
