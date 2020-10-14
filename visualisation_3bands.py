import matplotlib
matplotlib.use("Agg")
from visualisation_1band import BoxLayout_main
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
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
import matplotlib.pyplot as plt
from functools import partial
from kivy.core.window import Window
class BoxLayoutColor(BoxLayout_main):


    def scale_val(self,image_array):
        if len(np.shape(image_array)) == 2:
            image_array = [image_array]
        vmin = np.min([self.background_rms_image(5, image_array[i]) for i in range(len(image_array))])
        xl, yl = np.shape(image_array[0])
        box_size = 14  # in pixel
        xmin = int((xl) / 2 - (box_size / 2))
        xmax = int((xl) / 2 + (box_size / 2))
        vmax = np.max([image_array[i][xmin:xmax, xmin:xmax] for i in range(len(image_array))])
        return vmin, vmax

    def showplot_rgb(self,rimage, gimage, bimage):
        vmin, vmax = self.scale_val([rimage, gimage, bimage])
        img = np.zeros((rimage.shape[0], rimage.shape[1], 3), dtype=float)
        img[:, :, 0] = self.sqrt_sc(rimage, scale_min=vmin, scale_max=vmax)
        img[:, :, 1] = self.sqrt_sc(gimage, scale_min=vmin, scale_max=vmax)
        img[:, :, 2] = self.sqrt_sc(bimage, scale_min=vmin, scale_max=vmax)
        return img

    def sqrt_sc(self,inputArray, scale_min=None, scale_max=None):
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


    def update(self,event):
        self.diplaystate = 0
        plt.clf()
        self.textnumber.text = str(self.counter)
        self.draw_plot(self.scale_state)
        self.oo.draw_idle()
        self.tclass.text = self.classification[self.counter]
        self.tsubclass.text = self.subclassification[self.counter]
        self.tname.text = self.listimage[self.counter]
        self.update_df()


    def draw_plot(self,scale_state,defaultvalue=True,max=1,min=0):

        try:



            image_B, image_G, image_R = [pyfits.open(self.pathtofile + self.listimage[self.counter])[0].data,
                                         pyfits.open(self.pathtofile + self.listimage[self.counter])[1].data,
                                         pyfits.open(self.pathtofile + self.listimage[self.counter])[2].data]

            print (np.shape(image_B),np.shape(image_R),np.shape(image_G))
            image_color = self.showplot_rgb(image_R, image_G, image_B)

            if defaultvalue == True:
                self.scale_min_b, self.scale_max_b = self.scale_val(image_B)
                self.scale_min_g, self.scale_max_g = self.scale_val(image_G)
                self.scale_min_r, self.scale_max_r = self.scale_val(image_R)
            else:
                self.scale_min_b = min
                self.scale_max_b = max
                self.scale_min_r = min
                self.scale_max_r = max
                self.scale_min_g = min
                self.scale_max_g = max

            if scale_state == 'linear':
                image_B = image_B.clip(min=self.scale_min_b, max=self.scale_max_b)
                image_B = (image_B - self.scale_min_b) / (self.scale_max_b - self.scale_min_b)
                indices = np.where(image_B < 0)
                image_B[indices] = 0.0
                indices = np.where(image_B > 1)
                image_B[indices] = 1.0

                image_G = image_G.clip(min=self.scale_min_g, max=self.scale_max_g)
                image_G = (image_G - self.scale_min_g) / (self.scale_max_g - self.scale_min_g)
                indices = np.where(image_G < 0)
                image_G[indices] = 0.0
                indices = np.where(image_G > 1)
                image_G[indices] = 1.0

                image_R = image_R.clip(min=self.scale_min_r, max=self.scale_max_r)
                image_R = (image_R - self.scale_min_r) / (self.scale_max_r - self.scale_min_r)
                indices = np.where(image_R < 0)
                image_R[indices] = 0.0
                indices = np.where(image_R > 1)
                image_R[indices] = 1.0

            elif scale_state == 'log':

                factor = math.log10(self.scale_max_b - self.scale_min_b)
                indices0 = np.where(image_B < self.scale_min_b)
                indices1 = np.where((image_B >= self.scale_min_b) & (image_B <= self.scale_max_b))
                indices2 = np.where(image_B > self.scale_max_b)
                image_B[indices0] = 0.0
                image_B[indices2] = 1.0
                try:
                    image_B[indices1] = np.log10(image_B[indices1]) / (factor * 1.0)
                except:
                    print ("Error on math.log10 ")
                factor = math.log10(self.scale_max_r - self.scale_min_r)
                indices0 = np.where(image_R < self.scale_min_r)
                indices1 = np.where((image_R >= self.scale_min_r) & (image_R <= self.scale_max_r))
                indices2 = np.where(image_R > self.scale_max_r)
                image_R[indices0] = 0.0
                image_R[indices2] = 1.0
                try:
                    image_R[indices1] = np.log10(image_R[indices1]) / (factor * 1.0)
                except:
                    print ("Error on math.log10 ")

                factor = math.log10(self.scale_max_g - self.scale_min_g)
                indices0 = np.where(image_G < self.scale_min_g)
                indices1 = np.where((image_G >= self.scale_min_g) & (image_G <= self.scale_max_g))
                indices2 = np.where(image_G > self.scale_max_g)
                image_G[indices0] = 0.0
                image_G[indices2] = 1.0
                try:
                    image_G[indices1] = np.log10(image_G[indices1]) / (factor * 1.0)
                except:
                    print ("Error on math.log10 ")

            elif scale_state == 'sqrt':
                image_B = image_B.clip(min=self.scale_min_b, max=self.scale_max_b)
                image_B = image_B - self.scale_min_b
                indices = np.where(image_B < 0)
                image_B[indices] = 0.0
                image_B = np.sqrt(image_B)
                image_B = image_B / math.sqrt(self.scale_max_b - self.scale_min_b)

                image_R = image_R.clip(min=self.scale_min_r, max=self.scale_max_r)
                image_R = image_R - self.scale_min_r
                indices = np.where(image_R < 0)
                image_R[indices] = 0.0
                image_R = np.sqrt(image_R)
                image_R = image_R / math.sqrt(self.scale_max_r - self.scale_min_r)

                image_G = image_G.clip(min=self.scale_min_g, max=self.scale_max_g)
                image_G = image_G - self.scale_min_g
                indices = np.where(image_G < 0)
                image_G[indices] = 0.0
                image_G = np.sqrt(image_G)
                image_G = image_G / math.sqrt(self.scale_max_g - self.scale_min_g)

            elif scale_state == 'asinh':
                factor = np.arcsinh((self.scale_max_b - self.scale_min_b) / 2.0)
                indices0 = np.where(image_B < self.scale_min_b)
                indices1 = np.where((image_B >= self.scale_min_b) & (image_B <= self.scale_max_b))
                indices2 = np.where(image_B > self.scale_max_b)
                image_B[indices0] = 0.0
                image_B[indices2] = 1.0
                image_B[indices1] = np.arcsinh((image_B[indices1] - self.scale_min_b) / 2.0) / factor

                factor = np.arcsinh((self.scale_max_r - self.scale_min_r) / 2.0)
                indices0 = np.where(image_R < self.scale_min_r)
                indices1 = np.where((image_R >= self.scale_min_r) & (image_R <= self.scale_max_r))
                indices2 = np.where(image_R > self.scale_max_r)
                image_R[indices0] = 0.0
                image_R[indices2] = 1.0
                image_R[indices1] = np.arcsinh((image_R[indices1] - self.scale_min_r) / 2.0) / factor

                factor = np.arcsinh((self.scale_max_g - self.scale_min_g) / 2.0)
                indices0 = np.where(image_G < self.scale_min_g)
                indices1 = np.where((image_G >= self.scale_min_g) & (image_G <= self.scale_max_g))
                indices2 = np.where(image_G > self.scale_max_g)
                image_G[indices0] = 0.0
                image_G[indices2] = 1.0
                image_G[indices1] = np.arcsinh((image_G[indices1] - self.scale_min_g) / 2.0) / factor

            plt.style.use('dark_background')
            plt.subplot(2, 2, 1)
            plt.imshow(image_B)
            plt.subplot(2, 2, 1).text(5, 5, 'G', fontsize=18, ha='center', va='center')
            plt.style.use('dark_background')
            plt.axis('off')

            plt.subplot(2, 2, 2)
            plt.imshow(image_G)
            plt.subplot(2, 2, 2).text(5, 5, 'R', fontsize=18, ha='center', va='center')
            plt.style.use('dark_background')
            plt.axis('off')


            plt.subplot(2, 2, 3)
            plt.imshow(image_R)
            plt.subplot(2, 2, 3).text(5, 5, 'I', fontsize=18, ha='center', va='center')
            plt.style.use('dark_background')
            plt.axis('off')

            plt.subplot(2, 2, 4)
            plt.imshow(image_color)
            plt.style.use('dark_background')
            plt.axis('off')

            plt.subplots_adjust(top=0.99, bottom=0.01, left=0.01, right=0.99, hspace=0.0,
            wspace=0.0)


        except IndexError:
            popup = Popup(title=' ', content=Label(text='Incorrect format for color image'), size_hint=(None, None),
                          size=(400, 100))
            popup.open()

    def build(self):
        # Please enter the path of ds9 executable here:
        self.pathds9 = 'C:\\SAOImageDS9\\ds9.exe'

        self.pathtofile = './files_to_visualize/'

        self.listimage = sorted([os.path.basename(x) for x in glob.glob(self.pathtofile+ '*.fits')])
        self.counter = 0
        self.number_graded = 0
        self.COUNTER_MIN = 0
        self.COUNTER_MAX = len(self.listimage)


        self.classification = ['None'] * len(self.listimage)
        self.subclassification = ['None'] * len(self.listimage)
        self.comment = [' '] * len(self.listimage)
        self.scale_min = 0
        self.scale_max = 1

        self.scale_min_r=0
        self.scale_min_g = 0
        self.scale_min_b = 0
        self.scale_max_r = 1
        self.scale_max_g = 1
        self.scale_max_b = 1


        self.limit_max = 1
        self.limit_min = 0
        self.step = (self.scale_max - self.scale_min) / 10.

        self.scale_state = 'asinh'
        self.diplaystate = 0

        self.df = self.obtain_df()
        self.oo = FigureCanvasKivyAgg(plt.gcf())
        superBox = BoxLayout(orientation='vertical')

        horizontalBoxup = BoxLayout(orientation='horizontal', size_hint_y=0.1)

        horizontalBox = BoxLayout(orientation='horizontal')
        self.tname = Label(text=self.listimage[self.counter], font_size=20, size_hint_y=0.1)

        # button1 = Button(text="One",size_hint_x=0.1)


        self.draw_plot(self.scale_state)

        horizontalBox.add_widget(self.oo)

        verticalBox1 = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        verticalBox = BoxLayout(orientation='horizontal', size_hint_y=0.15)

        button3 = Button(text="Sure Lens", background_color=(0.4, 1, 0, 1))
        button32 = Button(text="Single Arc", background_color=(0.4, 1, 0, 1))

        button4 = Button(text="Maybe Lens", background_color=(0.4, 1, 0, 1))

        button5 = Button(text="Non Lens", background_color=(0.4, 1, 0, 1))
        button6 = Button(text="Merger")
        button7 = Button(text="Spiral")
        button8 = Button(text="Ring")
        button9 = Button(text="Elliptical")
        button10 = Button(text="Disk")
        button3.bind(on_press=partial(self.classify, 'L', 1))
        button32.bind(on_press=partial(self.classify, 'SA', 1))
        button4.bind(on_press=partial(self.classify, 'ML', 1))
        button5.bind(on_press=partial(self.classify, 'NL', 1))
        button6.bind(on_press=partial(self.classify, 'Merger', 2))
        button7.bind(on_press=partial(self.classify, 'Spiral', 2))
        button8.bind(on_press=partial(self.classify, 'Ring', 2))
        button9.bind(on_press=partial(self.classify, 'Elliptical', 2))
        button10.bind(on_press=partial(self.classify, 'Disk', 2))

        buttonscale1 = Button(text="Linear")
        buttonscale2 = Button(text="Sqrt")
        buttonscale3 = Button(text="Log")
        buttonscale4 = Button(text="Asinh")
        buttonscale1.bind(on_press=partial(self.change_scale, 'linear'))
        buttonscale2.bind(on_press=partial(self.change_scale, 'sqrt'))
        buttonscale3.bind(on_press=partial(self.change_scale, 'log'))
        buttonscale4.bind(on_press=partial(self.change_scale, 'asinh'))

        LSbutton = Button(text="LS", font_size=25, size_hint_x=0.1)
        LSbutton.bind(on_press=self.get_legacy_survey)
        savebutton = Button(text="Save csv", background_color=(0, 1, 0.4, 1), font_size=25, size_hint_x=0.4 )
        savebutton.bind(on_press=self.save_csv)
        commentbutton = Button(text="Comment", background_color=(0, 1, 0.4, 1), font_size=25, size_hint_x=0.3)
        commentbutton.bind(on_press=self.add_comment)
        self.textnumber = TextInput(text=str(self.counter), multiline=False, font_size=25, size_hint_x=0.1)
        self.textnumber.bind(on_text_validate=self.change_number)
        tnumber = Label(text=str(' ' + str(self.COUNTER_MAX-1)), font_size=25, size_hint_x=0.1)
        buttonds9 = Button(text="ds9", font_size=25, size_hint_x=0.1)
        buttonds9.bind(on_press=self.open_ds9)
        self.tclass = Label(text=self.classification[self.counter], font_size=25, size_hint_x=0.1)
        self.tsubclass = Label(text=self.subclassification[self.counter], font_size=25, size_hint_x=0.1)

        horizontalBoxup.add_widget(LSbutton)
        horizontalBoxup.add_widget(buttonds9)
        horizontalBoxup.add_widget(savebutton)
        horizontalBoxup.add_widget(commentbutton)
        horizontalBoxup.add_widget(self.tclass)
        horizontalBoxup.add_widget(self.tsubclass)
        horizontalBoxup.add_widget(self.textnumber)
        horizontalBoxup.add_widget(tnumber)

        verticalBox.add_widget(button3)
        verticalBox.add_widget(button32)

        verticalBox.add_widget(button4)
        verticalBox.add_widget(button5)
        verticalBox.add_widget(button6)
        verticalBox.add_widget(button7)
        verticalBox.add_widget(button8)
        verticalBox.add_widget(button9)
        verticalBox.add_widget(button10)

        bforward = Button(text=" --> ")
        bbackward = Button(text=" <-- ")
        bforward.bind(on_press=self.forward)
        bbackward.bind(on_press=self.backward)
        verticalBox1.add_widget(bbackward)
        verticalBox1.add_widget(bforward)
        verticalBox1.add_widget(buttonscale1)
        verticalBox1.add_widget(buttonscale2)
        verticalBox1.add_widget(buttonscale3)
        verticalBox1.add_widget(buttonscale4)

        superBox.add_widget(horizontalBoxup)
        superBox.add_widget(horizontalBox)

        superBox.add_widget(verticalBox1)
        superBox.add_widget(verticalBox)
        superBox.add_widget(self.tname)
        '''
        self._keyboard = Window.request_keyboard(self, self._keyboard_closed)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        '''
        return superBox


if __name__ == '__main__':
    BoxLayoutColor().run()
