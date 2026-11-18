import numpy as np
P=np.load('scripts/ws132/las132.npy'); b=P[P[:,3]==6]; g=P[P[:,3]==2]
hi=b[b[:,2]>133]; lo=b[(b[:,2]>126)&(b[:,2]<=133)]
def runs(S,y,key):
    t=S[np.abs(S[:,1]-y)<0.5]
    if len(t)==0: return ''
    xs=np.sort(t[:,0]); out=[]; s=xs[0]; p=xs[0]
    for x in xs[1:]:
        if x-p>1.6: out.append((s,p)); s=x
        p=x
    out.append((s,p)); return ' '.join('%.1f..%.1f'%r for r in out if r[1]-r[0]>1)
for y in np.arange(-224,-264,-2.0):
    print('%5.0f HI %-40s LO %s'%(y,runs(hi,y,0),runs(lo,y,0)))
# ridge: max z per x column of hi
for x in range(-178,-122,4):
    t=hi[np.abs(hi[:,0]-x)<1]
    if len(t): i=np.argmax(t[:,2]); print('RIDGEx',x,'zmax %.1f at y %.1f'%(t[i,2],t[i,1]))
for y in range(-228,-262,-4):
    t=hi[np.abs(hi[:,1]-y)<1]
    if len(t): i=np.argmax(t[:,2]); print('RIDGEy',y,'zmax %.1f at x %.1f'%(t[i,2],t[i,0]))
print('LOz',np.percentile(lo[:,2],[10,50,90]))
for (x,y) in [(-183,-230),(-183,-250),(-170,-256),(-150,-256),(-135,-264),(-120,-250),(-120,-232),(-150,-222),(-170,-222)]:
    t=g[(np.abs(g[:,0]-x)<2)&(np.abs(g[:,1]-y)<2)]; print('G',x,y,'%.2f'%np.median(t[:,2]) if len(t) else '-')
