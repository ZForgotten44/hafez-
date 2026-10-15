const fs=require('fs');const code=fs.readFileSync('giant_formula.js','utf8');
const H=eval('('+code.replace(/^H = /,'')+')');
const D=JSON.parse(fs.readFileSync('decoder_dump.json'));let ok=0,bad=[];
for(const [s,l,h] of D.fwd){ if(/dr$/.test(l)) continue; const v=H(s,l); if(v===h) ok++; else bad.push([s,l,h,v]); }
console.log('matched',ok,'of',D.fwd.filter(x=>!/dr$/.test(x[1])).length,'mismatches',bad.length,JSON.stringify(bad.slice(0,15)));
console.log('extras', H('D','293'), H('C','142H'), H('B','20H'), H('A','1'), H('C','417'), H('Z','1'));
