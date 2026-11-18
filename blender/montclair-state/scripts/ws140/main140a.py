import bpy, os
SAVE=os.environ.get('SAVE','0')=='1'
OB=bpy.data.objects
LAWN=bpy.data.materials['COLE_lawn_post2020_bs']
# regions (x0,x1,y0,y1): A = lawn W of / N of the Russ S lot W end + strip S; B = strip between Skyline W walk and BK E wall (S of the pale L pad)
REG={'A':(-195,-150,-305,-248),'A2':(-150,-88,-305,-276),'B':(-90,-73.2,-252,-216.5)}
def isortho(m):
    if m is None: return False
    n=m.name.lower()
    return ('ortho' in n) and not any(k in n for k in ('asphalt','walk','curb','paint','road','concrete','brick','roof'))
cands=[o for o in OB if o.type=='MESH' and (o.name.startswith(('Terrain_LiDAR_DTM_1m','WS110_ground_patch','WS133b_','WS134_ground','WS113_terrain_fan_fill','WS138b','WS138c','WS139')) ) and 'tree' not in o.name.lower()]
tot={}
for o in cands:
    me=o.data; mw=o.matrix_world; mats=list(me.materials)
    if not any(isortho(m) for m in mats): continue
    li=None
    for i,m in enumerate(mats):
        if m==LAWN: li=i
    hit=[]
    for p in me.polygons:
        m=mats[p.material_index] if p.material_index<len(mats) else None
        if not isortho(m): continue
        c=mw@p.center
        for k,(x0,x1,y0,y1) in REG.items():
            if x0<c.x<x1 and y0<c.y<y1: hit.append((p,k,m.name)); break
    if not hit: continue
    if li is None: me.materials.append(LAWN); li=len(me.materials)-1
    for p,k,mn in hit:
        p.material_index=li; tot[(o.name[:40],mn,k)]=tot.get((o.name[:40],mn,k),0)+1
    me.update()
for k,v in tot.items(): print('RETEX',k,v)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
