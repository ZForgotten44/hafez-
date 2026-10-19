"""Compile the formula in hformula.py into ONE JavaScript expression  H(S, L)  (section letter S, legacy label L).
The constants (row widths, twins, blocks, lists) are written into the expression as literals, so it needs nothing else."""
import json, hformula as F
J = lambda x: json.dumps(x, separators=(',', ':'))
def prefix(w1, w2, n):  # lots swept before row r of a two-section pass
    return [sum((w1[j] if j < len(w1) else 0) + (w2[j] if j < len(w2) else 0) for j in range(r)) for r in range(n)]
P2 = prefix(F.WD, F.WC, 24); WD24 = F.WD + [0]
P3 = prefix(F.WF, F.WE, 12)
PG = prefix(F.WG, F.WH, 4)
TW = [[[t, 1 if fl == 'a' else 0] for (t, fl) in F.CTW[r]] for r in range(1, 25)]
TR = [1 if r in F.CTRIO else 0 for r in range(1, 25)]
DB = [list(b) for b in F.DBLOCK]; DH = [F.DHLOT[r] for r in range(16, 22)]
EB = [list(b) for b in F.EBLOCK]
EH = [[int(k[0].rstrip('H')) if k[0] != '199BH' else 0, k[1], v] for k, v in F.EHLOT.items() if k[0] != '199BH']

parts = {}
parts['A'] = "(r=Math.floor((n-1)/19)+1,q=n-19*(r-1),(p===''&&n>=1&&n<=361&&(f===''||(f==='H'&&(q===13||q===5||q===1))))?44*(r-1)+22+(20-q+(q<=13)+(q<=5)+(q<=1)-(f==='H')):NaN)"
parts['B'] = ("((i=BM.indexOf(L))>=0?2331+i+1:p!==''?NaN:f==='H'?((n%20===0&&n>=20&&n<=380)?44*(n/20-1)+1:NaN):L==='19A'?2:f!==''?NaN:"
              "((r=(n-12)/19+1,Number.isInteger(r)&&r>=1&&r<=19)?44*(r-1)+22:((n>=1&&n<=380&&n%20!==0)?44*Math.floor((n-1)/20)+22-(n-20*Math.floor((n-1)/20)):NaN)))")
parts['C'] = ("(L==='124H'&&(n=142),r=CT.findIndex(t=>n<=t)+1,(p===''&&r>0&&(r===1||n>CT[r-2]))?"
              "(b=TW[r-1].filter(w=>w[0]>n||(w[0]===n&&!w[1])).length,k=CT[r-1]-n+1+3*TR[r-1]+b,"
              "f===''?836+P2[r-1]+WD[r-1]+k:"
              "(f==='H'&&TW[r-1].some(w=>w[0]===n))?836+P2[r-1]+WD[r-1]+k+(TW[r-1].find(w=>w[0]===n)[1]?1:-1):"
              "(f.length===1&&'CBA'.indexOf(f)>=0&&TR[r-1]&&n===CT[r-1])?836+P2[r-1]+WD[r-1]+'CBA'.indexOf(f)+1:NaN):NaN)")
parts['D'] = ("((f==='A'||f==='B')&&n>=367&&n<=384&&(f=''),"
              "(p===''&&n>=542&&n<=563&&(f===''||(f==='H'&&DM.includes(n))))?2372+(n-541)+DM.filter(t=>t<n).length+(f==='H'?1:0):"
              "(/^1[H-U]$/.test(L))?836+1+(85-L.charCodeAt(1)):"
              "(p===''&&f===''&&n>=1&&n<=20)?836+15+(20-n):"
              "(L==='1A'||L==='1B'||L==='1C'||L==='1D'||L==='1E')?836+35+(L.charCodeAt(1)-65):"
              "L==='F1'?836+40:L==='1G'?836+41:L==='1H_2'?836+42:L==='1I_2'?836+43:"
              "(p===''&&f==='H')?((n%20===0&&n>=20&&n<=280)?836+P2[n/20]+1:(n%20===9&&n>=29&&n<=289)?836+P2[(n+11)/20-1]+13:DH.includes(n)?836+P2[DH.indexOf(n)+15]+1:NaN):"
              "(p===''&&f===''&&n>=21&&n<=300)?(r=Math.floor((n-1)/20)+1,j=20*r-n,836+P2[r-1]+(j<=10?j+2:j+3)):"
              "(p===''&&f===''&&(g=DB.find(x=>x[3]<=n&&n<=x[2])))?836+P2[g[0]-1]+g[1]+g[2]-n:NaN)")
