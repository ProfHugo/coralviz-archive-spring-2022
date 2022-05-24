import numpy as np
import cv2
import os
import pathlib
import math

# note that OpenCV reads/writes in BGR
pixel_map = {
    b'\x00\x00\x00': 2, # Shadow
    b'\xff\x00\xff': 1, # CCA
    b'\x00\xff\x00': 0 # Unclassed
}

black = np.array([0, 0, 0])
pink = np.array([255, 0, 255])
green = np.array([0, 255, 0])

rev_pixel_map = {
    0: black, # Shadow
    1: pink, # CCA
    2: green # Unclassed
}

# Inferred the class of a pixel that is not exactly of a recognized color
def getClosestClass(pixel, pixel_map):
    min_distance = 442.0
    to_return = b'\x00\x00\x00'
    for key in pixel_map.keys():
        distance = math.sqrt((pixel[0] - key[0]) ** 2 + (pixel[1] - key[1]) ** 2 + (pixel[2] - key[2]) ** 2)
        if (distance <= min_distance):
            to_return = key
            min_distance = distance
    return pixel_map[to_return]

def pixel_to_class(pix, pixel_map):
    index = pix.tobytes()
    if index in pixel_map.keys():
        return pixel_map[index]
    else:
        return getClosestClass(index, pixel_map)

# Convert a RBG segmentation mask to a 2d composite segmentation class array
def imageToClassArray(raw_mask, pixel_map):
    class_array = np.empty(shape=raw_mask.shape[0:2] + (1,))
    for row in range(0, len(raw_mask)):
        for col in range(0, len(raw_mask[0])):
            class_array[row][col] = pixel_to_class(raw_mask[row][col], pixel_map)
    return class_array

# Convert a 2d segmentation class array to a RBG segmentation mask
def imageFromClassArray(class_arr, rev_pixel_map):
    image = np.empty(shape=class_arr.shape[0:2] + (3,))
    for row in range(0, len(class_arr)):
        for col in range(0, len(class_arr[0])):
            index = class_arr[row][col][0]
            if index in rev_pixel_map.keys():
                image[row][col] = rev_pixel_map[index]
            else:
                print(f"Error: Unrecognized class id at position x = {col}, y = {row}")
                return None
    return image

def main():
    # create save directory if it does not exist
    if not os.path.isdir("out"):
        os.mkdir("out")
    for imagename in os.listdir("colormasks"):
        f = os.path.join("colormasks", imagename)
        # checking if it is a file
        if os.path.isfile(f):
            image = cv2.imread(f)
            image = imageToClassArray(image, pixel_map)
            cv2.imwrite(os.path.join("out", f"{pathlib.Path(imagename).resolve().stem}_intLabels.png"), image)

if __name__ == "__main__":
    main()