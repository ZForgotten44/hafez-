/* P1 */
(function(){
  var ord='blocks',d;
  function Hf(sec,r,c,N){var SW=2*N;return ord==='blocks'?SW*(r-1)+(sec==='B'?0:N)+c:SW*(r-1)+2*c-(sec==='B'?1:0)}
  function run(){
    var N=+$('p1n').value,R=+$('p1r').value;$('p1nv').textContent=N;$('p1rv').textContent=R;
    var sec=$('p1sec').value,r0=+$('p1lv').value||1,c0=+$('p1c').value||1,r=Math.min(Math.max(1,r0),R),c=Math.min(Math.max(1,c0),N),clamp=(r!==r0||c!==c0);
    $('p1lv').max=R;$('p1c').max=N;
    var SW=2*N,Hs=Hf(sec,r,c,N);
    $('p1eqn').innerHTML=ord==='blocks'?'<span class="lbl">SWEEP  = </span>N<sub>B</sub> + N<sub>A</sub> = '+SW+'<br><span class="lbl">OFFSET = </span>SWEEP × R = '+SW*R+'<br><span class="lbl">H(B, r, c) = </span>SWEEP × (r − 1) + c<br><span class="lbl">H(A, r, c) = </span>SWEEP × (r − 1) + N<sub>B</sub> + c'
      :'<span class="lbl">SWEEP  = </span>N<sub>B</sub> + N<sub>A</sub> = '+SW+'<br><span class="lbl">OFFSET = </span>SWEEP × R = '+SW*R+'<br><span class="lbl">H(B, r, c) = </span>SWEEP × (r − 1) + 2c − 1<br><span class="lbl">H(A, r, c) = </span>SWEEP × (r − 1) + 2c';
    $('p1out').innerHTML='H('+sec+', level '+r+', column '+c+') = '+SW+' × '+(r-1)+(ord==='blocks'?(sec==='A'?' + '+N:''):'')+' + '+(ord==='blocks'?c:(sec==='B'?'2×'+c+'−1':'2×'+c))+' = <span class="hv">'+Hs+'</span> → '+pad(Hs)+'<br>Visited as lot '+Hs+' of '+SW*R+' in this pass. On level '+r+' the sweep visits '+(ord==='blocks'?'B columns 1 to '+N+' (H '+Hf('B',r,1,N)+' to '+Hf('B',r,N,N)+'), then A columns 1 to '+N+' (H '+Hf('A',r,1,N)+' to '+Hf('A',r,N,N)+').':'B and A columns in turn: B1, A1, B2, A2 …')+(clamp?'<br>Level and column were limited to 1–'+R+' and 1–'+N+'.':'');
    var cv=$('p1cv'),cx=cv.getContext('2d');cx.clearRect(0,0,cv.width,cv.height);
    var cw=(cv.width-60)/N,ch=Math.min(18,(cv.height-30)/(2*R+1)),tot=2*N*R,dk=isDark();cv._g={cw:cw,ch:ch,N:N,R:R};
    ['B','A'].forEach(function(s,si){for(var rr=1;rr<=R;rr++)for(var cc=1;cc<=N;cc++){var h=Hf(s,rr,cc,N),t=(h-1)/Math.max(1,tot-1);cx.fillStyle=ramp(t);cx.fillRect(40+(cc-1)*cw,10+(si*(R+1)+rr-1)*ch,cw-1.5,ch-1.5);
      if(rr===r&&cw>=24){cx.fillStyle=dk?(t<.45?'#f4f2ec':'#0b0b0a'):(t<.55?'#0b0b0a':'#f4f2ec');cx.font='500 '+Math.min(12,cw*.42)+'px "IBM Plex Mono",monospace';cx.textAlign='center';cx.fillText(h,40+(cc-1)*cw+cw/2,10+(si*(R+1)+rr-1)*ch+ch*.72)}}});
    cx.setLineDash([5,4]);cx.lineWidth=1.6;cx.strokeStyle=css('--fg');[0,1].forEach(function(si){cx.strokeRect(38,10+(si*(R+1)+r-1)*ch-2,N*cw+3,ch+2)});cx.setLineDash([]);
    cx.fillStyle=css('--fg');cx.font='600 11px "IBM Plex Mono",monospace';cx.textAlign='left';cx.fillText('visit ▶',40,10+(2*R+1)*ch+16);
    var si=sec==='B'?0:1,sx=40+(c-1)*cw-1,sy=10+(si*(R+1)+r-1)*ch-1;cx.fillStyle='#c5a448';cx.fillRect(sx,sy,cw,ch);cx.lineWidth=2.5;cx.strokeStyle='#0b0b0a';cx.strokeRect(sx,sy,cw,ch);
    cx.fillStyle='#0b0b0a';cx.font='700 '+Math.min(12,Math.max(8,cw*.42))+'px "IBM Plex Mono",monospace';cx.textAlign='center';if(cw>=20)cx.fillText(Hs,sx+cw/2,sy+ch*.72);
    cx.fillStyle=css('--g5');cx.font='600 12px "IBM Plex Mono",monospace';cx.textAlign='left';cx.fillText('B',14,10+ch);cx.fillText('A',14,10+(R+1)*ch+ch);
    d.upd();
  }
  d=demo('p1',['p1n','p1r','p1sec','p1lv','p1c'],function(){return ord!=='blocks'},function(){ord='blocks';[].forEach.call(document.querySelectorAll('button[data-ord]'),function(x){x.classList.toggle('on',x.getAttribute('data-ord')==='blocks')})},run);
  ['p1n','p1r','p1sec','p1lv','p1c'].forEach(function(i){on($(i),'input',run)});
  [].forEach.call(document.querySelectorAll('button[data-ord]'),function(b){on(b,'click',function(){ord=b.getAttribute('data-ord');[].forEach.call(document.querySelectorAll('button[data-ord]'),function(x){x.classList.toggle('on',x===b)});run()})});
  function cell(e){var cv=$('p1cv'),g=cv._g;if(!g)return null;var r=cv.getBoundingClientRect(),x=(e.clientX-r.left)*cv.width/r.width-40,y=(e.clientY-r.top)*cv.height/r.height-10;var cc=Math.floor(x/g.cw)+1,row=Math.floor(y/g.ch),si=row>=g.R+1?1:0,rr=row-si*(g.R+1)+1;if(cc<1||cc>g.N||rr<1||rr>g.R)return null;return {si:si,rr:rr,cc:cc,N:g.N}}
  on($('p1cv'),'mousemove',function(e){var q=cell(e);this.title=q?(q.si?'A':'B')+' level '+q.rr+', column '+q.cc+' = '+Hf(q.si?'A':'B',q.rr,q.cc,q.N):''});
  on($('p1cv'),'click',function(e){var q=cell(e);if(!q)return;$('p1sec').value=q.si?'A':'B';$('p1lv').value=q.rr;$('p1c').value=q.cc;run()});
  run();redraws.push(run);
})();

