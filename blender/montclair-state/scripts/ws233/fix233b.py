# ws233 fix b (on ws232b; supersedes fix233a, which gated the wrong row): W53o Stone Hall lower volume ground-floor windows.
# probe233a/b: evaluated ground at the lower volume's walls = 135.97..136.97 (3DEP agrees; 136.66 along the ESE walk wall), but the
# shader floor datum ti_z0 = 135.888 put the only window row at 136.84..138.31 with geometry sills at 136.78..136.86, i.e. sills
# 0.1-0.2 m over the lawn and the ground floor 0.8 m below grade. Evidence: Stone Hall has 2 floors (Montclarion 2016) and the 1966
# slides (digitalcommons slides 285/288) show the ground-floor punched windows with sills ~1 m+ over the lawn on a brick base.
# Decision: ground-floor datum = 136.9 (slab just above the highest adjacent grade 136.97, ~0.2-0.9 m over the lower sides; UNVERIFIED
# exact level) -> lower-volume ti_z0 = 136.9 (window row 137.85..139.32, under the 140.11 fascia; second row 141.05 stays gated by z1-0.9),
# geometry sills moved +1.012 m with it. upper0 keeps its own ti_z0 (its row 140.04..141.51 is unchanged).
# Also: 3 floating QS_Richardson grass points (104.9,247.2,138.97; 1.58 m over 3DEP) deleted.
import bpy, bmesh, json, numpy as np
MS='/workspace/nj-scenes/montclair-state/'; rep={}; Z0=136.9
o=bpy.data.objects['TI_Stone_Hall_313028565_lower_UNVERIFIED']; a=o.data.attributes['ti_z0']
old=sorted(set(round(x.value,3) for x in a.data)); dz=Z0-old[0]
for x in a.data: x.value=Z0
rep['lower_ti_z0']=[old,Z0,round(dz,3)]
s=bpy.data.objects['TR_Stone_window_sills_UNVERIFIED']; W=s.matrix_world; Wi=W.inverted()
for v in s.data.vertices:
    w=W@v.co; w.z+=dz; v.co=Wi@w
s.data.update(); rep['sills_moved']=len(s.data.vertices)
rep['sill_z']=sorted(set(round((W@v.co).z,2) for v in s.data.vertices))
P=np.load(MS+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
def p3(x,y):
    gx=x+280-0.5; gy=y+280-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    return float(P[i,j]*(1-fx)*(1-fy)+P[i,j+1]*fx*(1-fy)+P[i+1,j]*(1-fx)*fy+P[i+1,j+1]*fx*fy)
g=bpy.data.objects['QS_Richardson_lawn_grass_points_UNVERIFIED']; W=g.matrix_world; bm=bmesh.new(); bm.from_mesh(g.data)
dv=[v for v in bm.verts if 100<(W@v.co).x<180 and 170<(W@v.co).y<278 and (W@v.co).z-p3((W@v.co).x,(W@v.co).y)>1.0]
rep['grass_deleted']=[[round(c,2) for c in W@v.co] for v in dv]
if dv: bmesh.ops.delete(bm,geom=dv,context='VERTS'); bm.to_mesh(g.data)
bm.free()
print('F233B',json.dumps(rep),flush=True)
json.dump(rep,open(MS+'scripts/ws233/fix233b_report.json','w'))
