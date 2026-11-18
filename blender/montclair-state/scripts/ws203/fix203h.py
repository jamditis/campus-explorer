# ws203 W13h: same lawn-lip tuck as fix203c (strip/paving contacts kept), applied to the WS192 strip-E-end fillet + WS191b gap fill —
# the E-lawn eye view (0444) shows a dark notch where their outer edge stands proud of the lawn beside the strip's E end.
src=open('/workspace/nj-scenes/montclair-state/scripts/ws203/fix203c.py').read()
src=src.replace("LS=('WS191c_Lot3_S_strip_back',)","LS=('WS192_Lot3_S_strip_E_end','WS191b_Lot3_S_gap_lawn')")
exec(src)
