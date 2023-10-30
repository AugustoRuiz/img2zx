import sys, getopt
import numpy

import zxlib
import ioUser
import zxbasic

globalTiles = []
globalAttr = []

def getValues(tile, paperValues):
    inkColors = numpy.full(paperValues.shape, -1)
    tileHeight = tile.shape[0]
    tileWidth = tile.shape[1]
    pValues = numpy.copy(paperValues)

    for py in range(paperValues.shape[0]):
        for px in range(paperValues.shape[1]):
            if(pValues[py,px] & 0b11110000) != 0:
                inkColors[py,px] = (paperValues[py,px] & 0b11110000) >> 4
                pValues[py,px] = paperValues[py,px] & 0b001111
    return inkColors,tileHeight,tileWidth,pValues

def generateCodedSprites(tile, inkColors, tileHeight, tileWidth, pValues):
    row = []
    for y in range(tileHeight):
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
                            print("WARNING: At pixel ({},{}): Found color {} in character\n         with paper {} and ink {}.".format(x+offsetX, y, zxlib.getColorDescription(pixColor), zxlib.getColorDescription(pValues[cy,cx]), zxlib.getColorDescription(inkColors[cy,cx])))
            row.append(byteValue)
            cx = cx + 1
    result = [row[0], row[2], row[4], row[6], row[8], row[10], row[12], row[14],
            row[16], row[18], row[20], row[22], row[24], row[26], row[28], row[30],
            row[1], row[3], row[5], row[7], row[9], row[11], row[13], row[15],
            row[17], row[19], row[21], row[23], row[25], row[27], row[29], row[31]]
    return result

def generateCodedTiles(tile, inkColors, tileHeight, tileWidth, pValues):
    cy = 0
    row = []
    for y in range(0, tileHeight, 8):
        cx = 0
        for x in range(0, tileWidth, 8):
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
                                print("WARNING: At pixel ({},{}): Found color {} in character\n         with paper {} and ink {}.".format(x+offsetX, y+offsetY, zxlib.getColorDescription(pixColor), zxlib.getColorDescription(pValues[cy,cx]), zxlib.getColorDescription(inkColors[cy,cx])))

                row.append(byteValue)
            cx = cx + 1
        cy = cy + 1
    
    return row

def generateCodedAttrs(inkColors, pValues):
    for cx in range(inkColors.shape[1]):
        for cy in range(inkColors.shape[0]):
            if(inkColors[cy,cx] == -1):
                inkColors[cy,cx] = 0
            brightness = int(pValues[cy,cx] > 7 or inkColors[cy,cx] > 7)
            attrValue = (inkColors[cy,cx] & 0x7) | ((pValues[cy,cx] & 0x7) << 3) | brightness << 6
    return attrValue

def main(argv):
    argVals = ioUser.validateArguments(argv)
    
    th = int(argVals["tileHeight"])
    tw = int(argVals["tileWidth"])

    tiles = ioUser.getTiles(argVals["ifile"], tw, th)
    paperValues = ioUser.getPaperValues(argVals["pfile"])
    type = argVals["type"]

    xChars = int(tw / 8)
    yChars = int(th / 8)

    codedTiles = []
    codedAttrs = []

    tileIdx = 0
    for tileY in range(len(tiles)):
        for tileX in range(len(tiles[tileY])):
            inkColors, tileHeight, tileWidth, pValues = getValues(tiles[tileY][tileX], paperValues[tileY*yChars:(tileY+1)*yChars, tileX*xChars:(tileX+1)*xChars])

            if type == "tiles":
                codedTiles.append(generateCodedTiles(tiles[tileY][tileX], inkColors, tileHeight, tileWidth, pValues))
                codedAttrs.append(generateCodedAttrs(inkColors, pValues))
            else:
                codedTiles.append(generateCodedSprites(tiles[tileY][tileX], inkColors, tileHeight, tileWidth, pValues))
            
            tileIdx = tileIdx + 1
    
    if type == "tiles":
        print(zxbasic.getTilesBas(codedTiles, codedAttrs))
    else:
        print(zxbasic.getSpritesBas(codedTiles))
    

if __name__ == "__main__":
   main(sys.argv[1:])
