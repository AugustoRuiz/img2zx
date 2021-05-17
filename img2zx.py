import sys, getopt
import os.path
from cv2 import cv2
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

def printHelp():
    print ("img2zx.py -i <image file> -p <paper values file> -w <tile width> -h <tile height> [-o <output> -n <tile label name> -c -x]")
    print ("")
    print ("Mandatory args:")
    print (" -i <image file>:           Path to image with tileset.")
    print (" -p <paper values file>:    Path to file that contains the paper color for each character.")
    print (" -w <tile width>:           Tile width (in characters).")
    print (" -h <tile height>:          Tile height (in characters).")
    print ("")
    print ("Optional args:")
    print (" -o <output>:               Path to output assembly.")
    print (" -n <name>:                 Tile label name. Default value is 'tile'.")
    print (" -c:                        Export pixel data by characters. If specified, pixel data are extracted by char. Otherwise, pixel data is extracted traversing all tile width.")
    print (" -x:                        Include a byte indicating the tile idx. (for Sejuan ;) ).")
    print ("")
    print ("Note on file paths: If there are spaces in the path, use double quotes or scape spaces.")
    print ("")
    print ("The paper values file is a text file with the paper color that is used in each character. Characters are read left to right, then up to down, for the full image.")
    print ("You can specify the character ink with the paper value. The format used is: ")
    print ("    Bits 0-3: Paper value")
    print ("    Bits 4-7: Ink value")
    print ("This is most useful for empty tiles (where no ink pixels are found, and the tool will always specify black as the ink if not specified.")
    print ("")
    print ("Enjoy!")

def validateArguments(argv):
    result = {}
    try:
        options = getopt.getopt(argv, "?i:o:p:w:h:n:cx", ["help","ifile=","ofile=","paperfile=","width=","height=","bychar","tileidx","tilename="])
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)

    result["ofile"] = "tiles.asm"
    result["bychar"] = False
    result["tileIdx"] = False
    result["tilename"] = "tile"
    for arg, val in options[0]:
        if arg in ("-?", "--help"):
            printHelp()
            sys.exit()
        elif arg in ("-i", "--ifile"):
            result["ifile"] = val
        elif arg in ("-o", "--ofile"):
            result["ofile"] = val
        elif arg in ("-p", "--pfile"):
            result["pfile"] = val
        elif arg in ("-w", "--width"):
            result["tileWidth"] = val
        elif arg in ("-h", "--height"):
            result["tileHeight"] = val
        elif arg in ("-c", "--bychar"):
            result["bychar"] = True
        elif arg in ("-x", "--tileidx"):
            result["tileIdx"] = True
        elif arg in ("-n", "--tilename"):
            result["tileName"] = val
        else:
            print ("Unrecognized argument '{}' with value '{}'".format(arg, val))

    if not ("ifile" in result and "ofile" in result and "pfile" in result and "tileWidth" in result and "tileHeight" in result):
        errMsg = "ERROR: Missing argument(s):"
        for arg in ["ifile", "ofile", "pFile", "tileWidth", "tileHeight"]:
            if not arg in result:
                errMsg = "{} {},".format(errMsg, arg)
        print(errMsg[:-1])

        printHelp()
        sys.exit(2)

    return result

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

def getTiles(inFile, tileWidth, tileHeight):
    if not os.path.isfile(inFile):
        print("File '{}' does not exist. Exiting.".format(inFile))
        sys.exit(2)
    img = cv2.imread(inFile)
    rgbImg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    imgHeight = rgbImg.shape[0]
    imgWidth = rgbImg.shape[1]

    tiles = []

    palettizedArray = numpy.full((imgHeight, imgWidth), 0)

    for y in range(imgHeight):
        for x in range(imgWidth):
            palettizedArray[y][x] = getPaletteColor(rgbImg[y,x])

    for y in range(0, imgHeight, tileHeight):
        tiles.append([])
        for x in range(0, imgWidth, tileWidth):
            tiles[len(tiles) - 1].append(palettizedArray[y:y+tileHeight, x:x+tileWidth])

    return tiles

def getPaperValues(pFile):
    with open(pFile) as f:
        result = numpy.array([[int(x) for x in line.split()] for line in f])
    return result

def getColorDescription(col):
    return "{} ({})".format(col, ZX_PALETTE_NAMES[col])

