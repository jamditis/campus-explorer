# ws88: College Ave <-> accessible-lot strip (terrain lawn) -> dark mulch median overlay (Joe catwalk_01/03/04, Nov 12 9:19 AM)
import bpy,bmesh,os
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
X0,X1,Y0,Y1,S=-260.0,-224.0,-74.0,-58.0,0.5
nx=int((X1-X0)/S); ny=int((Y1-Y0)/S)
def ground(x,y):
    o0=Vector((x,y,150))
    for _ in range(8):
        ok,loc,n,i,o,_=sc.ray_cast(dg,o0,Vector((0,0,-1)))
        if not ok: return None
        if o.name.startswith('T_') or o.hide_render or 'DTM_target' in o.name: o0=loc-Vector((0,0,0.01)); continue
        mn=''
        if o.type=='MESH' and o.data.polygons and i<len(o.data.polygons):
            mi=o.data.polygons[i].material_index; ms=o.data.materials
            mn=ms[mi].name if mi<len(ms) and ms[mi] else ''
        return o.name,mn,loc.z
    return None
grid={}; rows=[]
for j in range(ny):
    row=''
    for i in range(nx):
        x=X0+(i+0.5)*S; y=Y0+(j+0.5)*S; g=ground(x,y)
        c='.'
        if g:
            if g[0]==T.name and any(k in g[1].lower() for k in ('lawn','grass','turf')): c='L'; grid[(i,j)]=g[2]
            elif 'mulch' in g[1].lower(): c='m'
            elif 'asphalt' in g[1].lower() or 'lot' in g[0].lower(): c='a'
            elif 'curb' in (g[0]+g[1]).lower(): c='c'
            else: c='o'
        row+=c
    rows.append(row)
for r in reversed(rows): print('P88M',r)
print('P88M lawn cells',len(grid))
if os.environ.get('BUILD')=='1':
    YLO,YHI=float(os.environ.get('YLO','-71')),float(os.environ.get('YHI','-62'))
    bm=bmesh.new(); vs={}
    def V(i,j):
        if (i,j) not in vs:
            x=X0+i*S; y=Y0+j*S
            r=T.evaluated_get(dg).ray_cast(T.matrix_world.inverted()@Vector((x,y,150)),Vector((0,0,-1)))
            z=(T.matrix_world@r[1]).z if r[0] else grid.get((min(i,nx-1),min(j,ny-1)),126)
            vs[(i,j)]=bm.verts.new((x,y,z+0.035))
        return vs[(i,j)]
    n=0
    for (i,j),z in grid.items():
        y=Y0+(j+0.5)*S
        if not (YLO<y<YHI): continue
        bm.faces.new((V(i,j),V(i+1,j),V(i+1,j+1),V(i,j+1))); n+=1
    me=bpy.data.meshes.new('WS88_median_mulch'); bm.to_mesh(me); bm.free()
    mat=bpy.data.materials.get('WS87_median_mulch_dark_JOEphoto') or bpy.data.materials['WS3_Mulch_bark_dark_brown']
    me.materials.append(mat)
    for o in [o for o in bpy.data.objects if o.name.startswith('WS88_CollegeAve_lot_median')]: bpy.data.objects.remove(o)
    ob=bpy.data.objects.new('WS88_CollegeAve_lot_median_MULCH_JOEphoto20261112_drape35mm_UNVERIFIED_edges',me)
    bpy.data.objects['WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020'].users_collection[0].objects.link(ob)
    print('A88 median faces',n,'mat',mat.name)
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('A88 saved')
