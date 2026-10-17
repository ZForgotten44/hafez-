/* passes: the whole map, muted gold shading, and a simulation through all six */
(function(){
  var bb=X.bbox,svg=$('passsvg'),NS='http://www.w3.org/2000/svg',polys=[],sel=0,sim=0,raf=0,cursor=null;
  svg.setAttribute('viewBox',(bb[0]-6)+' '+(bb[1]-6)+' '+(bb[2]-bb[0]+12)+' '+(bb[3]-bb[1]+12));
  LOTS.forEach(function(l){var p=document.createElementNS(NS,'polygon');p.setAttribute('points',l.poly.map(function(q){return q.join(',')}).join(' '));p._l=l;svg.appendChild(p);polys.push(p)});
  var g=document.createElementNS(NS,'g');svg.appendChild(g);
  var btns=$('passbtns');
  PASSES.forEach(function(p,i){var b=document.createElement('button');b.type='button';b.className='btn seg'+(i===0?' on':'');b.textContent='Pass '+p.n;on(b,'click',function(){stopSim();select(i)});btns.appendChild(b)});
  function select(i){sel=i;cursor=null;[].forEach.call(btns.children,function(x,j){x.classList.toggle('on',j===i)});paint()}
  function gold(h,p){return 'hsl(40,62%,'+(82-52*(h-p.lo)/Math.max(1,p.hi-p.lo)).toFixed(1)+'%)'}
  function paint(){
    var p=PASSES[sel],inr=[];
    polys.forEach(function(q){var l=q._l,inP=l.h>=p.lo&&l.h<=p.hi;if(inP)inr.push(l);
      var shown=inP&&(cursor==null||l.h<=cursor);q.setAttribute('fill',shown?gold(l.h,p):css('--g3'));q.setAttribute('opacity',inP?(shown?'1':'.6'):'.45')});
    g.innerHTML='';
    if(inr.length&&cursor==null){var u=(bb[2]-bb[0])/150;
      [[inr[0],'first'],[inr[inr.length-1],'last']].forEach(function(e){var c=document.createElementNS(NS,'circle');c.setAttribute('cx',e[0].cx);c.setAttribute('cy',e[0].cy);c.setAttribute('r',u*2.6);c.setAttribute('fill','#c5a448');c.setAttribute('stroke','#0b0b0a');c.setAttribute('stroke-width',u*.7);g.appendChild(c);
        var tx=document.createElementNS(NS,'text');tx.setAttribute('x',e[0].cx+u*4);tx.setAttribute('y',e[0].cy+u*1.4);tx.setAttribute('style','font:700 '+u*4.4+'px var(--mono);fill:var(--fg);stroke:var(--bg);stroke-width:'+u*1.2+'px;paint-order:stroke');tx.textContent=e[1]+' '+pad(e[0].h);g.appendChild(tx)})}
    if(inr.length&&cursor!=null){var cur=inr.filter(function(l){return l.h<=cursor}).pop();if(cur){var u2=(bb[2]-bb[0])/150,c2=document.createElementNS(NS,'circle');c2.setAttribute('cx',cur.cx);c2.setAttribute('cy',cur.cy);c2.setAttribute('r',u2*3);c2.setAttribute('fill','#c5a448');c2.setAttribute('stroke','#0b0b0a');c2.setAttribute('stroke-width',u2*.8);g.appendChild(c2)}}
    $('passread').textContent=cursor==null?'':'Pass '+p.n+' · '+pad(Math.round(cursor))+' of '+pad(p.hi);
    $('passinfo').innerHTML='<h4 style="margin-top:0">Pass '+p.n+' · sections '+esc(p.secs)+'</h4><div class="out">'+pad(p.lo)+' to '+pad(p.hi)+'<br>'+fmt(p.hi-p.lo+1)+' positions<br>'+fmt(inr.length)+' have an outline on the map</div><p>'+esc(p.how)+'</p><p class="note"><span class="pgrad"></span>first lot to last lot. Lots outside the pass are gray.</p>';
  }
  function stopSim(){sim=0;if(raf)cancelAnimationFrame(raf);raf=0;cursor=null;var b=$('passplay');b.classList.remove('on');b.textContent='Simulate the six passes'}
  function runPass(i){sel=i;[].forEach.call(btns.children,function(x,j){x.classList.toggle('on',j===i)});var p=PASSES[i],t0=performance.now(),dur=Math.min(4200,1300+(p.hi-p.lo)*4);
    function step(t){if(!sim)return;var f=Math.min(1,(t-t0)/dur);cursor=p.lo+f*(p.hi-p.lo);paint();if(f<1){raf=requestAnimationFrame(step)}else{setTimeout(function(){if(!sim)return;if(i<PASSES.length-1)runPass(i+1);else{stopSim();select(0)}},700)}}
    raf=requestAnimationFrame(step)}
  on($('passplay'),'click',function(){if(sim){stopSim();select(sel);return}sim=1;var b=$('passplay');b.classList.add('on');b.textContent='Stop';runPass(0)});
  paint();redraws.push(paint);
  $('passes').innerHTML='<table class="t"><tr><th>Pass</th><th>Sections</th><th>H-numbers</th><th>Positions</th><th>Share of 3,185</th></tr>'+PASSES.map(function(p){var n=p.hi-p.lo+1;return '<tr><td><b>'+p.n+'</b></td><td>'+esc(p.secs)+'</td><td class="num">'+pad(p.lo)+' – '+pad(p.hi)+'</td><td class="num">'+fmt(n)+'</td><td><span style="display:block;height:10px;border-radius:999px;background:hsl(40,62%,52%);width:'+(n/3185*100)+'%;min-width:4px"></span></td></tr>'}).join('')+'</table><p class="note" style="margin-top:10px">Where two sections share a pass, their levels are woven: level 1 of the first section, level 1 of the second, then level 2 of each. That is why one section\'s H-numbers are not one block. Pass 4 holds three margin lists and the G/H rows; the margins are numbered before G and H.</p>';
})();

