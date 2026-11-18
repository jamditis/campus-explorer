"""ea probe (read-only): for each dd corridor segment, list visible meshes (not the segment's own) with vertices inside its interior volume."""
import bpy, re, os
from mathutils import Vector
out=[]
def P(*a): s=' '.join(str(x) for x in a); out.append(s); print('EA',s,flush=True)
segs=sorted({m.group(1) for o in bpy.data.objects for m in [re.match(r'dd_([A-Z0-9]+)_floor_terrazzo$',o.name)] if m})
P('segs',segs)
for seg in segs:
    fl=bpy.data.objects[f'dd_{seg}_floor_terrazzo']
    tb=[o for o in bpy.data.objects if re.match(rf'dd_{seg}_tbase_\d+_(dY|dZ)$',o.name)]
    M=(tb[0].matrix_world if tb else fl.matrix_world).copy()
    Mi=M.inverted()
    own=[o for o in bpy.data.objects if o.name.startswith(f'dd_{seg}_')]
    P('SEG',seg,'nobj',len(own),'tbase frame from',tb[0].name if tb else fl.name, 'rot z deg', round(M.to_euler().z*57.2958,1), 'loc', tuple(round(c,2) for c in M.translation))
    for o in sorted(own,key=lambda o:o.name):
        if o.type!='MESH' or o.hide_render or re.search(r'_(ch|table|tbase|rug|floorbox|tped)_',o.name): continue
        L=[Mi@(o.matrix_world@v.co) for v in o.data.vertices]
        if not L: continue
        P('  own',o.name,'x',round(min(v.x for v in L),2),round(max(v.x for v in L),2),'y',round(min(v.y for v in L),2),round(max(v.y for v in L),2),'z',round(min(v.z for v in L),2),round(max(v.z for v in L),2))
    F=[Mi@(fl.matrix_world@v.co) for v in fl.data.vertices]
    x0,x1=min(v.x for v in F),max(v.x for v in F); y0,y1=min(v.y for v in F),max(v.y for v in F); zf=max(v.z for v in F)
    P('  floor box local x',round(x0,2),round(x1,2),'y',round(y0,2),round(y1,2),'ztop',round(zf,3))
    for o in bpy.data.objects:
        if o.type!='MESH' or o.hide_render or o.name.startswith(f'dd_{seg}_') or not o.data.vertices: continue
        ins=[]
        for v in o.data.vertices:
            l=Mi@(o.matrix_world@v.co)
            if x0+0.02<l.x<x1-0.02 and y0+0.02<l.y<y1-0.02 and zf+0.01<l.z<zf+3.2: ins.append(l)
        if ins:
            P('  INTRUDER',o.name,'nv_in',len(ins),'/',len(o.data.vertices),'x',round(min(v.x for v in ins),2),round(max(v.x for v in ins),2),'y',round(min(v.y for v in ins),2),round(max(v.y for v in ins),2),'z',round(min(v.z for v in ins)-zf,2),round(max(v.z for v in ins)-zf,2))
open(bpy.path.abspath('//data/ea/probe_clashes_ea.txt'),'w').write('\n'.join(out)+'\n')