def parseTile(tile, paperValues, byChar):
    result = ";; Pixel data"
    inkColors = numpy.full(paperValues.shape, -1)
    tileHeight = tile.shape[0]
    tileWidth = tile.shape[1]
    pValues = numpy.copy(paperValues)

    for py in range(paperValues.shape[0]):
        for px in range(paperValues.shape[1]):
            if(pValues[py,px] & 0b11110000) != 0:
                inkColors[py,px] = (paperValues[py,px] & 0b11110000) >> 4
                pValues[py,px] = paperValues[py,px] & 0b001111

    if byChar:
        cy = 0
        for y in range(0, tileHeight, 8):
            cx = 0
            for x in range(0, tileWidth, 8):
                result = "{}\n;; Char {},{}\nDEFB ".format(result, cx, cy)

                for offsetY in range(8):
                    byteValue = 0
                    for offsetX in range(8):
                        byteValue = byteValue << 1
                        pixColor = tile[y+offsetY,x+offsetX]
                        if(pixColor != pValues[cy,cx]):
                            byteValue = byteValue | 1
                            if inkColors[cy,cx] == -1:
                                inkColors[cy,cx] = pixColor
                            else:
                                if inkColors[cy,cx] != pixColor:
                                    print("WARNING: At pixel ({},{}): Found color {} in character\n         with paper {} and ink {}.".format(x+offsetX, y+offsetY, getColorDescription(pixColor), getColorDescription(pValues[cy,cx]), getColorDescription(inkColors[cy,cx])))

                    result = "{} {},".format(result, byteValue)
                cx = cx + 1
                result = result[:-1]
            cy = cy + 1
    else:
        for y in range(tileHeight):
            result = "{}\nDEFB ".format(result)
            cx = 0
            cy = int(y/8)
            for x in range(0, tileWidth, 8):
                byteValue = 0
                for offsetX in range(8):
                    byteValue = byteValue << 1
                    pixColor = tile[y,x+offsetX]
                    if(pixColor != pValues[cy,cx]):
                        byteValue = byteValue | 1
                        if inkColors[cy,cx] == -1:
                            inkColors[cy,cx] = pixColor
                        else:
                            if inkColors[cy,cx] != pixColor:
                                print("WARNING: At pixel ({},{}): Found color {} in character\n         with paper {} and ink {}.".format(x+offsetX, y, getColorDescription(pixColor), getColorDescription(pValues[cy,cx]), getColorDescription(inkColors[cy,cx])))
                result = "{} {},".format(result, byteValue)
                cx = cx + 1
            result = result[:-1]

    result = "{}\n;; Attribute data".format(result)
    result = "{}\nDEFB ".format(result)
    for cy in range(inkColors.shape[0]):
        for cx in range(inkColors.shape[1]):
            if(inkColors[cy,cx] == -1):
                inkColors[cy,cx] = 0
            brightness = int(pValues[cy,cx] > 7 or inkColors[cy,cx] > 7)
            attrValue = (inkColors[cy,cx] & 0x7) | ((pValues[cy,cx] & 0x7) << 3) | brightness << 6
            result = "{} {},".format(result, attrValue)
    result = "{}\n".format(result[:-1])

    return result

def writeAsmHeader(ofile, argVals):
    ofile.write(";; img2zx, a python script created by AugustoRuiz, from Retroworks, in 2020.\n")
    ofile.write(";; Feel free to use it anyway you want. If it was useful to you, it would be nice to know :)\n")
    ofile.write(";; Data generated from file '{}'.\n".format(argVals["ifile"]))
    ofile.write(";; Tile Size=({},{}).\n".format(argVals["tileWidth"], argVals["tileHeight"]))
    ofile.write(";; Paper values file '{}'.\n".format(argVals["pfile"]))

def main(argv):
    argVals = validateArguments(argv)

    th = int(argVals["tileHeight"])
    tw = int(argVals["tileWidth"])

    tiles = getTiles(argVals["ifile"], tw, th)
    paperValues = getPaperValues(argVals["pfile"])

    xChars = int(tw / 8)
    yChars = int(th / 8)

    tileIdx = 0
    with open(argVals["ofile"], "w") as ofile:
        writeAsmHeader(ofile, argVals)
        for tileY in range(len(tiles)):
            for tileX in range(len(tiles[tileY])):
                ofile.write("\n;; Tile ({},{})\n".format(tileX, tileY))
                ofile.write("{}_{}:\n".format(argVals["tilename"], tileIdx))
                if argVals["tileIdx"]:
                    ofile.write("DEFB {}\n".format(tileIdx))
                print("Parsing tile ({},{})".format(tileX, tileY))
                asm = parseTile(tiles[tileY][tileX], paperValues[tileY*yChars:(tileY+1)*yChars, tileX*xChars:(tileX+1)*xChars], argVals["bychar"])
                ofile.write(asm)
                tileIdx = tileIdx + 1
    print("Done!")

if __name__ == "__main__":
   main(sys.argv[1:])
