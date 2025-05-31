### Recovering from parts
I have limitation on file size on my local disk. So I splitted dump  
to bunch of 4G files before recovering. After that I modified this script to support  
splitted dump like this.
```bash
sudo dd if=/dev/sdd1 bs=1M status=progress | split -b 4G - forest.img.part.
./recovercr3.py --maxchunks=7 --input "/run/media/loki/Kingspec/Images/forest.img.pa
rt.*" --outdir /run/media/loki/Kingspec/Images/forest_sources
```
