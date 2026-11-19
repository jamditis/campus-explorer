# ws231 fix b (after fix231a): W53m + north-edge apron dip (raise-only, AGENTS rule 6)
#  (m) W53m: the SE street end (Roads_OSM x 245..250, y -38..-20) runs 0.1-0.8 m UNDER the WS60 edge apron (ws230 probe;
#      the ws230 subdivide-and-tuck of the apron opened a hole and was rejected). Instead of cutting the apron, the road is
#      lifted onto it: a third raise-only copy of QK_NE_end_drape_GN (WS231_SE_end_apron_drape, Object Info.001 = WS60 apron,
#      box x 238..252, y -44..-14) appended to Roads_OSM. Paving only goes up.
#  (a) [DROPPED, see below] north-edge apron dip x 171..176, y 249..251: WS60 apron verts 0.3-0.9 m under 3DEP (probe231b_after). WS60 verts in
#      x 145..250, y 246..252 more than 0.3 m under 3DEP raised to 3DEP (inner part of the apron only; outer edge untouched).
import bpy, json, numpy as np
MS='/workspace/nj-scenes/montclair-state/'
P=np.load(MS+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
def p3(x,y):
    gx=x+280-0.5; gy=y+280-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    return float(P[i,j]*(1-fx)*(1-fy)+P[i,j+1]*fx*(1-fy)+P[i+1,j]*(1-fx)*fy+P[i+1,j+1]*fx*fy)
rep={}
ng=bpy.data.node_groups['WS231_N_woods_path_drape_GN'].copy(); ng.name='WS231_SE_end_apron_drape_GN'
assert ng.nodes['Compare'].operation=='LESS_THAN'
ng.nodes['Object Info.001'].inputs['Object'].default_value=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']
for nn,v in zip(('Compare.001','Compare.002','Compare.003','Compare.004'),(238.0,252.0,-44.0,-14.0)): ng.nodes[nn].inputs[1].default_value=v
o=bpy.data.objects['Roads_OSM']; qk=o.modifiers['QK_NE_end_drape']
m=o.modifiers.new('WS231_SE_end_apron_drape','NODES'); m.node_group=ng
for k in qk.keys():
    try: m[k]=qk[k]
    except Exception: pass
m['Socket_1']=0.03; m.show_viewport=True; m.show_render=True
rep['Roads_OSM']=[x.name for x in o.modifiers]
# (a) DROPPED after probe231f: the low WS60 verts at y 248 are a hidden duplicate 'curtain' row under the 3DEP top row (raising
# them only collapsed hidden faces; the evaluated top was unchanged), and the 0.3-0.9 m dip at x 171..175, y 249..251 is the apron's
# designed ramp down to the skirt beyond the y 248 scene edge. Nothing changed in WS60.
print('F231B',json.dumps(rep),flush=True)
json.dump(rep,open(MS+'scripts/ws231/fix231b_report.json','w'))
