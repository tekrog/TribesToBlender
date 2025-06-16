# You will have to pip install opencv-python and numpy
import volumer
import terrain
import dml as tribes_dml
import cv2 as cv
import numpy as np
import palette
import dts
import tribesfont

if __name__ == '__main__':
    ter = terrain.terrain()
    ter.load_file("example_files\\Snowblind.ted")
    ter.print_stats()
    print(ter.get_true_height_range())

    ter = terrain.terrain()
    ter.load_file("example_files\\rpgbutch5.ted")
    ter.print_stats()
    print(ter.get_true_height_range())

