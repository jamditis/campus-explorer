# Session ed (Oct 21 2026 ~6:45 PM ET), after ccom_forecourt_edge_clean_20261021ed.py: DTM triangles and grass blades
# still overlapped the forecourt edge in a wavy line. Lawn within 0.8 m outside the paving is eased down to just below the
# paving edge (z <= edge_z - 0.015 + 0.05*d); grass points under the paving or within 0.25 m of its edge are sunk 1 m (hidden), others within
# 0.8 m follow the lawn. Orig z kept in point attribute ed2_orig_z on each touched mesh. SAVE=1 saves; REVERT=1 undoes.
import bpy, bmesh, os, re, mathutils
from mathutils.bvhtree import BVHTree
fc=bpy.data.objects['CCOM brick forecourt (ortho + photo)']
bm=bmesh.new(); bm.from_mesh(fc.data); bm.transform(fc.matrix_world)
bvh=BVHTree.FromBMesh(bm)
bnd=[(e.verts[0].co.copy(),e.verts[1].co.copy()) for e in bm.edges if e.is_boundary]
xs=[v.co.x for v in bm.verts]; ys=[v.co.y for v in bm.verts]
def inside(x,y,z):
    return bvh.ray_cast(mathutils.Vector((x,y,z+30)),mathutils.Vector((0,0,-1)))[0] is not None
def edge_info(p):
    best=(1e9,None)
    for a,b in bnd:
        a2=a.xy; b2=b.xy; ab=b2-a2; t=max(0,min(1,(p.xy-a2).dot(ab)/ab.length_squared)); q=a2+ab*t
        d=(p.xy-q).length
        if d<best[0]: best=(d,a.z+(b.z-a.z)*t)
    return best
targets=[bpy.data.objects['Terrain_LiDAR_DTM_1m']]+[o for o in bpy.data.objects if o.type=='MESH' and re.match(r'(?i)^(dS_grass|cx_grass|cd_grass|Lawn_grass_instanced)',o.name)]
REV=os.environ.get('REVERT')=='1'
for o in targets:
    me=o.data; mw=o.matrix_world; inv=mw.inverted(); grass=o.name!='Terrain_LiDAR_DTM_1m'
    if REV:
        a=me.attributes.get('ed2_orig_z')
        if a:
            for v,d in zip(me.vertices,a.data):
                if d.value>-9000: v.co.z=d.value
            me.attributes.remove(a); me.update(); print('ED2_REVERT',o.name)
        continue
    a=me.attributes.get('ed2_orig_z')
    if a is None:
        a=me.attributes.new('ed2_orig_z','FLOAT','POINT')
        vals=[-9999.0]*len(me.vertices); a.data.foreach_set('value',vals)
    n=s=0
    for i,v in enumerate(me.vertices):
        w=mw@v.co
        if not (min(xs)-0.9<w.x<max(xs)+0.9 and min(ys)-0.9<w.y<max(ys)+0.9): continue
        ins=inside(w.x,w.y,w.z)
        if ins and not grass: continue
        d,ez=edge_info(w)
        if d>0.8 and not ins: continue
        orig=a.data[i].value if a.data[i].value>-9000 else v.co.z
        wo=mw@mathutils.Vector((v.co.x,v.co.y,orig))
        if grass and (ins or d<0.25): zt=wo.z-1.0; s+=1
        else:
            zt=min(wo.z, ez-0.015+0.05*d)
        if abs(zt-w.z)>1e-5:
            a.data[i].value=orig; v.co.z=(inv@mathutils.Vector((w.x,w.y,zt))).z; n+=1
    me.update(); print('ED2_APPLIED',o.name,'moved',n,'sunk',s)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('ED_SAVED')
