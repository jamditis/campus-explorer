# ws67b: the WS60 apron still sat 0.3-0.6 m ABOVE the north-file pavements and the ws67 gap strip at x -262..-247 (hid the strip,
# made a dark lip at x ~-250). Push apron verts below every paved surface there and flatten the x>-251 lip onto the DTM edge.
import bpy,bmesh,numpy as np,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']
if A.get('ws67b_done',0)!=1:
    PAVE=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('KY_','LF_','ey_','KX_','LH_college','WS67_CollegeAve_gap','WS27_CollegeAve_carriageway'))]
    dg=bpy.context.evaluated_depsgraph_get(); bvs=[]
    for o in PAVE:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if max(p.x for p in bb)<-268 or min(p.x for p in bb)>-238: continue
        bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bvs.append((o.name,BVHTree.FromBMesh(bm))); bm.free()
    print('B67b paved',[n[:20] for n,_ in bvs])
    def low(x,y):
        zs=[]
        for n,b in bvs:
            for oz in (170,):
                h=b.ray_cast(Vector((x,y,oz)),Vector((0,0,-1)),200)
                if h[0]: zs.append(h[0].z)
        return min(zs) if zs else None
    D=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy').astype(np.float64)
    def de(y): return float(D[int(round(y))+250,0])
    mw=A.matrix_world; mi=mw.inverted(); k=0; mx=0
    bm=bmesh.new(); bm.from_mesh(A.data)
    fs=[f for f in bm.faces if (lambda c:-266<c.x<-244 and -68<c.y<-44)(mw@f.calc_center_median())]
    es=list({e for f in fs for e in f.edges}); print('B67b faces',len(fs))
    if es: bmesh.ops.subdivide_edges(bm,edges=es,cuts=2,use_grid_fill=True)
    bm.to_mesh(A.data); bm.free()
    for v in A.data.vertices:
        p=mw@v.co
        if not (-266<p.x<-244 and -68<p.y<-44): continue
        t=p.z
        # sample a 1.2 m neighbourhood so edges of pavements are also cleared
        cand=[low(p.x+dx,p.y+dy) for dx in (-1.2,0,1.2) for dy in (-1.2,0,1.2)]
        cand=[c for c in cand if c is not None]
        if cand: t=min(t,min(cand)-0.10)
        if p.x>-251.5: t=min(t,de(p.y)-0.05)
        if t<p.z-0.002: v.co=mi@Vector((p.x,p.y,t)); k+=1; mx=min(mx,t-p.z)
    A.data.update(); A['ws67b_done']=1; print('B67b apron verts lowered',k,round(mx,2))
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for y in (-59,-56,-53):
    row=[]
    for x in range(-264,-244,2):
        r=sc.ray_cast(dg,Vector((x,y,170)),Vector((0,0,-1)))
        while r[0] and r[4].name.startswith('WS67_CollegeAve_W_DTM'): r=sc.ray_cast(dg,r[1]-Vector((0,0,0.01)),Vector((0,0,-1)))
        row.append('%d:%s@%.2f'%(x,r[4].name[:9],r[1].z) if r[0] else '%d:-'%x)
    print('V67b y',y,' '.join(row))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('B67b saved')
