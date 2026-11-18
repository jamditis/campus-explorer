import os
P187=open('/workspace/nj-scenes/montclair-state/scripts/ws188/probe188cam.py').read()
for tag,pc,pp in [('CLOSE','-321.5,-233,2.2,-311,-237.5,0.0,30','233:274 290:274 350:274 280:163 270:160'),
                  ('WEYE','-336,-231,1.7,-312,-236,1.0,26','426:467 414:432 440:480 400:450 402:270'),
                  ('EEYE','-300,-241,1.7,-326,-232,0.5,26','414:243 405:240')]:
    os.environ['PCAM']=pc; os.environ['PPIX']=pp; print('TAG',tag,flush=True); exec(P187)
