"""Session va: constrain Freeman Hall north lettering to its solid supporting panel.

Only the UV Freeman sign FONT object is transformed/resized. No facade geometry
is edited. REVERT=1 restores the exact saved font transform and size; SAVE=1 saves.
"""
import bpy, json, os
from mathutils import Vector
D='/workspace/nj-scenes/montclair-state'
DATA=D+'/data/va'
os.makedirs(DATA,exist_ok=True)
sign=next(o for o in bpy.data.objects if o.type=='FONT' and o.data.body=='GRACE H. FREEMAN HALL')
if os.environ.get('REVERT')=='1':
    saved=json.load(open(DATA+'/lettering_pre_va.json'))
    sign.data.size=saved['size']
    rows=saved['matrix']
    from mathutils import Matrix
    sign.matrix_world=Matrix(rows)
    for r in range(4):
        for c in range(4):
            sign.matrix_world[r][c]=rows[r][c]
    sign.update_tag(refresh={'OBJECT'})
    bpy.context.view_layer.update()
    sign['va_fixed']=0
    print('VA REVERT: restored original font size and world transform')
else:
    if not sign.get('va_fixed'):
        saved={'size':sign.data.size,'matrix':[list(r) for r in sign.matrix_world],
               'name':sign.name,'body':sign.data.body}
        json.dump(saved,open(DATA+'/lettering_pre_va.json','w'),indent=2)
    frame=json.load(open(D+'/data/uv/freeman_osm_probe.json'))
    edge=next(e for e in frame['edges'] if e['i']==6)
    A=Vector((*edge['a'],0)); U=Vector((*edge['u'],0)); N=Vector((*edge['n'],0))
    wing=bpy.data.objects['UV_Freeman_N_lettering_brick_wing_UNVERIFIED']
    # These are exact 16-vertex oriented boxes: derive each panel's lateral
    # support range from its vertices, excluding its projecting mounting plate.
    verts=[wing.matrix_world@v.co for v in wing.data.vertices]
    wall_ts=[(p-A).dot(U) for p in verts if abs((p-A).dot(N)-0.18)<0.15]
    support_l=min(wall_ts); support_r=max(wall_ts)
    margin=0.12
    allowed=(support_r-support_l)-2*margin
    def span():
        bpy.context.view_layer.update()
        evaluated=sign.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh=evaluated.to_mesh()
        ps=[sign.matrix_world @ v.co for v in mesh.vertices]
        evaluated.to_mesh_clear()
        return [min((p-A).dot(U) for p in ps),max((p-A).dot(U) for p in ps)]
    before=span()
    factor=allowed/(before[1]-before[0])
    sign.data.size*=factor*0.99
    sign.location=A+U*((support_l+support_r)/2)+N*0.38+Vector((0,0,sign.location.z))
    preliminary=span()
    target_mid=(support_l+support_r)/2
    sign.location+=U*(target_mid-(preliminary[0]+preliminary[1])/2)
    bpy.context.view_layer.update()
    after=span()
    sign['va_fixed']=1
    sign['va_note']='Centre-fit within solid north lettering wall; 0.12 m lateral end margins; 0.04 m stand-off from backing plate.'
    report={'body':sign.data.body,'before_t':before,'after_t':after,
            'support_t':[support_l,support_r],'end_margin_m':margin,
            'sign_width_m':after[1]-after[0],'scale_factor':factor,
            'backing_outward_n_m':0.34,'sign_origin_outward_n_m':0.38,
            'sign_extrude_m':sign.data.extrude,'facade_geometry_changed':False,
            'objects':len(bpy.data.objects),'materials':len(bpy.data.materials),'status':'PASS'}
    assert after[0]>=support_l and after[1]<=support_r
    assert after[0]>=support_l+margin-0.001
    assert after[1]<=support_r-margin+0.001
    assert report['sign_width_m']<=allowed+0.0001
    json.dump(report,open(DATA+'/va_fix_report.json','w'),indent=2)
    print('VA_FIX',json.dumps(report,indent=2))
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile()
    print('VA SAVED',bpy.data.filepath)
