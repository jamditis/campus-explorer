"""Spandrel + base vs door glass with wider n tolerance; also mid-mullion / any white strip."""
import bpy, bmesh, json
from mathutils import Vector

def basis(k):
    G=bpy.data.objects['TJ_Blanton_entrance_%d_glass_UNVERIFIED'%k]
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
    return G,gc,u,n,half_w,zlo,zhi

# For each door, dump ALL faces of spandrel and block_base with |du|<half_w+1 and |dn|<3
for nm in ('TN_Blanton_spandrel_bands_UNVERIFIED','TN_Blanton_block_base_UNVERIFIED','TN_Blanton_piers_UNVERIFIED'):
    o=bpy.data.objects[nm]
    bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    mw=o.matrix_world
    print('====', nm, 'nfaces', len(bm.faces), 'nverts', len(bm.verts))
    for k in range(3):
        G,gc,u,n,half_w,zlo,zhi=basis(k)
        near=[]
        for f in bm.faces:
            c=mw@f.calc_center_median(); d=c-gc
            du=d.dot(u); dn=d.dot(n)
            if abs(du)<=half_w+1.5 and abs(dn)<=2.5 and zlo-1<=c.z<=zhi+1:
                near.append((round(du,2), round(dn,2), round(c.z,2), round((mw.to_3x3()@f.normal).dot(n),2)))
        near.sort(key=lambda t: (abs(t[0]), abs(t[1])))
        print(' door',k,'near faces',len(near))
        for t in near[:20]:
            print('  ', t)
    bm.free()

# Also: is there a separate mid-rail in the door glass mesh itself?
for k in range(3):
    G=bpy.data.objects['TJ_Blanton_entrance_%d_glass_UNVERIFIED'%k]
    F=bpy.data.objects['TJ_Blanton_entrance_%d_frame_UNVERIFIED'%k]
    print('GLASS',k,'verts:')
    for v in G.data.vertices:
        w=G.matrix_world@v.co; print(' ', [round(x,3) for x in w])
    print('FRAME',k,'unique z:', sorted(set(round((F.matrix_world@v.co).z,3) for v in F.data.vertices)))
    # edges that are horizontal across glass
    mw=F.matrix_world
    hz=[]
    for e in F.data.edges:
        a=mw@F.data.vertices[e.vertices[0]].co; b=mw@F.data.vertices[e.vertices[1]].co
        if abs(a.z-b.z)<0.05 and (a-b).length>1.0:
            hz.append(round((a.z+b.z)/2,3))
    print('FRAME',k,'long horizontal edges at z', sorted(set(hz)))

# Check for any object named band/spandrel/belt elsewhere near Blanton
for o in bpy.data.objects:
    if o.type!='MESH': continue
    if any(k in o.name.lower() for k in ('band','spandrel','belt','plinth','skirt','ledge','sill')):
        if 'Blanton' in o.name or 'Stone' in o.name or 'Bohn' in o.name:
            vs=[o.matrix_world@v.co for v in o.data.vertices]
            print('BANDISH', o.name, 'z', round(min(v.z for v in vs),2), round(max(v.z for v in vs),2), 'n', len(vs))
