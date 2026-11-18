#!/bin/bash
cd /workspace/nj-scenes/montclair-state/data/ts
while ! grep -q NAIP_DONE naip.log; do sleep 10; done
U='https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPPlus/ImageServer/exportImage?bbox=570958.75,679285.0,652979.5833333334,749822.9166666666&bboxSR=6527&imageSR=6527&size=2500,2150&format=jpg&compressionQuality=90&bandIds=0,1,2&interpolation=RSP_BilinearInterpolation&f=image'
for a in 1 2 3 4 5; do curl -s -m 200 -o naip_far.jpg "$U"; s=$(stat -c%s naip_far.jpg); [ $s -gt 200000 ] && break; echo retry $a $s; sleep 5; done
echo FAR_DONE $(stat -c%s naip_far.jpg)
