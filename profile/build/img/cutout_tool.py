import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
U='/mnt/user-data/uploads/Gemini_Generated_Image_'
def cutout(path,out,thresh_white,drop_die_line,keep_largest,seal=2,erode=1):
    im=Image.open(path).convert('RGB'); a=np.array(im).astype(np.int16)
    h,w,_=a.shape
    light=(a.min(axis=2)>=thresh_white)
    # outer background (pure white, connected to corners)
    pw=(a.min(axis=2)>=250); lab,_=ndi.label(pw)
    seeds=[lab[0,0],lab[0,w-1],lab[h-1,0],lab[h-1,w-1]]
    outer=np.isin(lab,[s for s in seeds if s])
    barrier=~light
    if drop_die_line:
        # remove the sticker's thin die-cut outline so the white margin connects to the outside
        d=ndi.distance_transform_edt(~outer)
        barrier&=~(d<=7)
    barrier=ndi.binary_closing(barrier,structure=np.ones((3,3)),iterations=seal)
    passable=~barrier|outer
    lab2,_=ndi.label(passable)
    s2=[lab2[0,0],lab2[0,w-1],lab2[h-1,0],lab2[h-1,w-1]]
    bg=np.isin(lab2,[s for s in s2 if s])
    fg=~bg
    if keep_largest:
        l3,n3=ndi.label(fg); sizes=ndi.sum(fg,l3,range(1,n3+1)); fg=(l3==(np.argmax(sizes)+1))
    fg=ndi.binary_fill_holes(fg)
    if erode: fg=ndi.binary_erosion(fg,iterations=erode)
    al=Image.fromarray((fg*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1))
    rgba=im.convert('RGBA'); rgba.putalpha(al)
    bb=al.point(lambda v:255 if v>20 else 0).getbbox(); rgba=rgba.crop(bb); rgba.save(out); print(out,rgba.size)
    prev=Image.new('RGBA',rgba.size,(13,14,22,255)); prev.alpha_composite(rgba)
    prev.convert('RGB').resize((rgba.width//3,rgba.height//3)).save(out.replace('.png','_prev.png'))
cutout(U+'jxcvx7jxcvx7jxcv.png','work/img/pointing.png',215,True,True)
cutout(U+'lfdknylfdknylfdk.png','work/img/laptop.png',250,False,False,seal=1,erode=2)
