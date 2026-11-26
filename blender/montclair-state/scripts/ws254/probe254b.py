# ws254 read-only probe (library load): evaluated ground around Feliciano's E recess / flight A foot / walk N end; wall x; OSM walk faces north
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
W=['Terrain_LiDAR_DTM_1m','WS250_W63_lawn_LiDAR2023_ground_patch_1m','WS251_W63b_passage_LiDAR2023_ground_patch_1m','Feliciano School of Business walls','Footpaths_OSM','PI_Feliciano_east_base_course_UNVERIFIED','WS253_W63d_Feliciano_E_walk_slabs','WS253_W63d_Feliciano_E_walk_and_stairs_UNVERIFIED','WS253_W63d_Feliciano_E_recess_apron_raise_only_UNVERIFIED','WS253_W63d_Feliciano_E_stair_cheek_walls_UNVERIFIED','PO_Feliciano_gutters_downpipes_UNVERIFIED','PN_Feliciano_eaves_UNVERIFIED']
with bpy.data.libraries.load(F) as (a,b): b.objects=[n for n in W if n in a.objects]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; print(flush=True,*[],sep=' ',end='\n',file=__import__('sys').stdout) or print('P254 mods',[m.name for m in T.modifiers])
dg=bpy.context.evaluated_depsgraph_get(); em=T.evaluated_get(dg).to_mesh(); M=T.matrix_world
vs=[M@v.co for v in em.vertices]
ps=[p.vertices[:] for p in em.polygons if any(-215<vs[i].x<-170 and 150<vs[i].y<205 for i in p.vertices)]
bt=BVHTree.FromPolygons(vs,ps)
def g(x,y):
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return h[0].z if h[0] else float('nan')
xs=np.arange(-199.0,-185.9,0.5)
print(flush=True,*[],sep=' ',end='\n',file=__import__('sys').stdout) or print('P254 cols',' '.join('%6.1f'%x for x in xs))
for y in []:
    print(flush=True,*[],sep=' ',end='\n',file=__import__('sys').stdout) or print('P254 y%6.1f '%y+' '.join('%6.2f'%g(x,y) for x in xs),flush=True)
# base mesh (unevaluated) faces overlapping recess box
B=(-197.8,-195.0,163.8,172.0); bm=T.data; k=0
for p in bm.polygons:
    ws=[M@bm.vertices[i].co for i in p.vertices]
    if not (max(w.x for w in ws)<B[0] or min(w.x for w in ws)>B[1] or max(w.y for w in ws)<B[2] or min(w.y for w in ws)>B[3]):
        k+=1
        if k<8: print(flush=True,*[],sep=' ',end='\n',file=__import__('sys').stdout) or print('P254 baseface',p.index,len(ws),'x %.1f..%.1f y %.1f..%.1f z %.2f..%.2f'%(min(w.x for w in ws),max(w.x for w in ws),min(w.y for w in ws),max(w.y for w in ws),min(w.z for w in ws),max(w.z for w in ws)))
print(flush=True,*[],sep=' ',end='\n',file=__import__('sys').stdout) or print('P254 base faces overlapping recess',k)
# wall x by horizontal rays (west) at z 136
Wo=bpy.data.objects['Feliciano School of Business walls']; bw=BVHTree.FromObject(Wo,dg)
for y in np.arange(163.0,175.1,0.5):
    r=[]
    for z in (134.5,135.6,137.0):
        h=bw.ray_cast(Vector((-188,y,z)),Vector((-1,0,0)),40); r.append('%.2f'%h[0].x if h[0] else 'none')
    print(flush=True,*[],sep=' ',end='\n',file=__import__('sys').stdout) or print('P254 wall y %.1f'%y,r)
for n in ('PI_Feliciano_east_base_course_UNVERIFIED','PO_Feliciano_gutters_downpipes_UNVERIFIED','PN_Feliciano_eaves_UNVERIFIED'):
    o=bpy.data.objects.get(n); 
    if not o: continue
    me=o.data; Mo=o.matrix_world
    pts=[Mo@v.co for v in me.vertices if -199<(Mo@v.co).x<-193 and 160<(Mo@v.co).y<175]
    if pts: print(flush=True,*[],sep=' ',end='\n',file=__import__('sys').stdout) or print('P254',n,len(pts),'x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f'%(min(p.x for p in pts),max(p.x for p in pts),min(p.y for p in pts),max(p.y for p in pts),min(p.z for p in pts),max(p.z for p in pts)))
o=bpy.data.objects['Footpaths_OSM']; print(flush=True,*[],sep=' ',end='\n',file=__import__('sys').stdout) or print('P254 fp mods',[m.name for m in o.modifiers])
eo=o.evaluated_get(dg); me=eo.to_mesh(); Mo=o.matrix_world; k=0
for p in me.polygons:
    c=Mo@p.center
    if -200<c.x<-180 and 178<c.y<200:
        k+=1
        if k<=40: print(flush=True,*[],sep=' ',end='\n',file=__import__('sys').stdout) or print('P254 fp',p.index,'c %.1f %.1f %.2f a %.1f'%(c.x,c.y,c.z,p.area), ' '.join('(%.1f,%.1f)'%((Mo@me.vertices[i].co).x,(Mo@me.vertices[i].co).y) for i in p.vertices))
print(flush=True,*[],sep=' ',end='\n',file=__import__('sys').stdout) or print('P254 fp faces',k)
os._exit(0)
