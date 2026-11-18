"""What white geometry sits across lower glass? Ray from TU cam through door; list TI lower mats; list objects whose bbox crosses lower glass plane."""
import bpy, bmesh, json
from mathutils import Vector, Matrix

# door 0
G=bpy.data.objects['TJ_Blanton_entrance_0_glass_UNVERIFIED']
gv=[G.matrix_world@v.co for v in G.data.vertices]
gc=sum(gv,Vector())/len(gv)
best=None
for i in range(len(gv)):
    for j in range(i+1,len(gv)):
        d=gv[j]-gv[i]; d.z=0
        if best is None or d.length>best.length: best=d
u=best.normalized(); n=Vector((-u.y,u.x,0))
BC=Vector((141.6,450.4,0))
if (gc-BC).to_2d().dot(n.to_2d())<0: n=-n
half_w=max(abs((v-gc).dot(u)) for v in gv)
zlo=min(v.z for v in gv); zhi=max(v.z for v in gv)
print('DOOR0 gc', [round(x,3) for x in gc], 'n', [round(x,3) for x in n], 'u', [round(x,3) for x in u])
print('glass z', round(zlo,3), round(zhi,3), 'half_w', round(half_w,3))

# Objects with ANY geometry in the lower-third of the glass slab (expanded)
z_band_lo=zlo-0.05; z_band_hi=zlo+0.85  # lower ~0.85 m of glass
hits=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    # skip huge terrain
    if o.name.startswith(('Terrain','Context','RZ2','QW_DTM','SA_ground','Footpath','SG_','Trees','Grass')): continue
    if 'Webster' in o.name or 'lawn' in o.name: continue
    vs=[]
    mw=o.matrix_world
    for v in o.data.vertices:
        w=mw@v.co; d=w-gc
        if abs(d.dot(u))<=half_w+0.05 and abs(d.dot(n))<=0.5 and z_band_lo<=w.z<=z_band_hi:
            vs.append(w)
    if len(vs)>=2:
        dns=[(v-gc).dot(n) for v in vs]
        hits.append(dict(name=o.name, n=len(vs), dn=[round(min(dns),3),round(max(dns),3)],
                         z=[round(min(v.z for v in vs),3),round(max(v.z for v in vs),3)],
                         mats=[m.name if m else None for m in o.data.materials][:2]))
hits.sort(key=lambda h: h['dn'][1], reverse=True)
print('HITS in lower glass slab (any Blanton-adjacent):')
for h in hits:
    print(' ', h)

# TI Blanton lower materials / object dims
for o in bpy.data.objects:
    if not o.name.startswith('TI_Blanton'): continue
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    print('TI', o.name, 'nverts', len(vs), 'z', round(min(v.z for v in vs),2), round(max(v.z for v in vs),2),
          'mats', [m.name if m else None for m in o.data.materials])

# Check surround: is it a solid hull that occludes from front? Sample face normals facing +n
S=bpy.data.objects['TU_Blanton_entrance_0_surround_UNVERIFIED']
bm=bmesh.new(); bm.from_mesh(S.data); bm.faces.ensure_lookup_table()
mw=S.matrix_world; mi=mw.inverted()
front_faces=0; samples=[]
for f in bm.faces:
    c=mw@f.calc_center_median(); fn=(mw.to_3x3()@f.normal).normalized()
    d=c-gc
    if abs(d.dot(u))<half_w and zlo-0.2<=c.z<=zlo+1.0:
        samples.append(dict(du=round(d.dot(u),2), dn=round(d.dot(n),3), z=round(c.z,2),
                            fn_n=round(fn.dot(n),3)))
        if fn.dot(n)>0.5: front_faces+=1
print('surround lower faces', len(samples), 'outward-facing', front_faces)
print(' samples', samples[:12])
bm.free()

# Canopy?
for o in bpy.data.objects:
    if 'Blanton' in o.name and ('canopy' in o.name.lower() or 'awning' in o.name.lower() or 'door' in o.name.lower() or 'entrance' in o.name.lower()):
        vs=[o.matrix_world@v.co for v in o.data.vertices]
        if vs:
            print('ENT', o.name, 'z', round(min(v.z for v in vs),2), round(max(v.z for v in vs),2), 'n', len(vs))
