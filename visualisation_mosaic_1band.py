
import matplotlib

matplotlib.use("Agg")
from visualisation_2 import BoxLayout_main
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
import time
import random


class CustomButton(Button):
    def __init__(self, lensing_value, **kwargs):
        Button.__init__(self, **kwargs)
        self.lensing_value=lensing_value

    def set_background_normal(self, image_path):
        self.background_normal = image_path
    def set_lensing_value(self,l):
        self.lensing_value=l



    def get_lensing_value(self):
        return self.lensing_value


class BoxLayoutMosaic(BoxLayout_main):
    def set_start_number(self):

        self.counter = self.forward_backward_state * 100

    def read_fits(self, i):

        file = self.pathtofile + self.listimage[i]
        # Note : memmap=False is much faster when opening/closing many small files
        with pyfits.open(file, memmap=False) as hdu_list:
            image = hdu_list[0].data
        return image



    def draw_image(self, index, scale_state, defaultvalue=True, max=1, min=0):

        try:
            image = self.read_fits(index)
        except IndexError:
            image = np.ones((44, 44)) * 0.0000001

        if defaultvalue == True:
            self.scale_min, self.scale_max = self.scale_val(image)
            self.limit_max = np.amax(image)
            self.limit_min = np.amax(image)
            self.step = (self.limit_max - self.limit_min) / 10.

        else:
            self.scale_min = min
            self.scale_max = max

        if scale_state == 'linear':

            image = image.clip(min=self.scale_min, max=self.scale_max)
            image = (image - self.scale_min) / (self.scale_max - self.scale_min)
            indices = np.where(image < 0)
            image[indices] = 0.0
            indices = np.where(image > 1)
            image[indices] = 1.0
        elif scale_state == 'log':

            try:
                factor = math.log10(self.scale_max - self.scale_min)

                indices0 = np.where(image < self.scale_min)
                indices1 = np.where((image >= self.scale_min) & (image <= self.scale_max))
                indices2 = np.where(image > self.scale_max)
                image[indices0] = 0.0
                image[indices2] = 1.0

                image[indices1] = np.log10(image[indices1]) / (factor * 1.0)
            except ValueError:
                popup = Popup(title='Error ', content=Label(text='Log of negative number'), size_hint=(None, None),
                              size=(400, 100))
                popup.open()
        elif scale_state == 'sqrt':
            image = image.clip(min=self.scale_min, max=self.scale_max)
            image = image - self.scale_min
            indices = np.where(image < 0)
            image[indices] = 0.0
            image = np.sqrt(image)
            image = image / math.sqrt(self.scale_max - self.scale_min)
        elif scale_state == 'asinh':
            factor = np.arcsinh((self.scale_max - self.scale_min) / 2.0)
            indices0 = np.where(image < self.scale_min)
            indices1 = np.where((image >= self.scale_min) & (image <= self.scale_max))
            indices2 = np.where(image > self.scale_max)
            image[indices0] = 0.0
            image[indices2] = 1.0
            image[indices1] = np.arcsinh((image[indices1] - self.scale_min) / 2.0) / factor

        return image
    '''
    def prepare_numpy_array(self):
        for i in np.arange(len(self.listimage)):
            image, height, width = self.numpyarray_from_fits(self.pathtofile + self.listimage[i])
            np.save(self.pathtoscratch_numpy + str(i + 1), image)
    '''
    def prepare_png(self, number):

        start = self.counter

        for i in np.arange(start, start + number + 1):
            img = self.draw_image(i, self.scale_state)

            image = Image.fromarray(np.uint8(img * 255), 'L')
            image = image.resize((150, 150), Image.ANTIALIAS)
            image.save(self.pathtoscratch + str(i + 1) + self.scale_state + str(start) + '.png', 'PNG')

            self.counter = self.counter + 1

    def clean_scratch(self, path_dir):
        filelist = os.listdir(path_dir)
        for f in filelist:
            os.remove(path_dir + f)

    def repeat_random_objects(self,fraction):
        number_of_duplicate=round(fraction*len(self.listimage))
        print('duplicate',number_of_duplicate,fraction*len(self.listimage))
        random.seed(self.random_seed)
        try:
            samples = random.sample(self.listimage, number_of_duplicate)
        except ValueError:
            samples = random.sample(self.listimage, 0)
            print("fraction higher than 1, number of repeated objects set to 0.")

        self.listimage.extend(samples)






    def update(self, event):

        self.set_start_number()
        start = self.counter
        self.textnumber.text = str(self.forward_backward_state)
        self.clean_scratch(self.pathtoscratch)

        self.prepare_png(100)

        i = start
        j=0

        for button in self.list_of_buttons:

            try:
                if self.dataframe['classification'][100 * self.forward_backward_state + j] == 0:
                    button.set_background_normal(self.pathtoscratch + str(i + 1) + self.scale_state + str(start) + '.png')
                    button.set_lensing_value(0)

                else:
                    button.set_background_normal(self.path_background)
                    button.set_lensing_value(1)
                self.dataframe['Grid_pos'].iloc[100 * self.forward_backward_state + j] = j + 1
            except KeyError:
                button.set_background_normal(self.pathtoscratch + str(i + 1) + self.scale_state + str(start) + '.png')


            # button.set_background_normal('cutecat.png')

            j=j+1
            i = i + 1
    def change_number(self,event):
        try:
            number=int(self.textnumber.text)
        except ValueError:
            number =self.counter
            popup = Popup(title=' ', content=Label(text='Not an int'), size_hint=(None, None),
                          size=(400, 100))
            popup.open()

        if number < 0:
            popup = Popup(title=' ', content=Label(text='Wrong number'), size_hint=(None, None),
                          size=(400, 100))
            popup.open()
        elif number * 100 > len(self.listimage):
            print(number * 100 + 100,len(self.listimage),'****')
            popup = Popup(title=' ', content=Label(text='Wrong number'), size_hint=(None, None),
                          size=(400, 100))
            popup.open()

        else:
            self.forward_backward_state=number
            self.update(event)
    def forward(self, event):
        maxforward = len(self.listimage) / 100 + 1
        self.forward_backward_state = self.forward_backward_state + 1

        if self.forward_backward_state * 100 +100 > len(self.listimage):

            if self.forward_backward_state > maxforward:
                self.forward_backward_state = self.forward_backward_state - 1

            popup = Popup(title=' ', content=Label(text='Last Frame'), size_hint=(None, None),
                          size=(400, 100))
            self.update(event)
            popup.open()




        else:
            self.update(event)

    def backward(self, event):
        self.forward_backward_state = self.forward_backward_state - 1
        if self.forward_backward_state < 0:
            self.forward_backward_state = 0
            self.update(event)
            popup = Popup(title=' ', content=Label(text='First frame'), size_hint=(None, None),
                          size=(400, 100))
            popup.open()
        else:
            self.update(event)

    def on_click(self, number, event):
        if 100 * self.forward_backward_state + number > len(self.listimage):
            print('Not an image')
        else:


            self.dataframe['Grid_pos'].iloc[100 * self.forward_backward_state + number]=number+1



            self.list_of_buttons[number].set_lensing_value(np.abs(self.list_of_buttons[number].get_lensing_value()-1))
            if self.list_of_buttons[number].get_lensing_value()==0:

                self.list_of_buttons[number].set_background_normal( self.pathtoscratch + str(number + 1 + self.forward_backward_state * 100) + self.scale_state + str(self.counter - 101) + '.png')

                self.dataframe['classification'].iloc[100 * self.forward_backward_state + number] = 0
            else:

                self.list_of_buttons[number].set_background_normal(self.path_background)

                self.dataframe['classification'].iloc[100 * self.forward_backward_state + number] = 1
            self.dataframe.to_csv('./classifications/classification_mosaic_autosave' + '.csv', index=False)


    def create_df(self):
        class_file = np.sort(glob.glob('./classifications/classification_mosaic_autosave.csv'))
        print (class_file, len(class_file))
        if len(class_file) >= 1:

            print('reading ' + str(class_file[len(class_file) - 1]))
            df = pd.read_csv(class_file[len(class_file) - 1])

        else:
            print('creating dataframe')
            dfc = ['file_name', 'classification','Grid_pos']
            df = pd.DataFrame(columns=dfc)
            df['file_name'] = self.listimage
            df['classification'] = np.zeros(np.shape(self.listimage))
            df['Grid_pos'] = np.zeros(np.shape(self.listimage))

        return df

    def build(self):
        #self.pathds9 = 'C:\\SAOImageDS9\\ds9.exe'

        self.pathtofile = './files_to_visualize/'
        #self.pathtofile ='D:\\Simunoboost\\'




        self.pathtoscratch = './scratch_png/'

        self.path_background='green.png'

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

        self.clean_scratch(self.pathtoscratch)



        random.Random(self.random_seed).shuffle(self.listimage)

        self.start_image_number = 0
        self.counter = 0
        self.scale_min = 0
        self.scale_max = 1
        self.limit_max = 1
        self.limit_min = 0
        self.step = (self.scale_max - self.scale_min) / 10.
        self.scale_state = 'linear'
        self.number_per_frame = 100
        self.forward_backward_state = 0
        self.total_n_frame =int(len(self.listimage)/100.)
        self.dataframe = self.create_df()


        self.prepare_png(self.number_per_frame)
        allbox = BoxLayout(orientation='vertical')
        buttonbox = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        superbox = GridLayout(cols=10, size_hint_y=0.9)
        self.list_of_buttons = []
        for i in np.arange(self.number_per_frame):
            try:
                if self.dataframe['classification'][i]==0:
                    self.list_of_buttons.append(
                        CustomButton(0,background_normal=self.pathtoscratch + str(i + 1) + self.scale_state + str(0) + '.png'))
                else:
                    self.list_of_buttons.append(
                        CustomButton(1, background_normal=self.path_background))
                self.dataframe['Grid_pos'].iloc[100 * self.forward_backward_state + i] = i + 1
            except KeyError:
                self.list_of_buttons.append(CustomButton(1, background_normal=self.pathtoscratch + str(i + 1) + self.scale_state + str(0) + '.png'))

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
    BoxLayoutMosaic().run()


