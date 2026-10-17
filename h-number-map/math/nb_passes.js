/* passes */
(function(){
  var bb=X.bbox,svg=$('passsvg'),mini=$('passmini'),NS='http://www.w3.org/2000/svg',polys=[],mpolys=[],sel=0;
  var asp=(bb[2]-bb[0]+12)/(bb[3]-bb[1]+12);
  mini.setAttribute('viewBox',(bb[0]-6)+' '+(bb[1]-6)+' '+(bb[2]-bb[0]+12)+' '+(bb[3]-bb[1]+12));
  var gMain=document.createElementNS(NS,'g'),gTrace=document.createElementNS(NS,'g'),gMiniBox=document.createElementNS(NS,'g');
  LOTS.forEach(function(l){var pts=l.poly.map(function(q){return q.join(',')}).join(' ');var p=document.createElementNS(NS,'polygon');p.setAttribute('points',pts);p._l=l;gMain.appendChild(p);polys.push(p);
    var m=document.createElementNS(NS,'polygon');m.setAttribute('points',pts);mini.appendChild(m);mpolys.push(m)});
  svg.appendChild(gMain);svg.appendChild(gTrace);mini.appendChild(gMiniBox);
  var btns=$('passbtns');
  PASSES.forEach(function(p,i){var b=document.createElement('button');b.type='button';b.className='btn seg'+(i===0?' on':'');b.textContent='Pass '+p.n;on(b,'click',function(){sel=i;[].forEach.call(btns.children,function(x,j){x.classList.toggle('on',j===i)});paint()});btns.appendChild(b)});
  function paint(){
    var p=PASSES[sel],inr=LOTS.filter(function(l){return l.h>=p.lo&&l.h<=p.hi});
    var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;inr.forEach(function(l){l.poly.forEach(function(q){if(q[0]<x0)x0=q[0];if(q[0]>x1)x1=q[0];if(q[1]<y0)y0=q[1];if(q[1]>y1)y1=q[1]})});
    if(!inr.length){x0=bb[0];x1=bb[2];y0=bb[1];y1=bb[3]}
    var w=x1-x0+30,h=y1-y0+30;if(w/h<asp)w=h*asp;else h=w/asp;var mx=(x0+x1)/2,my=(y0+y1)/2;
    svg.setAttribute('viewBox',(mx-w/2)+' '+(my-h/2)+' '+w+' '+h);
    polys.forEach(function(q){var l=q._l,on_=l.h>=p.lo&&l.h<=p.hi;q.setAttribute('fill',on_?ramp((l.h-p.lo)/Math.max(1,p.hi-p.lo)):css('--g3'));q.setAttribute('opacity',on_?'1':'.45')});
    mpolys.forEach(function(q,i){var l=LOTS[i],on_=l.h>=p.lo&&l.h<=p.hi;q.setAttribute('fill',on_?css('--fg'):css('--g3'))});
    gMiniBox.innerHTML='';var r=document.createElementNS(NS,'rect');r.setAttribute('x',mx-w/2);r.setAttribute('y',my-h/2);r.setAttribute('width',w);r.setAttribute('height',h);r.setAttribute('fill','none');r.setAttribute('stroke','#c5a448');r.setAttribute('stroke-width',(bb[2]-bb[0])/60);gMiniBox.appendChild(r);
    gTrace.innerHTML='';
    if(inr.length>1){
      var u=w/100,pts=inr.map(function(l){return l.cx+','+l.cy}).join(' ');
      var pl=document.createElementNS(NS,'polyline');pl.setAttribute('points',pts);pl.setAttribute('fill','none');pl.setAttribute('stroke',css('--fg'));pl.setAttribute('stroke-opacity','.55');pl.setAttribute('stroke-width',u*.22);pl.setAttribute('stroke-linejoin','round');gTrace.appendChild(pl);
      var k=Math.max(1,Math.floor(inr.length/16));
      for(var i=0;i+1<inr.length;i+=k){var a=inr[i],b=inr[i+1],dx=b.cx-a.cx,dy=b.cy-a.cy,L=Math.hypot(dx,dy);if(L<.5)continue;var ux=dx/L,uy=dy/L,mxp=(a.cx+b.cx)/2,myp=(a.cy+b.cy)/2,s=u*1.5;
        var t=document.createElementNS(NS,'polygon');t.setAttribute('points',[[mxp+ux*s,myp+uy*s],[mxp-ux*s*.7-uy*s*.8,myp-uy*s*.7+ux*s*.8],[mxp-ux*s*.7+uy*s*.8,myp-uy*s*.7-ux*s*.8]].map(function(q){return q.join(',')}).join(' '));t.setAttribute('fill',css('--fg'));t.setAttribute('stroke',css('--bg'));t.setAttribute('stroke-width',u*.12);gTrace.appendChild(t)}
      [[inr[0],'first'],[inr[inr.length-1],'last']].forEach(function(e){var c=document.createElementNS(NS,'circle');c.setAttribute('cx',e[0].cx);c.setAttribute('cy',e[0].cy);c.setAttribute('r',u*1.6);c.setAttribute('fill','#c5a448');c.setAttribute('stroke','#0b0b0a');c.setAttribute('stroke-width',u*.28);gTrace.appendChild(c);
        var tx=document.createElementNS(NS,'text');tx.setAttribute('x',e[0].cx+u*2.4);tx.setAttribute('y',e[0].cy-u*2);tx.setAttribute('style','font:700 '+u*2.6+'px var(--mono);fill:var(--fg);stroke:var(--bg);stroke-width:'+u*.7+'px;paint-order:stroke');tx.textContent=e[1]+' '+pad(e[0].h);gTrace.appendChild(tx)})}
    $('passinfo').innerHTML='<h4 style="margin-top:0">Pass '+p.n+' · sections '+esc(p.secs)+'</h4><div class="out">'+pad(p.lo)+' to '+pad(p.hi)+'<br>'+fmt(p.hi-p.lo+1)+' positions<br>'+fmt(inr.length)+' have an outline on the map</div><p>'+esc(p.how)+'</p><p class="note">The black line is the route in H order, and the arrowheads show which way it runs. Inside the pass the route goes level by level, so it sweeps across a section and steps over, rather than running down one line.</p>';
  }
  paint();redraws.push(paint);
  $('passes').innerHTML='<table class="t"><tr><th>Pass</th><th>Sections</th><th>H-numbers</th><th>Positions</th><th>Share of 3,185</th></tr>'+PASSES.map(function(p){var n=p.hi-p.lo+1;return '<tr><td><b>'+p.n+'</b></td><td>'+esc(p.secs)+'</td><td class="num">'+pad(p.lo)+' – '+pad(p.hi)+'</td><td class="num">'+fmt(n)+'</td><td><span style="display:block;height:10px;background:var(--fg);width:'+(n/3185*100)+'%;min-width:3px"></span></td></tr>'}).join('')+'</table><p class="note" style="margin-top:10px">Where two sections share a pass, their levels are woven: level 1 of the first section, level 1 of the second, then level 2 of each. That is why one section\'s H-numbers are not one block. Pass 4 holds three margin lists and the G/H rows; the margins are numbered before G and H.</p>';
})();

