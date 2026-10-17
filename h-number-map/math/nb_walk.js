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
  function rebuild(){
    var st=+$('sawstart').value,wd=+$('sawwidth').value;$('sawstartv').textContent=st;$('sawwidthv').textContent=wd;
    seq=LOTS.filter(function(l){return l.h>=st&&l.h<st+wd});var mp=Math.max(0,seq.length-1);$('walkpos').max=mp;if(posF>mp)posF=mp;$('walkpos').value=Math.round(posF);
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
    if(cp){var vb=svg.getAttribute('viewBox').split(' '),u=+vb[2]/160,pts=[];for(var k=0;k<=i;k++)pts.push(seq[k].cx+','+seq[k].cy);pts.push(cp.x+','+cp.y);var pl=document.createElementNS(NS,'polyline');pl.setAttribute('points',pts.join(' '));pl.setAttribute('fill','none');pl.setAttribute('stroke','#0b0b0a');pl.setAttribute('stroke-width',u*.9);pl.setAttribute('stroke-opacity','.75');pl.setAttribute('stroke-linejoin','round');pl.setAttribute('stroke-linecap','round');gT.appendChild(pl);
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
  var host=$('heroart');if(!host)return;var NS='http://www.w3.org/2000/svg',Wd=1000,Hh=300;
  var st=[],N=3,R=2,cw=84,ch=88;
  for(var r=0;r<R;r++)['B','A'].forEach(function(s){for(var c=0;c<N;c++){var x0=s==='B'?130:560;st.push({x:x0+c*cw,y:112+r*(ch+30)})}});
  var pts=st.map(function(p){return [p.x+27,p.y+44]});
  function smooth(p){var d='M'+p[0][0]+' '+p[0][1];for(var i=0;i<p.length-1;i++){var a=p[i-1]||p[i],b=p[i],c=p[i+1],e=p[i+2]||c;d+=' C'+(b[0]+(c[0]-a[0])/6)+' '+(b[1]+(c[1]-a[1])/6)+' '+(c[0]-(e[0]-b[0])/6)+' '+(c[1]-(e[1]-b[1])/6)+' '+c[0]+' '+c[1]}return d}
  var h='<svg viewBox="0 0 '+Wd+' '+Hh+'" xmlns="http://www.w3.org/2000/svg">'
   +'<circle class="hart-sun" cx="880" cy="70" r="38"/>'
   +'<path class="hart-hill2" d="M0 230 C150 170 300 200 460 215 S780 180 1000 205 V300 H0Z"/>'
   +'<path class="hart-hill1" d="M0 262 C170 214 330 258 520 246 S850 222 1000 250 V300 H0Z"/>';
  [[70,206,30,64],[960,198,26,58],[470,214,22,48]].forEach(function(t){h+='<ellipse class="hart-tree" cx="'+t[0]+'" cy="'+t[1]+'" rx="'+t[2]+'" ry="'+t[3]+'"/>'});
  h+='<text class="hart-label" x="'+(130+cw)+'" y="92">Section B</text><text class="hart-label" x="'+(560+cw)+'" y="92">Section A</text>';
  st.forEach(function(p){h+='<path class="hart-stone" d="M'+p.x+' '+(p.y+62)+' V'+(p.y+24)+' a27 24 0 0 1 54 0 V'+(p.y+62)+' Z"/>'});
  h+='<path class="hart-path" id="hartpath" d="'+smooth(pts)+'"/>';
  st.forEach(function(p,i){h+='<text class="hart-num" x="'+(p.x+27)+'" y="'+(p.y+52)+'" style="animation-delay:'+(0.25+i*0.42).toFixed(2)+'s">'+(i+1)+'</text>'});
  h+='</svg><button class="btn sm replay" type="button" id="hartreplay">Replay</button>';
  host.innerHTML=h;
  var path=$('hartpath');try{var L=path.getTotalLength();host.style.setProperty('--len',Math.ceil(L)+2);path.style.strokeDasharray=Math.ceil(L)+2;path.style.strokeDashoffset=Math.ceil(L)+2}catch(e){}
  function go(){host.classList.remove('go','static');void host.offsetWidth;host.classList.add('go')}
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduce)host.classList.add('static');else go();
  on($('hartreplay'),'click',function(){host.classList.remove('static');go()});
})();

