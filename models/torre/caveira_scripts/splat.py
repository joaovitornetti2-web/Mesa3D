import sys, numpy as np
from PIL import Image
d=np.load(sys.argv[1]); V,F,C=d['V'],d['F'],d['C']; out=sys.argv[2]
cmap=eval(sys.argv[3]) if len(sys.argv)>3 else {1:(40,40,44),2:(235,232,228),3:(200,30,40)}
T=V[F]; P=T.mean(1); n=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]); n/=np.linalg.norm(n,axis=1,keepdims=True)+1e-12
cols=np.array([cmap[c] for c in (1,2,3)],float)[C-1]
ims=[]; S=10; H=int((P[:,2].max()+2)*S)
for ang in (0,90,180,270):
    a=np.radians(ang); R=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]])
    Q=P@R.T; N=n@R.T; W=int((2*np.abs(P[:,:2]).max()+4)*S)
    x=(Q[:,0]*S+W/2).astype(int); y=(H-Q[:,2]*S).astype(int); dpt=Q[:,1]
    ok=(x>=0)&(x<W)&(y>=0)&(y<H); o=np.argsort(-dpt[ok]); idx=np.where(ok)[0][o]
    img=np.full((H,W,3),70.); 
    lum=np.clip(0.35+0.65*np.clip(-N[:,1]*0.7+N[:,2]*0.5,0,1),0,1)
    for dx in (0,1):
      for dy in (0,1):
        img[np.clip(y[idx]+dy,0,H-1),np.clip(x[idx]+dx,0,W-1)]=cols[idx]*lum[idx,None]
    ims.append(Image.fromarray(img.astype(np.uint8)))
Wd=Image.new('RGB',(sum(i.width for i in ims),H))
for k,im in enumerate(ims): Wd.paste(im,(k*im.width,0))
Wd.save(out)
