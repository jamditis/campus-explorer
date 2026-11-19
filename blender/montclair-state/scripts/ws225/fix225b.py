# W47 (cont.): flip paving/landscape sheets whose faces all point DOWN (back-facing from above in single-sided
# web-viewer exports). Only objects with NO modifiers, whose mesh users are all flagged too, and whose names are
# (closed/open solids such as planters and riser fillers are excluded: a planter's bottom legitimately faces down)
# ground-surface items (never ceilings/soffits/roofs/canopies). DRY=1 lists only.
import bpy, bmesh, os, re
DRY=os.environ.get('DRY','0')=='1'
OK=re.compile('asphalt|plaza|paver|joint|edging|mulch|patio|walk|apron|gravel|lawn|bed',re.I)
NO=re.compile('planter|filler|riser|ceil|soffit|roof|canopy|overhang|underside|bottom|eave|awning|curb',re.I)
flag={}
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or not o.data.polygons: continue
    R=o.matrix_world.to_3x3()
    a=[(R@p.normal).z*p.area for p in o.data.polygons]
    dn=-sum(x for x in a if x<0); up=sum(x for x in a if x>0)
    if dn>2*up and dn>0.2: flag[o.name]=(dn,up,len(a))
done=set(); n=0
for nm,(dn,up,nf) in sorted(flag.items()):
    o=bpy.data.objects[nm]
    if not OK.search(nm) or NO.search(nm): continue
    why=''
    if o.modifiers: why='has modifiers'
    users=[u.name for u in bpy.data.objects if u.data==o.data]
    if any(u not in flag for u in users): why='shared mesh with unflagged users'
    if o.matrix_world.determinant()<0: why='mirrored transform'
    print('P225B %s %-60s down %.1f up %.1f nf %d users %d %s'%('SKIP' if why else 'FLIP',nm[:60],dn,up,nf,len(users),why),flush=True)
    if why or o.data.name in done or DRY: continue
    bm=bmesh.new(); bm.from_mesh(o.data); bmesh.ops.reverse_faces(bm,faces=bm.faces[:]); bm.to_mesh(o.data); bm.free(); o.data.update()
    done.add(o.data.name); n+=1
print('P225B flipped meshes',n,'(dry)' if DRY else '',flush=True)
