import bpy, collections
o=bpy.data.objects['UV_Freeman_N_entrance_curtain_doors_canopy_UNVERIFIED']
mw=o.matrix_world; me=o.data
g=collections.Counter()
for p in me.polygons:
    if p.material_index==2:
        c=mw@p.center; g[(round(c.z,1), round(c.y,1))]+=1
print('M2',sorted(g.items()))
s=bpy.data.objects['UV_Freeman_N_entrance_steps_handrails_UNVERIFIED']
g=collections.Counter()
for p in s.data.polygons:
    c=s.matrix_world@p.center
    if p.material_index==0 and abs(p.normal.z)>0.9: g[(round(c.z,2),round(c.y,1))]+=1
print('ST',sorted(g.items()))
for n in ['UV_Freeman_N_globe_pendant_UNVERIFIED','UV_Freeman_N_globe_pendant_UNVERIFIED.001']:
    ob=bpy.data.objects[n]; print('G',n,tuple(round(a,2) for a in ob.location), ob.parent)
