# ws21: Terrain_LiDAR_DTM_1m has scattered 1-cell holes (missing faces) in the lawn/court north of Life Hall; the void below shows as dark cracks/'broken paving'.
# Fill small holes (<=8 sides) inside the corridor box; copy each new loop's UVs/material from the vertex's existing faces.
import bpy,bmesh,os
SAVE=os.environ.get('SAVE')=='1'
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']; M=o.matrix_world; Mi=M.inverted()
print('TERRAIN faces',len(o.data.polygons),'mods',[m.type for m in o.modifiers],'uv',[u.name for u in o.data.uv_layers])
bm=bmesh.new(); bm.from_mesh(o.data)
X0,X1,Y0,Y1=-200,200,-200,200
bedges=[e for e in bm.edges if e.is_boundary and all(X0<(M@v.co).x<X1 and Y0<(M@v.co).y<Y1 for v in e.verts)]
print('boundary edges in box',len(bedges))
res=bmesh.ops.holes_fill(bm,edges=bedges,sides=8)
nf=res['faces']; print('NEW faces',len(nf))
uvs=bm.loops.layers.uv
for f in nf:
    for l in f.loops:
        src=[ol for ol in l.vert.link_loops if ol.face not in nf]
        if src:
            for k in uvs.keys(): l[uvs[k]].uv=src[0][uvs[k]].uv.copy()
    nb=[g for e in f.edges for g in e.link_faces if g is not f and g not in nf]
    if nb: f.material_index=nb[0].material_index; f.smooth=nb[0].smooth
import collections
c=collections.Counter((int((M@f.calc_center_median()).x//25)*25,int((M@f.calc_center_median()).y//25)*25) for f in nf)
print('WHERE',sorted(c.items(),key=lambda x:-x[1])[:20])
if SAVE:
    bm.to_mesh(o.data); o.data.update(); o['ws21']='small holes filled (holes_fill sides<=8, box +-200)'
    bpy.ops.wm.save_mainfile(); print('SAVED')
