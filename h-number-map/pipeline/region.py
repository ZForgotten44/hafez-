import numpy as np, fitz
from glyphs import get_dr
from scipy import ndimage as ndi
from PIL import Image, ImageDraw
MAROON=(0.5,0.14,0.28)
def region_mask(page,r=4,scale=1.0):
    W,H=int(page.rect.width*scale)+1,int(page.rect.height*scale)+1
    im=Image.new("L",(W,H),0); dr=ImageDraw.Draw(im)
    for x in get_dr(page):
        if x['type']=='f' and x['fill'] and all(abs(a-b)<0.02 for a,b in zip(x['fill'],MAROON)):
            R=x['rect']
            if max(R.width,R.height)>60: continue   # title bar / other maroon art
            pts=[]
            for it in x['items']:
                if it[0]=='l': pts+=[(it[1].x,it[1].y),(it[2].x,it[2].y)]
                elif it[0]=='c': pts+=[(it[1].x,it[1].y),(it[4].x,it[4].y)]
            if len(pts)>=3: dr.polygon([(px*scale,py*scale) for px,py in pts],fill=255)
            for p in pts: dr.ellipse([p[0]*scale-r*scale,p[1]*scale-r*scale,p[0]*scale+r*scale,p[1]*scale+r*scale],fill=255)
    for x in get_dr(page):
        if x['type']=='s' and x['color'] and all(abs(a-b)<0.02 for a,b in zip(x['color'],MAROON)) and (x['width'] or 0)>0.5:
            for it in x['items']:
                if it[0]=='l': dr.line([(it[1].x*scale,it[1].y*scale),(it[2].x*scale,it[2].y*scale)],fill=255,width=max(1,int(2*r*scale)))
    m=np.array(im)>0
    # close residual gaps then fill
    filled=ndi.binary_fill_holes(m)
    interior=filled & ~m
    lab,n=ndi.label(interior)
    return lab,n
