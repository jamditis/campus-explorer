# pu: Dickson west/south "top strip" -- the 352 steep LiDAR roof-edge faces (z 147.7-150.1, parapet band above the walls)
# already use the Dickson facade brick (slot 3) but the roof mesh had no 'facade' UV, so the Brick Texture sampled one
# point (mortar) and the whole band rendered as a flat white strip. Add a 'facade' UV on the roof mesh: u = metres along
# the face, v = 20 + (z - 147) so v > win_top (no shader windows) -> same brick coursing as the wall below.
# Parapet as brick UNVERIFIED (no west-face photo). REVERT=1 removes the UV layer (mesh geometry untouched).
import bpy, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
r=bpy.data.objects['Dickson Hall roof (LiDAR)']; me=r.data
if 'facade' in me.uv_layers and r.get('pu_topstrip_uv'):
    me.uv_layers.remove(me.uv_layers['facade']); del r['pu_topstrip_uv']; print('REVERTED_PU_TOPSTRIP')
if not REV:
    bad=[]
    for i,s in enumerate(r.material_slots):
        m=s.material
        if not m or not m.use_nodes or i==3: continue
        for l in m.node_tree.links:
            if (l.from_node.type=='TEX_COORD' and l.from_socket.name=='UV') or (l.from_node.type=='UVMAP' and l.from_node.uv_map==''): bad.append(m.name)
            if l.to_node.type=='TEX_IMAGE' and l.to_socket.name=='Vector': pass
        for n in m.node_tree.nodes:
            if n.type in ('TEX_IMAGE','NORMAL_MAP') and not any(i.is_linked for i in n.inputs if i.name=='Vector') and n.type=='TEX_IMAGE': bad.append(m.name+':unlinked_img')
    if bad: print('PU_TOPSTRIP_ABORT',bad)
    else:
        uvl=me.uv_layers.new(name='facade'); d=uvl.data; mw=r.matrix_world; n3=mw.to_3x3(); k=0
        for p in me.polygons:
            n=(n3@p.normal)
            for li in p.loop_indices:
                co=mw@me.vertices[me.loops[li].vertex_index].co
                if abs(n.normalized().z)<0.35:
                    t=Vector((-n.y,n.x,0)).normalized(); d[li].uv=(co.dot(t), 20.0+(co.z-147.0))
                else: d[li].uv=(co.x*0.0, 30.0)
            k+=abs(n.normalized().z)<0.35
        r['pu_topstrip_uv']=1; print('PU_TOPSTRIP faces',k)
