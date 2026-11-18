# ws32: walk crossing the CCOM dock apron z-fought with it (±2 cm). Lower apron under the walk (+0.3 m buffer) to walk-4 cm,
# then seat terrain >=5 cm under apron/walk in the box; vary the apron asphalt tone.
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
def bvh(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(o.matrix_world); e.to_mesh_clear()
    t=BVHTree.FromBMesh(b); b.free(); return t
FP=bvh('Footpaths_OSM')
D=Vector((0,0,-1))
ap=bpy.data.objects['CCOM_dock_apron_20261014jf3']; mw=ap.matrix_world; mi=mw.inverted()
n=0; mx=0
OFF=[(0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3),(0.21,0.21),(-0.21,0.21),(0.21,-0.21),(-0.21,-0.21)]
for v in ap.data.vertices:
    p=mw@v.co; zs=[]
    for dx,dy in OFF:
        h=FP.ray_cast(Vector((p.x+dx,p.y+dy,p.z+3)),D,6)
        if h[0] is not None: zs.append(h[0].z)
    if zs:
        t=max(min(zs)-0.04,p.z-0.08)
        if p.z>t:
            mx=max(mx,p.z-t); p.z=t; v.co=mi@p; n+=1
ap.data.update(); print('apron verts lowered',n,'max',round(mx,3))
dg.update()
AP=bvh('CCOM_dock_apron_20261014jf3'); FP=bvh('Footpaths_OSM')
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tw=ter.matrix_world; ti=tw.inverted(); k=0
for v in ter.data.vertices:
    p=tw@v.co
    if not(-4<p.x<16 and -41<p.y<-20): continue
    zs=[h[0].z for h in (AP.ray_cast(Vector((p.x,p.y,p.z+3)),D,8),FP.ray_cast(Vector((p.x,p.y,p.z+3)),D,8)) if h[0] is not None]
    if zs and p.z>min(zs)-0.05:
        p.z=min(zs)-0.05; v.co=ti@p; k+=1
ter.data.update(); print('terrain verts seated',k)
# apron asphalt: subtle large/small tone variation + roughness variation (was flat 0.14)
m=bpy.data.materials['CCOM_dock_asphalt_20261014jf3']; nt=m.node_tree; b=nt.nodes['Principled BSDF']
if 'WS32_noise' not in nt.nodes:
    tc=nt.nodes.new('ShaderNodeTexCoord')
    nz=nt.nodes.new('ShaderNodeTexNoise'); nz.name='WS32_noise'; nz.inputs['Scale'].default_value=0.35; nz.inputs['Detail'].default_value=6; nz.inputs['Roughness'].default_value=0.55
    nf=nt.nodes.new('ShaderNodeTexNoise'); nf.name='WS32_fine'; nf.inputs['Scale'].default_value=40; nf.inputs['Detail'].default_value=2
    nt.links.new(tc.outputs['Object'],nz.inputs['Vector']); nt.links.new(tc.outputs['Object'],nf.inputs['Vector'])
    mix=nt.nodes.new('ShaderNodeMix'); mix.data_type='FLOAT'; mix.inputs[0].default_value=0.35
    nt.links.new(nz.outputs['Fac'],mix.inputs[2]); nt.links.new(nf.outputs['Fac'],mix.inputs[3])
    cr=nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position=0.35; cr.color_ramp.elements[0].color=(0.125,0.122,0.118,1)
    cr.color_ramp.elements[1].position=0.68; cr.color_ramp.elements[1].color=(0.19,0.185,0.175,1)
    nt.links.new(mix.outputs[0],cr.inputs['Fac']); nt.links.new(cr.outputs['Color'],b.inputs['Base Color'])
    rr=nt.nodes.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value=0.78; rr.inputs['To Max'].default_value=0.95
    nt.links.new(nf.outputs['Fac'],rr.inputs['Value']); nt.links.new(rr.outputs['Result'],b.inputs['Roughness'])
    bm=nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value=0.12; bm.inputs['Distance'].default_value=0.003
    nt.links.new(nf.outputs['Fac'],bm.inputs['Height']); nt.links.new(bm.outputs['Normal'],b.inputs['Normal'])
    print('apron material varied')
