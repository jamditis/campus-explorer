import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); V=mathutils.Vector
for x in (-16.5,-15.5,-13,-11,-9,-7.6):
    up=sc.ray_cast(dg,V((x,16.2,138.5)),V((0,0,1)))
    n=sc.ray_cast(dg,V((x,15.5,140.5)),V((0,1,0)))
    n2=sc.ray_cast(dg,V((x,15.5,144.0)),V((0,1,0)))
    print('OEP x',x,'up',round(up[1].z,3) if up[0] else None, up[4].name if up[0] else None,'| N@140.5',round(n[1].y,3) if n[0] else None, n[4].name if n[0] else None,'| N@144',round(n2[1].y,3) if n2[0] else None, n2[4].name if n2[0] else None)
for x in (-17.5,-16.0):
    w=sc.ray_cast(dg,V((-14.0,16.2,140.0)),V((-1,0,0)))
print('OEP west from stair', round(w[1].x,3) if w[0] else None, w[4].name if w[0] else None)
for nm in ('NG stair','NG stair stringer','NG stair S stringer'):
    o=bpy.data.objects.get(nm); print('OEP obj',nm, bool(o), [m.name for m in o.data.materials] if o else '')
print('OEP stairs',[o.name for o in bpy.data.objects if o.name.startswith('NG stair')][:20])
print('OEP wood mats',[m.name for m in bpy.data.materials if any(k in m.name.lower() for k in ('wood','walnut','oak','teak','veneer'))][:40])
