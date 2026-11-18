# ws189b: Sprague Field S goalpost (gooseneck) from LiDAR 2023 + NJOGIS 2020 ortho (prep/ws181_lot36/ortho181.jpg).
# Evidence: LiDAR class-1 returns form a horizontal band at z 118.77-118.89 (median ~118.82) over x -352.0..-346.7
# (data clipped at x -352), y -211.7..-209.8; class-2 ground 115.78-115.79 -> 3.04 m = 10 ft NCAA crossbar height;
# centre x -349.4 => 5.64 m (18 ft 6 in NCAA width) spans -352.2..-346.6. Ortho: pale rectangle x -352.8..-345.0 (uprights leaning)
# with a stem to y ~-212.6 => gooseneck base ~1.9 m S of the crossbar (typical 6 ft offset). Uprights not resolved in LiDAR
# (thin) -> 30 ft above the bar = UNVERIFIED; colour pale yellow from the ortho tone = UNVERIFIED; no base pad modelled (no source).
import bpy, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
CX=-349.4; YB=-212.6; YC=-210.7; GZ0=115.785
def ground189(x,y):
    best=None
    for o in bpy.data.objects:
        if o.type!='MESH' or not any(s in o.name.lower() for s in ('turf','sprague')) or o.hide_render: continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if not (min(v.x for v in bb)<=x<=max(v.x for v in bb) and min(v.y for v in bb)<=y<=max(v.y for v in bb)): continue
        bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free()
        h=t.ray_cast(Vector((x,y,140)),Vector((0,0,-1)))[0]
        if h and h.z<GZ0+0.5 and (best is None or h.z>best[0]): best=(h.z,o.name)
    return best
gb=ground189(CX,YB); gc=ground189(CX,YC)
print('FIX189B ground base',gb,'bar',gc,flush=True)
GZ=gb[0] if gb else GZ0
ZB=GZ0+3.05 if not gc else gc[0]+3.05
mat=bpy.data.materials.get('WS189_goalpost_paleyellow_UNVERIFIED') or bpy.data.materials.new('WS189_goalpost_paleyellow_UNVERIFIED')
mat.use_nodes=True; p=mat.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(0.78,0.72,0.38,1); p.inputs['Roughness'].default_value=0.45
p.inputs['Metallic'].default_value=0.2
col=bpy.data.collections.get('WS189_Sprague_goalpost') or bpy.data.collections.new('WS189_Sprague_goalpost')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in list(col.objects): bpy.data.objects.remove(o)
def tube(name,pts,r):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=r; cu.bevel_resolution=3; cu.use_fill_caps=True
    sp=cu.splines.new('POLY'); sp.points.add(len(pts)-1)
    for i,q in enumerate(pts): sp.points[i].co=(q[0],q[1],q[2],1)
    o=bpy.data.objects.new(name,cu); col.objects.link(o); o.data.materials.append(mat); return o
# gooseneck: vertical base, smooth bend forward (N) up to the crossbar centre
arc=[(CX,YB,GZ-0.05),(CX,YB,ZB-0.9)]
for i in range(1,9):
    a=math.radians(90*i/8); arc.append((CX,YB+(YC-YB)*math.sin(a)*0.55, ZB-0.9+0.9*(1-math.cos(a))*0.9))
arc.append((CX,YC,ZB))
tube('WS189_goalpost_gooseneck_LiDAR2023_ortho2020',arc,0.11)
tube('WS189_goalpost_crossbar_10ft_LiDAR2023',[(CX-2.82,YC,ZB),(CX+2.82,YC,ZB)],0.07)
for s in (-1,1):
    tube(f'WS189_goalpost_upright_{"W" if s<0 else "E"}_30ft_UNVERIFIED',[(CX+s*2.82,YC,ZB),(CX+s*2.82,YC,ZB+9.14)],0.055)
print('FIX189B goalpost built cx',CX,'bar y',YC,'z',round(ZB,3),'base y',YB,'gz',round(GZ,3),'objs',len(col.objects),flush=True)