parts['E'] = ("(/^(152|169|19[0-9])[AB]$/.test(L)&&(n===152||n===169||(n>=190&&n<=199))?(r=n===152?9:10,k=n===152?21:n===169?10:12+(199-n),1871+P3[r-1]+WF[r-1]+k):"
              "L==='199BH'?1871+P3[9]+WF[9]+11:p!==''?NaN:"
              "(f===''&&n>=1&&n<=152)?(r=Math.floor((n-1)/19)+1,q=n-19*(r-1),1871+P3[r-1]+WF[r-1]+(19-q+1)+(q<=13)+(q<=9)+(q<=5)):"
              "(f==='H'&&n<=152&&((q=n-19*Math.floor((n-1)/19))===13||q===9||q===5))?(r=Math.floor((n-1)/19)+1,1871+P3[r-1]+WF[r-1]+(19-q+1)+(q<=13)+(q<=9)+(q<=5)-1):"
              "f==='H'?((g=EH.find(x=>x[0]===n))?1871+P3[g[1]-1]+WF[g[1]-1]+g[2]:NaN):"
              "(f===''&&(g=EB.find(x=>x[3]<=n&&n<=x[2])))?1871+P3[g[0]-1]+WF[g[0]-1]+g[1]+g[2]-n:NaN)")
parts['F'] = "((p===''&&f===''&&n>=1&&n<=198)?(r=Math.floor((n-1)/18)+1,1871+P3[r-1]+19-(n-18*(r-1))):(p===''&&f===''&&n>=199&&n<=210)?2401+(n-198):NaN)"
parts['G'] = ("(L==='19'?2415:p!==''?NaN:(f===''&&(n===58||n===59||n===60))?2413+PG[n-58]+1:"
              "((f===''||f==='H')&&n>=1&&n<=57)?(r=Math.floor((n-1)/19)+1,j=19*r-n,f==='H'?(n===19*r?2413+PG[r-1]+2:n===19*r-11?2413+PG[r-1]+14:NaN):2413+PG[r-1]+(j<=10?j+3:j+4)):"
              "(f===''&&n>=61&&n<=75)?2413+PG[3]+(n-60):NaN)")
parts['H'] = "((p===''&&f===''&&n>=1&&n<=92)?(r=Math.floor((n-1)/23)+1,2413+PG[r-1]+22*0+WG[r-1]+23*r+1-n):NaN)"
parts['M'] = "((p===''&&f==='')?((n>=82&&n<=279)?n+2556:(i=MF.indexOf(String(n)))>=0?2586+i+1:NaN):NaN)"
parts['K'] = "((p===''&&f===''&&(i=KO.indexOf(String(n)))>=0)?2835+i+1:NaN)"
parts['J'] = "((p===''&&f===''&&n>=1&&n<=132)?2950+n:NaN)"
parts['I'] = "((p===''&&f===''&&n>=1&&n<=64)?3082+n:NaN)"
parts['L'] = "((p===''&&f===''&&n>=69&&n<=107)?3146+n-68:NaN)"
consts = dict(BM=F.BMARGIN, CT=F.CT, TW=TW, TR=TR, P2=P2, WD=WD24, P3=P3, WF=F.WF, PG=PG, WG=F.WG, DM=list(F.DM_TW), DH=DH, DB=DB, EB=EB, EH=EH, MF=F.MFIRST, KO=F.KORDER)
pre = ("(m=/^([A-Z]?)([0-9]+)(.*)$/.exec(L),p=m?m[1]:'',n=m?+m[2]:NaN,f=m?m[3]:'',"
       "S==='A'?" + parts['A'] + ":S==='B'?" + parts['B'] + ":S==='C'?" + parts['C'] + ":S==='D'?" + parts['D'] + ":S==='E'?" + parts['E'] + ":S==='F'?" + parts['F'] + ":S==='G'?" + parts['G'] +
       ":S==='H'?" + parts['H'] + ":S==='M'?" + parts['M'] + ":S==='K'?" + parts['K'] + ":S==='J'?" + parts['J'] + ":S==='I'?" + parts['I'] + ":S==='L'?" + parts['L'] + ":NaN)")
decl = ';'.join('%s=%s' % (k, J(v)) for k, v in consts.items())
full = "H = (S, L) => { var m,p,n,f,r,q,c,k,i,j,g,b," + decl.replace(';', ',') + "; return " + pre + "; }"
open('giant_formula.js', 'w').write(full)
json.dump(dict(parts=parts, consts=consts, expr=pre, decl=decl), open('giant_parts.json', 'w'))
print('giant expression length', len(pre), 'chars; with constants', len(full))
