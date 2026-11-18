import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=['Terrain_LiDAR_DTM_1m']
o=to.objects[0]; bpy.context.scene.collection.objects.link(o)
D=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
dn=o.modifiers['QI_east_edge_LiDAR_patch'].node_group.nodes['Delete Geometry']
print('QT domain',dn.domain,dn.mode)
def run(tag):
    dg=bpy.context.evaluated_depsgraph_get()
    bm=bmesh.new(); bm.from_mesh(o.evaluated_get(dg).to_mesh()); bm.transform(o.matrix_world); T=BVHTree.FromBMesh(bm)
    miss=0; dev=[]
    for x in np.arange(88,246,1.0):
        for y in np.arange(-80,-50,1.0):
            r=T.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0]
            if not r or r.z<50: miss+=1
            else: dev.append(abs(r.z-D[int(y+250),int(x+250)]))
    dev=np.array(dev); print('QT',tag,'miss',miss,'dev>0.5',(dev>0.5).sum(),'max',round(dev.max(),2),'p95',round(np.percentile(dev,95),2))
run('orig')
dn.domain='FACE'; run('face')
m=o.modifiers['QI_east_edge_LiDAR_patch']; m.show_viewport=False; run('noQI'); m.show_viewport=True
ng=m.node_group; N=ng.nodes; L=ng.links
gi=N['Group Input']; rc=N['Raycast']
cap=N.new('GeometryNodeCaptureAttribute'); cap.domain='POINT'
cap.capture_items.new('BOOLEAN','hit')
for l in list(L):
    if l.to_node==dn: L.remove(l)
L.new(gi.outputs[0],cap.inputs[0]); L.new(rc.outputs['Is Hit'],cap.inputs[1])
L.new(cap.outputs[0],dn.inputs['Geometry']); L.new(cap.outputs[1],dn.inputs['Selection'])
run('pointcapture')
def prof(tag):
    dg=bpy.context.evaluated_depsgraph_get()
    bm=bmesh.new(); bm.from_mesh(o.evaluated_get(dg).to_mesh()); bm.transform(o.matrix_world); T=BVHTree.FromBMesh(bm)
    for x in (100,115,130,160,200):
        s=[]
        for y in range(-54,-82,-2):
            r=T.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0]
            s.append('%+.1f'%(r.z-D[int(y+250),int(x+250)]) if r and r.z>50 else ' nan')
        print('QP',tag,x,' '.join(s))
prof('fixed')
for mm in o.modifiers: mm.show_viewport=False
prof('base')
o.modifiers['PB_terrain_fan_regrid'].show_viewport=True; prof('PBonly')
