import numpy

# Number	Binary value	Dark (RGB)  Bright (RGB)    name
# 0	        000	            #000000	    #000000	        black
# 1	        001	            #0000D7	    #0000FF         blue
# 2	        010	            #D70000	    #FF0000	        red
# 3	        011	            #D700D7	    #FF00FF	        magenta
# 4	        100	            #00D700	    #00FF00     	green
# 5	        101	            #00D7D7	    #00FFFF	        cyan
# 6	        110	            #D7D700	    #FFFF00	        yellow
# 7	        111	            #D7D7D7	    #FFFFFF	        white

ZX_PALETTE =    [[0x00, 0x00, 0x00], [0x00, 0x00, 0xD7], [0xD7, 0x00, 0x00], [0xD7, 0x00, 0xD7], 
                 [0x00, 0xD7, 0x00], [0x00, 0xD7, 0xD7], [0xD7, 0xD7, 0x00], [0xD7, 0xD7, 0xD7],
                 [0x00, 0x00, 0x00], [0x00, 0x00, 0xFF], [0xFF, 0x00, 0x00], [0xFF, 0x00, 0xFF], 
                 [0x00, 0xFF, 0x00], [0x00, 0xFF, 0xFF], [0xFF, 0xFF, 0x00], [0xFF, 0xFF, 0xFF]]

ZX_PALETTE_NAMES = ["BLACK", "BLUE", "RED", "MAGENTA", 
                    "GREEN", "CYAN", "YELLOW", "WHITE",
                    "LIGHT BLACK", "LIGHT BLUE", "LIGHT RED", "LIGHT MAGENTA", 
                    "LIGHT GREEN", "LIGHT CYAN", "LIGHT YELLOW", "LIGHT WHITE"]

def getPaletteColor(rgbValues):
    nearestColor = 0
    minDistance = float('inf')
    colorIdx = 0
    for c in ZX_PALETTE:
        dist = numpy.linalg.norm(c - rgbValues)
        if dist < minDistance:
            minDistance = dist
            nearestColor = colorIdx
        colorIdx = colorIdx + 1

    return nearestColor

def getColorDescription(col):
    return "{} ({})".format(col, ZX_PALETTE_NAMES[col])