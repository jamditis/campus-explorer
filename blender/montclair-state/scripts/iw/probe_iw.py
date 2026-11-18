# read-only: level structure of the crease faces touching aisle verts
import bpy, numpy as np
Z_STAGE=132.45; RISER=(141.3-132.45)/19
o=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=o.data
mats=[m.name for m in me.materials]; print('IWP mats',mats)
ai=[i for i,n in enumerate(mats) if 'aisle' in n]; si=mats.index('hn_amphi_seat_stone_blocks'); ri=mats.index('hn_amphi_riser_coursed_stone')
aisle_v=set()
for p in me.polygons:
    if p.material_index in ai: aisle_v.update(p.vertices)
V=me.vertices; cnt=0; ex=0; fr_a=[]; fr_r=[]
for p in me.polygons:
    if p.material_index not in (si,ri): continue
    t=np.degrees(np.arccos(min(1,max(-1,p.normal.z))))
    if 8<t<55 and any(v in aisle_v for v in p.vertices):
        cnt+=1
        for v in p.vertices:
            l=(V[v].co.z-Z_STAGE)/RISER
            (fr_a if v in aisle_v else fr_r).append(l-np.floor(l+1e-6))
        if ex<6: print('IWP face',p.index,mats[p.material_index],round(t,1),[(round(V[v].co.x,2),round(V[v].co.y,2),round((V[v].co.z-Z_STAGE)/RISER,3),v in aisle_v) for v in p.vertices]); ex+=1
print('IWP n',cnt)
print('IWP aisle-vert frac hist',np.histogram(fr_a,bins=10,range=(0,1))[0])
print('IWP row-vert frac hist',np.histogram(fr_r,bins=10,range=(0,1))[0])
# also check the aisle half-step levels distribution
fa=[(V[v].co.z-Z_STAGE)/RISER*2 for v in aisle_v]; fa=np.array(fa); print('IWP aisle half-level frac hist',np.histogram(fa-np.floor(fa+1e-6),bins=10,range=(0,1))[0])
print('IWP verts',len(V),'faces',len(me.polygons))
