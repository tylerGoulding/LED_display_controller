from PIL import Image
from psd_tools import PSDImage
import numpy as np
import sys, os
import argparse


class _ledArray():
    """Base Class for a single LED data stream."""
    def __init__(self,layer,color_mode='BW'):
        self.psd_layer = layer;
        self.name = layer.name;
        self.numLEDS = len(layer.layers);
        self.outputCount = [0 for i in xrange(self.numLEDS)];
        #self.outputFile = outputFile
        if color_mode == 'RGB':
            self.outputArray =[ [-1,-1,-1] for i in xrange(self.numLEDS)]
        else:
            self.outputArray = [-1 for i in xrange(self.numLEDS)]
    def generateOutput(self):
        outputString = "const uint8_t " + self.name + "_" + "[] =  {"
        outputArray = [outputString]
        for byte in self.outputArray:
            outputArray.append(str(byte));
            outputArray.append(", ");
        del outputArray[-1]
        outputArray.append("}");
        outputString = ''.join([a for a in outputArray])
        print outputString
    def updateAverage(self,index,value):
        count = self.outputCount[index] = self.outputCount[index] + 1;
        oldMean = self.outputArray[index]
        self.outputArray[index] = oldMean + (value-oldMean)/count


def parser_init():
    parser = argparse.ArgumentParser(
            description = 'arguments to output LED array');
    parser.add_argument("-m", "--mask",nargs=1,required=True,  help="Photoshop file of the LED positions.")
    parser.add_argument("-e", "--effect",nargs=1,required=True, help="Photo of the effect to overlay on to the LEDS. This should be the same pixel size as the mask!")
    parser.add_argument("-o", "--output",nargs=1,  type=argparse.FileType('w'), default=sys.stdout, help="Photoshop file of the LED positions.")
    return parser;
def main():
    parser = parser_init();
    #parser_init()
    args = parser.parse_args()
    #mask = args.mask
    #overlay = args.overlay
    mask = args.mask[0]

    overlay = Image.open(args.effect[0])
    
    overlay = overlay.convert("LA");

    maskPSD = PSDImage.load(mask)
    maskPIL = maskPSD.as_PIL();
    maskPIL = maskPIL.convert("1");

    maskMeta = maskPSD.header
    # check if the dimesions of the mask and the overlay are the same
    if ((maskMeta.width != overlay.width) and (maskMeta.height != overlay.height)):
        raise("incorrect Size");
    print maskPSD.layers


    maskLayers = [ _ledArray(layer,) for layer in maskPSD.layers ]
    if (1):
        print "Found " + str(len(maskLayers)) + " LED data lines"
        print "These are the following layers:"
        for layer in maskLayers:
            print "   " + layer.name

    for ledArray in maskLayers:
        numLEDS = ledArray.numLEDS;
        for i,led in enumerate(ledArray.psd_layer.layers):
            # since layers loaded most to least recent, first led is the last in the led stream
            index = numLEDS - i-1;
            print index
            x1,y1,x2,y2 = led.bbox;
            # print "(",x1,y1,x2,y2,")"
            # loop through bounding box and look for average value
            # bbox doesnt return a tranformed bbox so we need to check if
            # the pixel in the box is also part of the "led"
            for x in xrange(x1,x2):
                for y in xrange(y1,y2):
                    pixel = maskPIL.getpixel((x,y))
                    if (pixel == 0):
                        # we have found a pixel, calculate average value
                        intensity = overlay.getpixel((x,y))
                        # print intensity[0]
                        ledArray.updateAverage(index,intensity[0]);
        ledArray.generateOutput()
    # for 


if __name__ == '__main__':
    main()