# ws231 fix a (W53k part 2 + W53l, NE/N scene edge paving vs ground; raise-only, AGENTS rule 6).
# probe231b (EVALUATED, drape GN on) showed the ws230 "NE street 0.75-1.3 m over 3DEP" was a raw-vertex reading: the
# evaluated street sits median +0.03 m on the ground. The real defects are paving BURIED by ground the drapes don't see:
#  (k) Roads_OSM east end x 232..238, y 186..200 up to 2.73 m and Footpaths_OSM x ~230, y ~214 up to 1.92 m under the
#      WS230_NE_east_gap_fill_3DEP_UNVERIFIED (QK_NE_end_drape raycasts Terrain, QJ_NE_seam_fill and the skirt only).
#  (l) the NE woods footpath x 150..168, y 228..250 up to 6.2 m under the terrain / WS60 apron (outside QK's box x 195..250).
# Fix: two copies of QK_NE_end_drape_GN (raise-only: paving -> max(ground hits)+offset where it is >2 cm below), appended at
# the END of the Roads_OSM / Footpaths_OSM stacks:
#  WS231_NE_fill_drape: Object Info.001 -> WS230 fill, same box (x 195..250, y 135..258)  [Roads + Footpaths]
#  WS231_N_woods_path_drape: Object Info.001 -> WS60 apron, box x 145..175, y 222..256   [Footpaths]
# The QK copies are made RAISE-ONLY (the original QK is a downward drape: it only moves paving that is >2 cm ABOVE ground).
# Plus (p) the terrain pit at x 150..168, y 245..248 (evaluated −2.8…−6.3 m under 3DEP; probe231e: it is the
# QI_east_edge_LiDAR_terrain_patch north rows, still on padded dtm_1m because fix230c kept QI verts within 2 m of paving =
# the buried path): QI and QG patch verts in x 140..250, y 225..262 more than 0.3 m under 3DEP are raised to 3DEP.
import bpy, json, numpy as np
MS='/workspace/nj-scenes/montclair-state/'
P=np.load(MS+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
def p3(x,y):
    gx=x+280-0.5; gy=y+280-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    return float(P[i,j]*(1-fx)*(1-fy)+P[i,j+1]*fx*(1-fy)+P[i+1,j]*(1-fx)*fy+P[i+1,j+1]*fx*fy)
rep={}
src=bpy.data.node_groups['QK_NE_end_drape_GN']
def mk(name,obj,box):
    ng=src.copy(); ng.name=name
    ng.nodes['Object Info.001'].inputs['Object'].default_value=bpy.data.objects[obj]
    for nn,v in zip(('Compare.001','Compare.002','Compare.003','Compare.004'),box):
        c=ng.nodes[nn]; old=c.inputs[1].default_value; c.inputs[1].default_value=v
        rep.setdefault(name,[]).append((nn,old,v))
    # RAISE-ONLY: the original QK compares A = z - (ground_max + offset) GREATER_THAN 0.02 (a downward drape). The copies
    # move a vertex only where it is more than 2 cm BELOW ground_max + offset (A LESS_THAN -0.02).
    c=ng.nodes['Compare']; assert c.inputs[0].links[0].from_node.name=='Math.005'
    c.operation='LESS_THAN'; c.inputs[1].default_value=-0.02
    return ng
# check compare semantics before editing (expect x>195, x<250, y>135, y<258)
for nn in ('Compare.001','Compare.002','Compare.003','Compare.004'):
    c=src.nodes[nn]; l=c.inputs[0].links
    rep.setdefault('qk_compare_src',[]).append((nn,c.operation,round(c.inputs[1].default_value,1),l[0].from_socket.name if l else None))
ngk=mk('WS231_NE_fill_drape_GN','WS230_NE_east_gap_fill_3DEP_UNVERIFIED',(195.0,250.0,135.0,258.0))
ngl=mk('WS231_N_woods_path_drape_GN','WS60_terrain_edge_apron_LiDAR_to_skirt',(145.0,175.0,222.0,256.0))
for on,mods in (('Roads_OSM',[('WS231_NE_fill_drape',ngk,0.03)]),('Footpaths_OSM',[('WS231_NE_fill_drape',ngk,0.05),('WS231_N_woods_path_drape',ngl,0.05)])):
    o=bpy.data.objects[on]; qk=o.modifiers['QK_NE_end_drape']
    for mn,ng,off in mods:
        m=o.modifiers.new(mn,'NODES'); m.node_group=ng
        for k in qk.keys():
            try: m[k]=qk[k]
            except Exception: pass
        m['Socket_1']=off
        m.show_viewport=qk.show_viewport or True; m.show_render=True
    rep[on]=[m.name for m in o.modifiers]
# (p) pit
for pn in ('QI_east_edge_LiDAR_terrain_patch','QG_north_strip_LiDAR_terrain_patch'):
    t=bpy.data.objects[pn]; W=t.matrix_world; I=W.inverted(); n=0; mx=0; xs=[]
    for v in t.data.vertices:
        w=W@v.co
        if 140<w.x<250 and 225<w.y<262:
            d=p3(w.x,w.y)-w.z
            if d>0.3: mx=max(mx,d); xs.append(round(w.x)); w.z=p3(w.x,w.y); v.co=I@w; n+=1
    t.data.update(); rep[pn]={'verts_raised':n,'max_raise':round(mx,2),'x_range':[min(xs),max(xs)] if xs else None}
print('F231A',json.dumps(rep),flush=True)
json.dump(rep,open(MS+'scripts/ws231/fix231a_report.json','w'))
