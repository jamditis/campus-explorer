import bpy
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src) as (fr,to): allo=list(fr.objects)
pref=('KY_','KX_','WS27','WS35','WS38','WS39','WS40','LH_college','eu_','ce_','fu_')
n=[x for x in allo if x.startswith(pref) or 'College' in x or 'curb' in x.lower()]
print('N',len(n))
with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=n
for o in to.objects:
    if not o: continue
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]; zs=[p.z for p in bb]
    if max(xs)<-300 or min(xs)>-200 or o.type!='MESH': continue
    # verts near gap
    me=o.data; mw=o.matrix_world
    g=[mw@v.co for v in me.vertices]
    near=[p for p in g if -262<p.x<-243]
    s=''
    if near: s='gap n=%d x%.1f..%.1f y%.1f..%.1f z%.2f..%.2f'%(len(near),min(p.x for p in near),max(p.x for p in near),min(p.y for p in near),max(p.y for p in near),min(p.z for p in near),max(p.z for p in near))
    print('CK',o.name[:48],o.parent.name[:20] if o.parent else '-',len(me.polygons),round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(zs),2),round(max(zs),2),s)
