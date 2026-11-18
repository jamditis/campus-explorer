# ws125d: groundcover pads read as flat discs -> low rounded spreading mounds (dwarf-shrub carpet), ~0.3-0.45 m tall, still overlapping.
import bpy, random
random.seed(1250)
n=0
for o in bpy.data.objects:
    if o.name.startswith('WS125_bed_groundcover_'):
        zb=o.location.z+ (-0.03 and 0)  # keep base roughly: recompute from old scale
        oz=o.scale.z; s=random.uniform(0.75,1.05); newz=s*0.42
        # base height under object = location.z + gz*oz ; gz = -0.04 for boxwood core, so shift by delta
        o.location.z += -0.04*(oz-newz)
        o.scale=(s,s*random.uniform(0.9,1.1),newz); n+=1
print('M125d groundcover reshaped',n)
bpy.ops.wm.save_mainfile(); print('M125d SAVED')
