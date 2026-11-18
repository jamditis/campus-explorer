# ws203 W19 last two faint marks (S-bay close-up): ray-cast puts them on exposed WS94 slit-filler / WS81 underlay slivers at the old seam
# x~-233.3 (y -105.6 and y -99.5). Probes p203A/p203B (0.02 m, real terrain) -> residual grids r203A/r203B vs 0.4 m local median plane.
# Same designer call and tool as ws202 (fix202b.py raise-only flusher, cap 2.5 cm, covered underlay 0.3 mm under the sheet above).
import os
for g,b in (('r203A.npz','-234.4,-232.4,-106.4,-104.7'),('r203B.npz','-234.2,-232.2,-100.5,-98.7')):
    os.environ['GRID']='/workspace/nj-scenes/montclair-state/scripts/ws203/'+g; os.environ['FBOX']=b; os.environ['EB']='0.0003'
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws202/fix202b.py').read())
