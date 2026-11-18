# ws172b: yard-tree variety (ws171 self-review item 3: all 8 WS171 yard trees were one red-maple mesh). Residential yards S of Normal Ave W in
# Montclair are a mixed oak/maple canopy (species UNVERIFIED: LiDAR gives height/crown only). Swap tallest broad crowns to pin oak / sugar maple
# from the asset library (same mesh already in main if present, else appended once from assets/campus_trees_v2.blend), rescale each to its LiDAR
# height about the trunk base, vary 'autumn' per instance and crown aspect +-8%. Positions/heights unchanged (LiDAR).
import bpy, math
from mathutils import Matrix, Vector
OB=bpy.data.objects
def find(sp):
    c=[o for o in OB if o.type=='MESH' and o.name.startswith('Tree_'+sp) and 'LOD1' in o.name]
    if not c: c=[o for o in OB if o.type=='MESH' and o.name.startswith('Tree_'+sp)]
    if c: return c[0]
    lib='/workspace/nj-scenes/assets/campus_trees_v2.blend'
    with bpy.data.libraries.load(lib) as (a,b):
        nm=[n for n in a.objects if n.startswith('Tree_'+sp) and 'LOD1' in n] or [n for n in a.objects if n.startswith('Tree_'+sp)]
        print('FIX172b lib objects for',sp,nm[:4],flush=True); b.objects=nm[:1]
    o=b.objects[0] if b.objects else None
    return o
src={'PinOak':find('PinOak'),'SugarMaple':find('SugarMaple')}
print('FIX172b sources',{k:(v.name if v else None) for k,v in src.items()},flush=True)
def base(o):
    mw=o.matrix_world; W=[mw@v.co for v in o.data.vertices]; zm=min(w.z for w in W); zM=max(w.z for w in W); L=[w for w in W if w.z<zm+0.3]
    return Vector((sum(w.x for w in L)/len(L),sum(w.y for w in L)/len(L),zm)), zM-zm
PLAN={'S_yard_D':('PinOak',0.30),'S_yard_I':('PinOak',0.45),'S_yard_C':('SugarMaple',0.55),'S_yard_A':('SugarMaple',0.35),'S_yard_H':('SugarMaple',0.70),
      'S_yard_E':(None,0.25),'S_yard_K':(None,0.60),'S_yard_B':(None,0.45)}
BI={}
for k,(lab,(sp,au)) in enumerate(sorted(PLAN.items())):
    t=[o for o in OB if o.name.startswith('WS171_tree_'+lab+'_')]
    if not t: continue
    t=t[0]; b0,h0=base(t)
    s=src.get(sp) if sp else None
    if s is not None:
        if s.name not in BI: BI[s.name]=base(s)
        sb,sh=BI[s.name]; sc=h0/sh; asp=1.0+0.08*math.sin(2.1*k+0.4)
        t.data=s.data
        t.matrix_world=Matrix.Translation(b0)@Matrix.Rotation(1.7*k+0.3,4,'Z')@Matrix.Diagonal((sc*asp,sc/asp,sc,1))@Matrix.Translation(-sb)@s.matrix_world
        for i,sl in enumerate(s.material_slots):
            if i<len(t.material_slots): t.material_slots[i].link='DATA'
        t.name='WS171_tree_%s_LiDAR2023_h%dm_%s_UNVERIFIEDspecies'%(lab,round(h0),sp)
    t['autumn']=au
    nb,nh=base(t); print('FIX172b',t.name,'h',round(h0,1),'->',round(nh,1),'base shift',round((nb-b0).length,2),flush=True)
for o in [o for o in OB if o.name.startswith('Tree_') and o.users_collection==() ]: pass
