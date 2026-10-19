/* ---------------- section 6: code workspace ---------------- */
(function(){
  var inDoc;
  function hlLine(l){var e=esc(l);if(inDoc){if(/"""/.test(l))inDoc=false;return '<span class="c">'+e+'</span>'}
    if((l.match(/"""/g)||[]).length===1){inDoc=true;return e.replace(/("""[\s\S]*)/,'<span class="c">$1</span>')}
    return e.replace(/(#.*$)|(&quot;[^&]*?&quot;|"[^"]*"|'[^']*')|\b(def|return|if|elif|else|for|in|not|and|or|is|None|True|False|import|from|lambda|while|raise|class|continue|break)\b|\b(\d+)\b/g,function(m,cm,st,kw,nu){return cm?'<span class="c">'+cm+'</span>':st?'<span class="s">'+st+'</span>':kw?'<span class="k">'+kw+'</span>':'<span class="n">'+nu+'</span>'})}
  var all=[],nav='',panes='';
  X.snips.forEach(function(g){nav+='<h6>'+esc(g.title)+'</h6>';
    g.items.forEach(function(s){var idx=all.push(s.src)-1;inDoc=false;var body=s.src.split('\n').map(function(l){return '<span class="ln">'+hlLine(l)+'</span>'}).join('');
      nav+='<button type="button" data-i="'+idx+'">'+esc(s.name)+'</button>';
      panes+='<div class="pane" data-i="'+idx+'"'+(idx?' hidden':'')+'><div class="ph"><div><b>'+esc(s.name)+'</b><span class="file">'+esc(s.file)+' · '+s.src.split('\n').length+' lines · '+esc(g.title.toLowerCase())+'</span><p>'+esc(s.desc||'')+'</p>'+(s.demo?'<p>Implements: <a href="'+esc(s.demo[1])+'">'+esc(s.demo[0])+'</a></p>':'')+'</div><button class="cpy" type="button" data-cp="'+idx+'">Copy</button></div><pre class="code">'+body+'</pre></div>'})});
  $('snips').innerHTML='<div class="cw"><div class="fl" role="tablist" aria-label="Functions">'+nav+'<p style="margin:14px;font:500 .7em var(--mono);color:#a8a69e">'+all.length+' functions</p></div><div class="panes" style="min-width:0">'+panes+'</div></div>';
  var btns=[].slice.call($('snips').querySelectorAll('.fl button')),ps=[].slice.call($('snips').querySelectorAll('.pane'));
  function show(i){btns.forEach(function(b){b.classList.toggle('on',+b.getAttribute('data-i')===i)});ps.forEach(function(p){p.hidden=+p.getAttribute('data-i')!==i})}
  btns.forEach(function(b){on(b,'click',function(){show(+b.getAttribute('data-i'))})});show(0);
  [].forEach.call($('snips').querySelectorAll('[data-cp]'),function(b){on(b,'click',function(){copyText(all[+b.getAttribute('data-cp')])})});
})();
function copyText(t){
  function fb(){var ta=document.createElement('textarea');ta.value=t;ta.style.cssText='position:fixed;left:-999px';document.body.appendChild(ta);ta.select();var ok=false;try{ok=document.execCommand('copy')}catch(e){}document.body.removeChild(ta);toast(ok?'Copied':'Select the text and copy')}
  try{if(navigator.clipboard){navigator.clipboard.writeText(t).then(function(){toast('Copied')},fb)}else fb()}catch(e){fb()}
}

