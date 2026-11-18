cd /workspace/nj-scenes/montclair-state
bash scripts/ws217/jobwipc.sh > scripts/ws217/jobwipc.out 2>&1
sed -i 's/ws217b promoted 4:56 PM ET/ws217c promoted 5:00 PM ET/; s/35853ff01140ac1dcdc1f19446f9c11948d73d03ff4ee28d8c94ac05087201c3/'$(cut -d" " -f1 montclair_state_ws217c.blend.sha256)'/' /workspace/nj-scenes/exports/model-20261118f/NOTES.md
bash scripts/ws217/release217f.sh > scripts/ws217/release217f.out 2>&1
