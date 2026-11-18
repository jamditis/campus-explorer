import bpy
c=bpy.data.collections.get('Buildings_context')
print('Buildings_context count', len(c.objects) if c else None)
if c:
    for o in sorted(c.objects, key=lambda x:x.name):
        if o.type=='MESH' and ('wall' in o.name.lower() or 'roof' in o.name.lower() or 'Hall' in o.name or 'Building' in o.name):
            zs=[(o.matrix_world@v.co).z for v in o.data.vertices]
            print(f"  {o.name[:75]:75s} z=[{min(zs):.1f},{max(zs):.1f}] n={len(zs)} hide={o.hide_get()}")

# Finley detail: wall max vs roof up-face
for pref in ['Finley Hall','Sprague Library','Calcia Hall']:
    wo=bpy.data.objects.get(pref+' walls')
    ro=bpy.data.objects.get(pref+' roof (LiDAR)')
    wz=sorted((wo.matrix_world@v.co).z for v in wo.data.vertices)
    up=[]
    rmw=ro.matrix_world
    for f in ro.data.polygons:
        n=(rmw.to_3x3()@f.normal).normalized()
        if n.z>0.7: up.append((rmw@f.center).z)
    up=sorted(up)
    print(f"\n{pref}: wall_max={wz[-1]:.3f} roof_up=[{up[0]:.3f},{up[-1]:.3f}] med={up[len(up)//2]:.3f} gap_to_med={up[len(up)//2]-wz[-1]:+.3f}")
    # top 20 wall verts
    print('  top20 wall z:', [round(z,3) for z in wz[-20:]])
