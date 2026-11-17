import numpy as np, trimesh
from scipy import ndimage
from skimage import measure
d=np.load('cav_solid.npz'); S=d['S']; o=d['o']; P=float(d['P'])
nx,ny,nz=S.shape
X=np.arange(nx)*P+o[0]; Y=np.arange(ny)*P+o[1]; Z=np.arange(nz)*P+o[2]
cav=np.zeros_like(S)
for k in range(nz):
    if 47<=Z[k]<=126:
        sl=S[:,:,k]; cav[:,:,k]=ndimage.binary_fill_holes(sl)&~sl
# máscara 2D da cavidade em z=50 para descer até a base, mais o corredor da boca
m50=cav[:,:,int((50-o[2])/P)].copy()
yy,xx=np.meshgrid(Y,X)
corredor=(np.abs(xx)<22)&(yy<0)&(yy>-54)
base2d=ndimage.binary_erosion(m50,iterations=1)|(corredor&ndimage.binary_dilation(m50,iterations=60)&~S[:,:,int(20/P)])
T=np.tan(np.radians(50)); E=3.6/np.cos(np.radians(50))
ZZ=Z[None,None,:]; YY=yy[:,:,None]
# rampa A: sai da parede de trás, desce para a frente (ponta em y=+8, z=89)
zA=89+(YY-8)*T
rA=(YY>=8)&(ZZ<=zA)&(ZZ>=zA-E)
# rampa B: sai da parede da frente (acima da boca), desce para trás (ponta em y=-2, z=46)
zB=46+(-2-YY)*T
rB=(YY<=-2)&(ZZ<=zB)&(ZZ>=zB-E)
dentro=cav.copy(); dentro[:,:,Z<47]|=base2d[:,:,None]
# rampas engrossadas 1,2 mm para dentro das paredes (garante união com a casca)
paredes=ndimage.binary_dilation(dentro,iterations=3)&S
R=(rA|rB)&(dentro|paredes)
# piso: cunha maciça da parede de trás (z=24) até a boca (z=5), dentro da máscara base
zP=5+(YY+40)*(19/80.)
piso=base2d[:,:,None]&(ZZ<=np.clip(zP,5,24))
piso|=ndimage.binary_dilation(base2d,iterations=3)[:,:,None]&S&(ZZ<=np.clip(zP,5,24))
A=(R|piso)
A=ndimage.binary_opening(A,iterations=1)
A[:,:,Z<0]=False
lab,n=ndimage.label(A); sz=ndimage.sum(A,lab,range(1,n+1)); A=np.isin(lab,1+np.where(sz>5000)[0])
print('voxels add',A.sum(),n)
v,f,_,_=measure.marching_cubes(np.pad(A,1).astype(np.float32),0.5); v=(v-1)*P+o; v[v[:,2]<0.3,2]=0
m=trimesh.Trimesh(v,f); m.fix_normals(); print('wt',m.is_watertight,'vol',m.volume/1000,'bodies',m.body_count)
m.export('cav_rampas.stl')
np.savez_compressed('cav_add.npz',A=A)
# checagem: a soma tem caminho?
tot=S|A
np.savez_compressed('cav_total.npz',S=tot,o=o,P=P)
