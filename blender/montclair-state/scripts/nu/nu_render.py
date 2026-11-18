import bpy, os, bmesh, mathutils
# nu: nt render chain + for cutaway cams (render-time only, not saved): dark section poche caps on the cut wall tops
# (up-facing, narrow top faces of wall/shell meshes inside the CCOM cut region), 4 mm above the top so they read as a section cut.
_cams=os.environ['CAMS'].split(','); _nu=[]
if any('cutaway' in c for c in _cams) and os.environ.get('NOPOCHE')!='1':
    W=float(os.environ.get('POCHEW','0.65'))
    mat=bpy.data.materials.get('NU_section_poche_charcoal_render_only') or bpy.data.materials.new('NU_section_poche_charcoal_render_only')
    mat.use_nodes=True; b=mat.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(0.035,0.033,0.032,1); b.inputs['Roughness'].default_value=0.85
    bm=bmesh.new(); nobj=0; nf=0
    def _bb(o):
        cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [min(c[i] for c in cs) for i in range(3)],[max(c[i] for c in cs) for i in range(3)]
    for o in list(bpy.data.objects):
        if o.type!='MESH' or o.hide_render: continue
        nm=o.name.lower()
        if not (('wall' in nm or 'room shell' in nm or 'partition' in nm or 'pilaster' in nm or 'jamb' in nm) and 'glass' not in nm and 'skirting' not in nm and 'plaque' not in nm): continue
        lo,hi=_bb(o)
        if not (hi[0]>-24 and lo[0]<17 and hi[1]>-17 and lo[1]<29 and 139<hi[2]<160): continue
        M=o.matrix_world; N=M.to_3x3().inverted().transposed(); got=0
        for p in o.data.polygons:
            n=(N@p.normal).normalized()
            if n.z<0.97: continue
            vs=[M@o.data.vertices[i].co for i in p.vertices]
            zt=max(v.z for v in vs)
            if zt<hi[2]-0.08 or zt<139: continue
            P=sum((vs[i]-vs[i-1]).length for i in range(len(vs))); A=p.area*abs(M.to_3x3().determinant())**(2/3)
            if P<=0 or 2*A/P>W/2: continue
            nv=[bm.verts.new((v.x,v.y,v.z+0.004)) for v in vs]
            try: bm.faces.new(nv); got+=1
            except ValueError: pass
        if got: nobj+=1; nf+=got
    # lidless room shells (zero-thickness boxes, lids removed by nt for cutaway cams): a 12 cm dark rim along the top edge so they read as cut walls
    nsh=0
    for o in list(bpy.data.objects):
        if o.type=='MESH' and not o.hide_render and 'room shell' in o.name and len(o.data.vertices)==8:
            M=o.matrix_world; ws=[M@v.co for v in o.data.vertices]; zt=max(v.z for v in ws)
            top=[v for v in ws if abs(v.z-zt)<1e-3]
            if len(top)!=4: continue
            c=sum(top,mathutils.Vector())/4; top.sort(key=lambda v: mathutils.Vector((v.x-c.x,v.y-c.y)).to_2d().angle_signed(mathutils.Vector((1,0)))) 
            T=float(os.environ.get('RIM','0.12')); inn=[]
            for v in top:
                d=mathutils.Vector((c.x-v.x,c.y-v.y,0)); dx=T*(1 if d.x>0 else -1); dy=T*(1 if d.y>0 else -1)
                inn.append(mathutils.Vector((v.x+dx,v.y+dy,zt)))
            ov=[bm.verts.new((v.x,v.y,zt+0.004)) for v in top]; iv=[bm.verts.new((v.x,v.y,zt+0.004)) for v in inn]
            for k in range(4):
                try: bm.faces.new((ov[k],ov[(k+1)%4],iv[(k+1)%4],iv[k]))
                except ValueError: pass
            nsh+=1
    print('NU shell rims',nsh)
    me=bpy.data.meshes.new('NU_poche_render_only'); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    po=bpy.data.objects.new('NU section poche caps (render only)',me); bpy.context.scene.collection.objects.link(po)
    po.visible_shadow=False; _nu.append(po)
    print('NU poche objects',nobj,'faces',nf)
exec(open('scripts/nt/nt_render.py').read())
for o in _nu: bpy.data.objects.remove(o)
