import sys, getopt
import os.path
import cv2
import numpy

import zxlib

def printHelp():
    print ("img2zx.py -i <image file> -p <paper values file> -w <tile width> -h <tile height> [-o <output> -n <tile label name> -c -x]")
    print ("")
    print ("Mandatory args:")
    print (" -i <image file>:           Path to image with tileset or spriteset.")
    print (" -p <paper values file>:    Path to file that contains the paper color for each character.")
    print (" -w <tile width>:           Tile width (in characters).")
    print (" -h <tile height>:          Tile height (in characters).")
    print ("")
    print ("Optional args:")
    print (" -o <output>:               Path to output assembly.")
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
        options = getopt.getopt(argv, "?i:o:p:t:", ["help","ifile=","ofile=","paperfile=","itype="])
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)

    result["ofile"] = "file.bas"
    result["tileWidth"] = 8
    result["tileHeight"] = 8
    result["type"] = "tiles" # tiles or sprites

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
        elif arg in ("-t", "--itype"):
            result["type"] = val
        else:
            print ("Unrecognized argument '{}' with value '{}'".format(arg, val))
    
    if result['type'] == 'sprites':
        result['tileWidth'] = 16
        result['tileHeight'] = 16

    if not ("ifile" in result and "ofile" in result and "pfile" in result and "tileWidth" in result and "tileHeight" in result):
        errMsg = "ERROR: Missing argument(s):"
        for arg in ["ifile", "ofile", "pFile", "tileWidth", "tileHeight"]:
            if not arg in result:
                errMsg = "{} {},".format(errMsg, arg)
        print(errMsg[:-1])

        printHelp()
        sys.exit(2)

    return result

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
            palettizedArray[y][x] = zxlib.getPaletteColor(rgbImg[y,x])

    for y in range(0, imgHeight, tileHeight):
        tiles.append([])
        for x in range(0, imgWidth, tileWidth):
            tiles[len(tiles) - 1].append(palettizedArray[y:y+tileHeight, x:x+tileWidth])

    return tiles

def getPaperValues(pFile):
    with open(pFile) as f:
        result = numpy.array([[int(x) for x in line.split()] for line in f])
    return result