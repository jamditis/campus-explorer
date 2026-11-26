# ws254c: walk N extension's north end showed a ~6 cm lip over the OSM walk (138.81 m at y 190.8-193) in the eye view from N ->
# last two rows lowered so the slab dives under the OSM walk start (y 190.5 top 138.84, y 191.0 top 138.78).
import bpy
o=bpy.data.objects['WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED']; M=o.matrix_world; Mi=M.inverted(); me=o.data
for yt,zt in ((190.5,138.84),(191.0,138.78)):
    vs=[v for v in me.vertices if abs((M@v.co).y-yt)<0.01]; top=max((M@v.co).z for v in vs); d=zt-top
    for v in vs: w=M@v.co; w.z+=d; v.co=Mi@w
    print('F254C row',yt,'verts',len(vs),'top %.3f -> %.3f'%(top,zt),flush=True)
me.update()
