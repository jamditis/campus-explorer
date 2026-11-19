# ws224e: College Ave paving sheets with every face pointing DOWN (WS27 carriageway, WS67 gap asphalt): renders fine in
# Cycles but is back-facing from above for single-sided exports (web viewer). No modifiers on either -> flip all faces.
import bpy
for nm in ('WS27_CollegeAve_carriageway_2020ortho','WS67_CollegeAve_gap_asphalt'):
    o=[o for o in bpy.data.objects if o.name.startswith(nm)][0]; R=o.matrix_world.to_3x3()
    assert not o.modifiers, o.name
    up=sum(1 for p in o.data.polygons if (R@p.normal).z>0)
    if up==0:
        o.data.flip_normals(); o.data.update()
    print('F224E',o.name[:40],'up before',up,'after',sum(1 for p in o.data.polygons if (R@p.normal).z>0),'of',len(o.data.polygons),flush=True)
