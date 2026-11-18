# ws59: retone the far/mid woods canopy carpet (MID_canopy_carpet_leaf_ai + static MID_canopy_green_*) from summer green to a mid-November NJ mix (russet/bronze oaks, dull gold, olive, some evergreen). Idempotent.
import bpy
m=bpy.data.materials['MID_canopy_carpet_leaf_ai']; nt=m.node_tree
r=nt.nodes['ah_ramp'].color_ramp; r.interpolation='CONSTANT'
P=[(0.0,(0.018,0.035,0.014)),(0.14,(0.050,0.042,0.020)),(0.30,(0.085,0.036,0.014)),(0.46,(0.100,0.056,0.020)),(0.60,(0.060,0.052,0.045)),(0.74,(0.130,0.085,0.025)),(0.84,(0.070,0.058,0.050)),(0.93,(0.026,0.046,0.018))]  # v2: more russet/brown + bare grey-brown crowns, less gold
while len(r.elements)>1: r.elements.remove(r.elements[-1])
r.elements[0].position=P[0][0]; r.elements[0].color=(*P[0][1],1)
for p,c in P[1:]:
    e=r.elements.new(p); e.color=(*c,1)
aj=nt.nodes['AJ_mix']
for i in aj.inputs:
    if i.type=='RGBA' and not i.is_linked: i.default_value=(0.22,0.16,0.08,1)
for n in ('MID_canopy_green_0_20261014x','MID_canopy_green_1_20261014x','MID_canopy_green_2_20261014x','MID_canopy_carpet_20261014x'):
    mm=bpy.data.materials.get(n)
    if not mm: continue
    b=[x for x in mm.node_tree.nodes if x.type=='BSDF_PRINCIPLED'][0]
    b.inputs['Base Color'].default_value={'MID_canopy_green_0_20261014x':(0.10,0.045,0.014,1),'MID_canopy_green_1_20261014x':(0.12,0.075,0.018,1),'MID_canopy_green_2_20261014x':(0.035,0.045,0.018,1),'MID_canopy_carpet_20261014x':(0.07,0.05,0.02,1)}[n]
print('A59 retoned')
