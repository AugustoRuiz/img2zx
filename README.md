# img2zxbasic

Simple script to convert raster images (bmp, png, gif...) into basic file for [Boriel's ZX Basic](https://zxbasic.readthedocs.io/en/docs/) and [GuSprites](https://github.com/gusmanb/GuSprites) sprite library

Project based on [img2zx](https://github.com/AugustoRuiz/img2zx) de [Augusto Ruiz](https://github.com/AugustoRuiz), and just adapted its output.

### Requeriments
python 3.7.7 nor higher

```bash
pip install -r requeriments.txt
```

### Run

#### Python locally
Put in paperValues.txt paper value for each tile

```bash
python img2zx.py -i tiles.png -p paperValues.txt -o tiles.bas 
```
#### Docker
```bash
docker run -it -u $(id -u):$(id -g) -v ${PWD}:/share rtorralba/img2zxbasic -i /share/tiles.png -p /share/paperValues.txt -o /share/tiles.bas
```
