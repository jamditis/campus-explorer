# pi (session pi, Nov 1 2026). ALL UNVERIFIED. REVERT=1 undoes everything.
# (A) Feliciano LiDAR roof: every sloped face (0.15<|nz|<0.95) -> new slot PI_Feliciano_roof_tile_forced_UNVERIFIED
#     (copy of shared Roof_tile_or_membrane with membrane/side-colour switches Mix.008/Mix.009 forced to tile) -> no white hip shards.
#     Vertical faces still on Wall_stucco_mission (LiDAR step walls) -> pg plain-stucco copy (no grey shader windows).
# (B) Feliciano walls: vertical faces of the west re-entrant beside the entrance bay (x -220..-209.5, y 165..176)
#     -> pg plain-stucco copy (their shader windows read as grey glass slivers above the pavilion gable).
import bpy,os,sys,json
REV=os.environ.get('REVERT')=='1'
PL='PG_Feliciano_wall_stucco_plain_no_shader_windows_UNVERIFIED'; TN='PI_Feliciano_roof_tile_forced_UNVERIFIED'
def undo(o,names):
    if 'pi_prev_mi' in o:
        for i,mi in json.loads(o['pi_prev_mi']): o.data.polygons[i].material_index=mi
        del o['pi_prev_mi']
    for k in reversed([k for k,s in enumerate(o.material_slots) if s.material and s.material.name in names and k>=o.get('pi_nslots',99)]):
        o.data.materials.pop(index=k)
    for p in ('pi_nslots','UNVERIFIED_pi'):
        if p in o: del o[p]
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']; w=bpy.data.objects['Feliciano School of Business walls']
undo(r,(PL,TN)); undo(w,(PL,))
if TN in bpy.data.materials and bpy.data.materials[TN].users==0: bpy.data.materials.remove(bpy.data.materials[TN])
if not REV:
    t=bpy.data.materials['Roof_tile_or_membrane'].copy(); t.name=TN; nt=t.node_tree
    for nm in ('Mix.008','Mix.009'):
        n=nt.nodes[nm]
        for l in list(nt.links):
            if l.to_node==n and l.to_socket.name=='Factor': nt.links.remove(l)
        n.inputs['Factor'].default_value=0.0
    R=r.matrix_world.to_3x3(); r['pi_nslots']=len(r.material_slots)
    r.data.materials.append(t); ts=len(r.data.materials)-1; r.data.materials.append(bpy.data.materials[PL]); ps=len(r.data.materials)-1
    prev=[];a=b=0
    for p in r.data.polygons:
        nz=abs((R@p.normal).normalized().z)
        if 0.15<nz<0.95 and p.material_index in (0,3): prev.append((p.index,p.material_index)); p.material_index=ts; a+=1
        elif nz<=0.15 and p.material_index==3: prev.append((p.index,3)); p.material_index=ps; b+=1
    r['pi_prev_mi']=json.dumps(prev); r['UNVERIFIED_pi']='sloped LiDAR roof faces forced to tile; step walls plain stucco'
    mw=w.matrix_world; R=mw.to_3x3(); slot=[k for k,s in enumerate(w.material_slots) if s.material and s.material.name==PL][0]
    prev=[]
    for p in w.data.polygons:
        c=mw@p.center
        if abs((R@p.normal).z)<0.3 and -220<c.x<-209.5 and 165<c.y<176 and w.material_slots[p.material_index].material.name=='Wall_stucco_mission':
            prev.append((p.index,p.material_index)); p.material_index=slot
    w['pi_prev_mi']=json.dumps(prev); w['UNVERIFIED_pi']='re-entrant beside entrance bay plain stucco'
    print('PI_FIX roof tile',a,'roof plain',b,'walls',[x[0] for x in prev])
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
print('PI_DONE',REV,len(bpy.data.objects))
