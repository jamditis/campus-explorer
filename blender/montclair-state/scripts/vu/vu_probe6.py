import bpy, bmesh
from mathutils import Vector
SP=bpy.data.objects['TN_Blanton_spandrel_bands_UNVERIFIED']
bm=bmesh.new(); bm.from_mesh(SP.data); bm.verts.ensure_lookup_table()
mw=SP.matrix_world
# islands
seen=set(); islands=[]
for v in bm.verts:
    if v.index in seen: continue
    st=[v]; isl=[]; seen.add(v.index)
    while st:
        a=st.pop(); isl.append(a)
        for e in a.link_edges:
            b=e.other_vert(a)
            if b.index not in seen: seen.add(b.index); st.append(b)
    ws=[mw@x.co for x in isl]
    c=sum(ws,Vector())/len(ws)
    islands.append((c, ws, min(p.z for p in ws), max(p.z for p in ws)))
print('spandrel islands', len(islands))
# lowest storey islands only
low=[(c,ws,z0,z1) for c,ws,z0,z1 in islands if z1<138.0]
print('lowest-storey islands', len(low))
# door 0 basis
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
# sort low islands by du along south wall (door 0)
items=[]
for c,ws,z0,z1 in low:
    d=c-gc
    # only those near this wall (small |dn| relative to wall)
    if abs(d.dot(n))<3.0:
        items.append((d.dot(u), d.dot(n), z0, z1, len(ws),
                      min((p-gc).dot(u) for p in ws), max((p-gc).dot(u) for p in ws)))
items.sort()
print('low islands near door0 wall (du, dn, z0, z1, nverts, du_lo, du_hi):')
for t in items:
    print(' ', tuple(round(x,2) if isinstance(x,float) else x for x in t))

# Same for doors 1 and 2
for k in (1,2):
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
    items=[]
    for c,ws,z0,z1 in low:
        d=c-gc
        if abs(d.dot(n))<3.0:
            items.append((round(d.dot(u),2), round(d.dot(n),2), round(min((p-gc).dot(u) for p in ws),2), round(max((p-gc).dot(u) for p in ws),2), len(ws)))
    items.sort()
    print('door',k,'half_w',round(half_w,2),'nearby low islands', items)

# CRITICAL: do any low spandrel islands SPAN across du=0 (door center)?
print('--- islands that straddle du=0 for each door ---')
for k in range(3):
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
    for c,ws,z0,z1 in islands:
        dus=[(p-gc).dot(u) for p in ws]; dns=[(p-gc).dot(n) for p in ws]
        if min(dus)<0<max(dus) and abs(sum(dns)/len(dns))<2.0 and z0<140:
            print(' door',k,'STRADDLE z',round(z0,2),round(z1,2),'du',round(min(dus),2),round(max(dus),2),'dn',round(min(dns),2),round(max(dns),2),'n',len(ws))
bm.free()
