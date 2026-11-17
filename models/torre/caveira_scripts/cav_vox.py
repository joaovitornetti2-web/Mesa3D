import numpy as np, trimesh, time
from scipy import ndimage
ESC=2.1; P=0.4
d=np.load('caveira.npz'); V=d['V']*ESC; F=d['F']
m=trimesh.Trimesh(V,F,process=False)
pts,_=trimesh.sample.sample_surface(m, 25000000)
o=V.min(0)-2*P; idx=np.floor((pts-o)/P).astype(int); sh=idx.max(0)+3
G=np.zeros(sh,bool); G[idx[:,0],idx[:,1],idx[:,2]]=True
G=ndimage.binary_closing(G,iterations=1)
# fecha o fundo (base plana) para o fill funcionar
G[:,:,0]|=ndimage.binary_fill_holes(G[:,:,:4].any(2))
S=ndimage.binary_fill_holes(G)
print('shape',S.shape,'solid frac',S.sum()/S.size,'o',o)
np.savez_compressed('cav_solid.npz',S=S,o=o,P=P)
