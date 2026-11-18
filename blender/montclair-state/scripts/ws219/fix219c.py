# ws219 W38c: WS214_WS69_N_berm_tip_curb_return_nose (a ws214 curb-return nose built before the ws215/ws217 walks) now
# stands as a grey 10-19 cm fin where the WS215 RHD SE sidewalk, the WS72 Kasser landing and the College Ave crosswalk
# meet. With the WS69 curb depressed at the crosswalk (fix219a), a curb return here has no function: both sides are
# walk at the same grade and the crosswalk landing is flush. Tuck the nose under the walks (verts clamped to adjacent
# walk/asphalt grade - 1 cm) so the paving is the single winner. Curb-piece only; no paving moved.
import bpy, json
G=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws218/w38_grid218.json'))
G={tuple(map(float,k.split(','))):v for k,v in G.items()}
OK=('WS72_K','WS215_','KY_col','WS67_C')
def ground(x,y):
    c=[v[1] for (gx,gy),v in G.items() if abs(gx-x)<=0.6 and abs(gy-y)<=0.6 and v[0].startswith(OK)]
    return min(c) if c else 125.14
o=bpy.data.objects['WS214_WS69_N_berm_tip_curb_return_nose_ortho2020_UNVERIFIED']; M=o.matrix_world; Mi=M.inverted()
n=0; mx=0
for v in o.data.vertices:
    w=M@v.co; g=ground(w.x,w.y)-0.01
    if w.z>g: mx=max(mx,w.z-g); w.z=g; v.co=Mi@w; n+=1
o.data.update()
print('F219C nose verts tucked',n,'of',len(o.data.vertices),'max drop',round(mx,3),'mods',[m.type for m in o.modifiers],flush=True)
