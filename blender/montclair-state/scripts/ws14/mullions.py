"""ws14b: addition glass -> dark reflective (no transmission into the closed box, per Joe's Nov 6 glass rule);
add a centre mullion + transom (4 cm, 3 cm proud) on each addition window. UNVERIFIED pattern. SAVE=1 saves."""
import bpy, bmesh, os
from mathutils import Vector
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; me=o.data
slots=[s.material.name for s in o.material_slots]
MUL=slots.index('TZ_Cole_add_mullion_UNVERIFIED'); GLA=slots.index('TZ_Cole_add_glass_UNVERIFIED')
m=bpy.data.materials['TZ_Cole_add_glass_UNVERIFIED']; b=m.node_tree.nodes['Principled BSDF'] if 'Principled BSDF' in m.node_tree.nodes else [n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0]
b.inputs['Base Color'].default_value=(0.03,0.04,0.05,1); b.inputs['Roughness'].default_value=0.05
b.inputs['Transmission Weight'].default_value=0.0; b.inputs['IOR'].default_value=1.52
bm=bmesh.new(); bm.from_mesh(me)
seen=set(); comps=[]
for f in bm.faces:
    if f.index in seen or f.material_index!=GLA: continue
    st=[f]; c=[]; seen.add(f.index)
    while st:
        g=st.pop(); c.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in seen and h.material_index==GLA: seen.add(h.index); st.append(h)
    comps.append(c)
walls=[Vector((0.97,-0.22,0)).normalized(),Vector((-0.97,0.22,0)).normalized()]
def box(c0,W,Fn,ua,ub,za,zb,d0,d1):
    cs=[]
    for uu in (ua,ub):
        for zz in (za,zb):
            for dd in (d0,d1):
                p=c0+W*uu+Fn*dd; cs.append(bm.verts.new(Vector((p.x,p.y,zz))))
    bc=sum((v.co for v in cs),Vector())/8
    for q in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        f=bm.faces.new([cs[i] for i in q]); f.material_index=MUL; f.normal_update()
        if f.normal.dot(f.calc_center_median()-bc)<0: f.normal_flip()
n=0
for c in comps:
    vs={v for f in c for v in f.verts}; cc=sum((v.co for v in vs),Vector())/len(vs)
    Fn=None
    for w in walls:
        fr=[f for f in c if abs(f.normal.dot(w))>0.9 and (f.calc_center_median()-cc).dot(w)>0.01]
        if fr and max(fr,key=lambda f:f.calc_area()).calc_area()>0.5: Fn=w; F=max(fr,key=lambda f:f.calc_area()); break
    if Fn is None: print('NOWIN',[round(x,2) for x in cc]); continue
    W=Vector((-Fn.y,Fn.x,0)); fc=F.calc_center_median()
    us=[(v.co-fc).dot(W) for v in F.verts]; zs=[v.co.z for v in F.verts]
    u0,u1,z0,z1=min(us),max(us),min(zs),max(zs)
    ft=(fc-cc).dot(Fn)  # unused
    base=fc
    print('WIN',[round(x,2) for x in cc],round(u0,2),round(u1,2),round(z0,2),round(z1,2),len(F.verts))
    box(base,W,Fn,-0.02,0.02,z0,z1,-0.005,0.03)
    zt=z1-(z1-z0)*0.3
    box(base,W,Fn,u0,u1,zt-0.02,zt+0.02,-0.005,0.03)
    n+=1
bm.to_mesh(me); me.update(); bm.free()
print('MULLIONS',n)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
