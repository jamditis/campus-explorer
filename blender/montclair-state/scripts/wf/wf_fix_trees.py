import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
os_chdir=True
import os; os.chdir('/workspace/nj-scenes/montclair-state')
X0,X1,Y0,Y1=50.,300.,320.,520.
SINK=-0.25
dg=bpy.context.evaluated_depsgraph_get()
P=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
Pe=P.evaluated_get(dg); pme=Pe.to_mesh()
bp=BVHTree.FromPolygons([P.matrix_world@v.co for v in pme.vertices],[tuple(p.vertices) for p in pme.polygons]); Pe.to_mesh_clear()
ske=sk.evaluated_get(dg); sme=ske.to_mesh()
bs=BVHTree.FromPolygons([sk.matrix_world@v.co for v in sme.vertices],[tuple(p.vertices) for p in sme.polygons]); ske.to_mesh_clear()
def gz(x,y):
    h=bp.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    if h[0] is not None: return h[0].z,'patch'
    h=bs.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    if h[0] is not None: return h[0].z,'skirt'
    return None,None
def tb(o):
    mw=o.matrix_world; p0=mw.translation
    P=[(mw@v.co).z for v in o.data.vertices if ((mw@v.co).xy-p0.xy).length<0.3]
    return min(P) if P else p0.z
# audit before
rows=[]
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree') or o.type!='MESH': continue
    p=o.matrix_world.translation
    if not(X0<=p.x<X1 and Y0<=p.y<Y1): continue
    g,src=gz(p.x,p.y); b=tb(o)
    rows.append(dict(n=o.name,x=round(p.x,2),y=round(p.y,2),tb=round(b,3),g=round(g,3) if g else None,src=src,
                     err=round((g+SINK)-b,3) if g else None, wf_dz=o.get('wf_dz'), we_dz=o.get('we_dz')))
errs=[r for r in rows if r['err'] is not None and abs(r['err'])>0.15]
print('N',len(rows),'off',len(errs),'wf_dz set',sum(1 for r in rows if r['wf_dz'] is not None))
print('err stats',np.percentile([r['err'] for r in rows if r['err'] is not None],[0,10,50,90,100]))
print('sample off',errs[:8])
print('sample ok',[r for r in rows if r['err'] is not None and abs(r['err'])<=0.15][:5])
# by source
from collections import Counter
print('src',Counter(r['src'] for r in rows))
print('off src',Counter(r['src'] for r in errs))
# Fix: re-reseat with view_layer update per batch
fixed=0
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree') or o.type!='MESH': continue
    p=o.matrix_world.translation
    if not(X0<=p.x<X1 and Y0<=p.y<Y1): continue
    g,src=gz(p.x,p.y)
    if g is None: continue
    b=tb(o); d=(g+SINK)-b
    if abs(d)>0.08:
        o.location.z += d
        o['wf_dz']=round(float(o.get('wf_dz',0.0))+d,3)
        fixed+=1
bpy.context.view_layer.update()
# re-audit
off2=0; rows2=[]
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree') or o.type!='MESH': continue
    p=o.matrix_world.translation
    if not(X0<=p.x<X1 and Y0<=p.y<Y1): continue
    g,src=gz(p.x,p.y); b=tb(o)
    if g is not None and abs((g+SINK)-b)>0.15: off2+=1
    rows2.append(abs((g+SINK)-b) if g else 0)
print('FIXED',fixed,'still off',off2,'maxabs',max(rows2) if rows2 else None,'med',float(np.median(rows2)))
json.dump(dict(before_off=len(errs),fixed=fixed,after_off=off2),open('data/wf/tree_fix.json','w'),indent=1)
bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects))
