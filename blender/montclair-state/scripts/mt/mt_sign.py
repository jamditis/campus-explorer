# Session mt (Oct 29 2026): CCOM tower sign per MontclairCCOM FB post Oct 27 2026 (5 photos, all of the WEST/entrance face).
import bpy, math
from mathutils import Vector
A=Vector((-18.303,24.988)); B=Vector((-20.0,18.3))
t=(B-A).normalized()                      # along face (N->S)
n=Vector((-0.969,0.246)).normalized()     # outward normal
C=(A+B)/2; FACEW=(B-A).length
font=bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', check_existing=True)
font.pack()
L1=bpy.data.objects['CCOM tower 4a lettering COLLEGE OF']
L2=bpy.data.objects['CCOM tower 4a lettering COMMUNICATION AND MEDIA']
TARGET_W=0.58*FACEW   # line 2 width ~0.51-0.60 of face width in photos 1 and 3 (t2)
for o in (L1,L2):
    o.data.font=font; o.data.extrude=0.010; o.data.align_x='CENTER'; o.data.align_y='CENTER'; o.data.space_character=1.0
    o.data.size=0.3
bpy.context.view_layer.update()
w=L2.dimensions.x; s=0.3*TARGET_W/w
for o in (L1,L2): o.data.size=s
bpy.context.view_layer.update()
cap=L2.dimensions.y
ZC=147.45   # t2: band underside 151.0, arched-window frame top 144.92; photos put it ~0.55-0.6 down from the band
gap=cap*1.7
off=0.012   # letter back face just proud of the stucco
xy=C+n*off
L1.location=(xy.x,xy.y,ZC+gap/2); L2.location=(xy.x,xy.y,ZC-gap/2)
for o in (L1,L2):
    o.visible_shadow=True
    o['source']='MontclairCCOM Facebook post Oct 27 2026 (refs/web/20261029/ccom_fb_post_20261027_sign_grid.png); session mt'
    o['status']='text+face+colour from photos; size/height/font (Liberation Sans Bold ~ Helvetica) UNVERIFIED'
print('SIGN face_w',round(FACEW,3),'size',round(s,4),'w2',round(L2.dimensions.x,3),'w1',round(L1.dimensions.x,3),'cap',round(cap,3),'z1',round(L1.location.z,3),'z2',round(L2.location.z,3))
print('COUNT',len(bpy.data.objects))
bpy.ops.wm.save_mainfile()
print('SAVED')
