import matplotlib

matplotlib.use("Agg")

from visualisation_mosaic_1band import BoxLayoutMosaic, CustomButton
import math
import numpy as np
import sys
import os
import glob
import urllib.request
import pandas as pd
from astropy.wcs import WCS
from astropy.visualization import make_lupton_rgb
import astropy.io.fits as pyfits
from kivy.app import App
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
import matplotlib.pyplot as plt
from functools import partial
from kivy.core.window import Window
from PIL import Image
import random


class BoxLayoutMosaicColor(BoxLayoutMosaic):

    def scale_val(self, image_array):
        if len(np.shape(image_array)) == 2:
            image_array = [image_array]
        vmin = np.min([self.background_rms_image(5, image_array[i]) for i in range(len(image_array))])
        xl, yl = np.shape(image_array[0])
        box_size = 14  # in pixel
        xmin = int((xl) / 2 - (box_size / 2))
        xmax = int((xl) / 2 + (box_size / 2))
        vmax = np.max([image_array[i][xmin:xmax, xmin:xmax] for i in range(len(image_array))])
        return vmin, vmax

    def showplot_rgb(self, rimage, gimage, bimage):
        vmin, vmax = self.scale_val([rimage, gimage, bimage])
        img = np.zeros((rimage.shape[0], rimage.shape[1], 3), dtype=float)
        img[:, :, 0] = self.sqrt_sc(rimage, scale_min=vmin, scale_max=vmax)
        img[:, :, 1] = self.sqrt_sc(gimage, scale_min=vmin, scale_max=vmax)
        img[:, :, 2] = self.sqrt_sc(bimage, scale_min=vmin, scale_max=vmax)

        return img

    def sqrt_sc(self, inputArray, scale_min=None, scale_max=None):
        #
        imageData = np.array(inputArray, copy=True)

        if scale_min is None:
            scale_min = imageData.min()
        if scale_max is None:
            scale_max = imageData.max()

        imageData = imageData.clip(min=scale_min, max=scale_max)
        imageData = imageData - scale_min
        indices = np.where(imageData < 0)
        imageData[indices] = 0.00001
        imageData = np.sqrt(imageData)
        imageData = imageData / np.sqrt(scale_max - scale_min)
        return imageData

    # function that reads a multi-extension fits file and return three arrays
    def read_fits(self, i):

        file = self.pathtofile + self.listimage[i]
        # Note : memmap=False is much faster when opening/closing many small files
        with pyfits.open(file, memmap=False) as hdu_list:
            image_B = hdu_list[0].data
            image_G = hdu_list[1].data
            image_R = hdu_list[2].data

        return image_R, image_G, image_B

    # def draw_image(self,name,scale_state,defaultvalue=True,max=1,min=0):
    def draw_image(self, index, scale_state, defaultvalue=True, max=1, min=0):
        try:

            image_R, image_G, image_B = self.read_fits(index)  # modification : read fits file instead of numpy array
            image = self.showplot_rgb(image_R, image_G, image_B)
        except IndexError:
            image = np.ones((44, 44, 3)) * 0.0000001

        return image

    def prepare_png(self, number):

        start = self.counter

        for i in np.arange(start, start + number + 1):
            img = self.draw_image(i, self.scale_state)
            image = Image.fromarray(np.uint8(img * 255), 'RGB')
            image = image.resize((150, 150), Image.ANTIALIAS)
            image.save(self.pathtoscratch + str(i + 1) + self.scale_state +self.colormap+ str(start) + '.png', 'PNG')

            self.counter = self.counter + 1

    def build(self):
        self.pathds9 = 'C:\\SAOImageDS9\\ds9.exe'

        self.pathtofile = './files_to_visualize/'

        self.pathtoscratch = './scratch_png/'
        self.pathtoscratch_numpy = './scratch_numpy_array/'
        self.path_background = 'green.png'

        self.listimage = sorted([os.path.basename(x) for x in glob.glob(self.pathtofile + '*.fits')])

        if len(sys.argv) > 1:
            self.random_seed = sys.argv[1]
        else:
            print("Random seed set to default value 42")
            self.random_seed = 42
        if len(sys.argv) > 2:
            self.fraction = float(sys.argv[2])
        else:
            print("No repeated objects")
            self.fraction = 0


        self.repeat_random_objects(self.fraction)
        random.Random(self.random_seed).shuffle(self.listimage)

        self.clean_scratch(self.pathtoscratch)

        self.start_image_number = 0
        self.counter = 0
        self.scale_min = 0
        self.scale_max = 1
        self.limit_max = 1
        self.limit_min = 0
        self.step = (self.scale_max - self.scale_min) / 10.
        self.scale_state = 'linear'
        self.number_per_frame = 100
        self.total_n_frame = int(len(self.listimage) / 100.)
        self.forward_backward_state = 0
        self.dataframe = self.create_df()
        self.colormap = 'gray'

        self.prepare_png(self.number_per_frame)
        allbox = BoxLayout(orientation='vertical')
        buttonbox = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        superbox = GridLayout(cols=10, size_hint_y=0.9)
        self.list_of_buttons = []
        for i in np.arange(self.number_per_frame):
            try:
                if self.dataframe['classification'][i] == 0:
                    self.list_of_buttons.append(
                        CustomButton(0, source=self.pathtoscratch + str(i + 1) + self.scale_state+ self.colormap+ str(
                            0) + '.png'))
                else:
                    self.list_of_buttons.append(
                        CustomButton(1, source=self.path_background))
                self.dataframe['Grid_pos'].iloc[100 * self.forward_backward_state + i] = i + 1
            except KeyError:
                self.list_of_buttons.append(CustomButton(1, source=self.pathtoscratch + str(
                    i + 1) + self.scale_state + self.colormap+str(0) + '.png'))

            self.list_of_buttons[i].bind(on_press=partial(self.on_click, i))
        for button in self.list_of_buttons:
            superbox.add_widget(button)

        allbox.add_widget(superbox)

        buttonscale1 = Button(text="Linear")
        buttonscale2 = Button(text="Sqrt")
        buttonscale3 = Button(text="Log")
        buttonscale4 = Button(text="Asinh")
        buttonscale1.bind(on_press=partial(self.change_scale, 'linear'))
        buttonscale2.bind(on_press=partial(self.change_scale, 'sqrt'))
        buttonscale3.bind(on_press=partial(self.change_scale, 'log'))
        buttonscale4.bind(on_press=partial(self.change_scale, 'asinh'))

        bforward = Button(text=" --> ")
        bbackward = Button(text=" <-- ")
        bforward.bind(on_press=self.forward)
        bbackward.bind(on_press=self.backward)

        self.textnumber = TextInput(text=str(self.forward_backward_state), multiline=False, font_size=25)
        self.textnumber.bind(on_text_validate=self.change_number)
        tnumber = Label(text=str(' / ' + str(self.total_n_frame)), font_size=25)

        buttonbox.add_widget(buttonscale1)
        buttonbox.add_widget(buttonscale2)
        buttonbox.add_widget(buttonscale3)
        buttonbox.add_widget(buttonscale4)
        buttonbox.add_widget(bbackward)
        buttonbox.add_widget(bforward)
        buttonbox.add_widget(self.textnumber)
        buttonbox.add_widget(tnumber)

        allbox.add_widget(buttonbox)
        return allbox


if __name__ == '__main__':
    BoxLayoutMosaicColor().run()
    
