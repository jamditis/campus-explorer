# pn: dark-fascia eaves (0.65 m overhang, red tile top, soffit) round the exposed edges of the pn tiers 153.3/156.6/161.3 (UNVERIFIED, after feliciano_commons_08). REVERT=1 removes.
import bpy, bmesh, json, os, sys
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv; OUT=os.environ.get('SAVEAS')
ON='PN_Feliciano_eaves_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me); print('REVERTED_PN_EAVES')
if not REV:
    E=json.load(open('data/pn/eaves.json')); M=bpy.data.materials
    bm=bmesh.new(); TH=0.12; BT=0.22
    for e in E:
        loops=[e['ext']]+e['holes']; z=e['z']
        tris=tessellate_polygon([[Vector((x,y,0)) for x,y in L] for L in loops]); flat=[q for L in loops for q in L]
        top=[bm.verts.new((x,y,z+TH)) for x,y in flat]; bot=[bm.verts.new((x,y,z-BT)) for x,y in flat]
        for a,b,c in tris:
            try: bm.faces.new((top[a],top[b],top[c])).material_index=0
            except ValueError: pass
            try: bm.faces.new((bot[c],bot[b],bot[a])).material_index=1
            except ValueError: pass
        off=0
        for L in loops:
            n=len(L)
            for i in range(n):
                a,b=off+i,off+(i+1)%n
                try: bm.faces.new((bot[a],bot[b],top[b],top[a])).material_index=2
                except ValueError: pass
            off+=n
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(ON); bm.to_mesh(me); bm.free()
    for n in ('PI_Feliciano_roof_tile_forced_UNVERIFIED','Eave_tile_top_soffit_under','Eave_fascia_dark_wood'): me.materials.append(M[n])
    o=bpy.data.objects.new(ON,me); bpy.data.collections['PN_Feliciano_remass_20261101pn_UNVERIFIED'].objects.link(o)
    print('PN_EAVES faces',len(me.polygons))
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED_AS',OUT)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
