import pickle, fitz, math, csv, collections, importlib.util, os, sys
import render
OUT="/Users/mansyhafez/Desktop/hafez#/h-number-map"
os.makedirs(OUT,exist_ok=True)
spec=importlib.util.spec_from_file_location("dec","/Users/mansyhafez/Desktop/hafez#/s4/s4decoder1.py"); dec=importlib.util.module_from_spec(spec); spec.loader.exec_module(dec)
recs,bad=pickle.load(open('final.pkl','rb'))
k=4.0
def extra(pg,put,k):
    # retitle: OVERALL MAP -> H-NUMBER MAP
    pg.draw_rect(fitz.Rect(257*k,532*k,394*k,553*k),color=None,fill=(1,1,1))
    txt="H-NUMBER MAP"; fs=1.0
    L=fitz.get_text_length(txt,fontname="tibo",fontsize=fs); fs=128*k/L
    pg.insert_text(fitz.Point(260*k,548*k),txt,fontsize=fs,fontname="tibo",color=(0,0,0))
    note=["Each lot shows its H-number, written without the leading \"H\" and zeros",
          "(e.g. 1871 = H001871).  A / B after a number marks the two rows of a double-row lot.",
          "Lots that still show a small original label have not been assigned a new number on this map."]
    for i,l in enumerate(note):
        pg.insert_text(fitz.Point(432*k,(519+i*8.5)*k),l,fontsize=5.6*k,fontname="tiro",color=(0.1,0.1,0.1))
big=os.path.join(OUT,"Cedar_Grove_H-Number_Map_44x34in.pdf")
render.build(big,recs,k=k,extra=extra)
# ---- tiled letter-size version (landscape, 0.5in margins, 5 x 5 tiles at 100% of the big sheet)
src=fitz.open(big); W,H=src[0].rect.width,src[0].rect.height
tw,th=720,540; cols=math.ceil(W/tw); rows=math.ceil(H/th)
t=fitz.open()
for r in range(rows):
    for c in range(cols):
        pg=t.new_page(width=792,height=612)
        clip=fitz.Rect(c*tw,r*th,min((c+1)*tw,W),min((r+1)*th,H))
        dst=fitz.Rect(36,36,36+clip.width,36+clip.height)
        pg.show_pdf_page(dst,src,0,clip=clip)
        pg.draw_rect(dst,color=(0.6,0.6,0.6),width=0.4)
        pg.insert_text(fitz.Point(36,26),f"Cedar Grove Cemetery - H-Number Map   |   tile row {r+1}/{rows}, column {c+1}/{cols}   |   print at 100% (actual size)",fontsize=8,fontname="helv",color=(0.3,0.3,0.3))
        pg.insert_text(fitz.Point(36,600),"Tiles do not overlap: butt the printed edges together (left to right, top to bottom) to rebuild the 44 x 34 in map.",fontsize=7,fontname="helv",color=(0.4,0.4,0.4))
t.save(os.path.join(OUT,"Cedar_Grove_H-Number_Map_letter_tiles.pdf"),deflate=True)
# ---- CSVs
placed={(r['sec'],r['txt']) for r in recs}
with open(os.path.join(OUT,"placed_lots.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["section","old_lot_label","h_number","map_x","map_y"])
    for r in sorted(recs,key=lambda r:(r['sec'],r['h'])): w.writerow([r['sec'],r['txt'],r['f'],round(r['ocen'][0],2),round(r['ocen'][1],2)])
miss=[]
for s in 'ABCDEFGHIJKLM':
    for row in dec.full_table(s):
        lab=row['lot_label']
        if (s,lab) in placed: continue
        note=""
        if lab.endswith('dr'): note="internal double-row key (labelled as A/B on the map)"
        elif s=='D' and lab.isdigit() and 367<=int(lab)<=384: note="shared base of a double-row lot (map shows 'A'/'B' rows)"
        elif s=='E' and lab.isdigit() and 190<=int(lab)<=199: note="shared base of a double-row lot (map shows 'A'/'B' rows)"
        miss.append((s,lab,row['h_lot'],note))
with open(os.path.join(OUT,"lots_not_placed_on_map.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["section","lot_label_in_decoder","h_number","note"]); w.writerows(miss)
unk=[]
for (pi,sec),ls in bad.items():
    for l in ls:
        if len(l['txt'])>=2 and len(l['txt'])<=6 and any(ch.isdigit() for ch in l['txt']):
            unk.append((sec,l['txt'],round(l['cen'][0],1),round(l['cen'][1],1),pi))
with open(os.path.join(OUT,"map_labels_not_in_decoder.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["section_region","label_read_from_map","page_x","page_y","source_page_index"]); w.writerows(unk)
print("placed",len(recs),"not placed",len(miss),"unknown labels",len(unk))
