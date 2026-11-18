import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
def caster(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); mw=o.matrix_world; iw=mw.inverted()
    d=(iw.to_3x3()@Vector((0,0,-1))).normalized()
    def f(x,y):
        r=e.ray_cast(iw@Vector((x,y,400)),d); return (mw@r[1]).z if r[0] else None
    return f
UG=caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED'); SA=caster('SA_ground_lower_patch_UNVERIFIED'); DT=caster('Terrain_LiDAR_DTM_1m')
def gnd(x,y):
    for c in (UG,SA,DT):
        z=c(x,y)
        if z is not None: return z
    return None
o=bpy.data.objects['QXP_pedestrian_area_313024781_paving_UNVERIFIED']
mw=o.matrix_world; me=o.data
eu={}
for p in me.polygons:
    for ek in p.edge_keys: eu[ek]=eu.get(ek,0)+1
# south-ish boundary verts (low y among region)
bv=[]
for ek,c in eu.items():
    if c!=1: continue
    for vi in ek:
        p=mw@me.vertices[vi].co
        if -68<p.x<-40 and 244<p.y<252:
            bv.append((vi,p.x,p.y,p.z,gnd(p.x,p.y)))
bv.sort(key=lambda t:t[2])
print('QXP boundary in box',len(bv))
for t in bv[:40]:
    dz=(t[3]-t[4]) if t[4] is not None else None
    print('B',t,'dz',dz)
# face normals near south: find near-horizontal vs vertical
print('--- faces with low |nz| (vertical-ish) near y246 ---')
nvert=0
for p in me.polygons:
    c=mw@p.center
    if -65<c.x<-48 and 245<c.y<250:
        n=(mw.to_3x3()@p.normal).normalized()
        if abs(n.z)<0.35:
            nvert+=1
            if nvert<=15:
                print('VF',p.index,c,n, 'mat', me.materials[p.material_index].name if me.materials else None)
print('vertical-ish faces',nvert)
# materials on QXP
print('mats',[m.name if m else None for m in me.materials])
