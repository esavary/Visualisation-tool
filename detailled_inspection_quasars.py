import matplotlib
matplotlib.use("Agg")
from visualisation_1band import BoxLayout_main
from visualisation_1band import ColoredFigureCanvasKivyAgg
from visualisation_1band import CustomSlider
import math
import numpy as np
import sys
import webbrowser
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
import platform
from astroquery.sdss import SDSS
from astropy import coordinates as coords



class BoxLayoutQUASARS(BoxLayout_main):


    def get_sdss_spectra(self,event):
        s_path = './csv_catalog/'
        sam = glob.glob(s_path + '*.csv')
        if len(sam) == 1:
            try:
                sample = pd.read_csv(sam[0])
                ra = sample.iloc[self.counter]['ra']
                dec = sample.iloc[self.counter]['dec']

                pos = coords.SkyCoord(ra, dec, unit='deg')
                # pos = coords.SkyCoord(150.36921, 50.46581,  unit='deg')

                xid = SDSS.query_region(pos, spectro=True)
                plate = int(xid['plate'])
                mjd = int(xid['mjd'])
                fiberID = int(xid['fiberID'])
                webbrowser.open("https://dr14.sdss.org/optical/spectrum/view?id=309946&plate="+str(plate)+"&mjd="+str(mjd)+"&fiberid="+str(fiberID), new=1)
            except TypeError:
                popup = Popup(title='No spectrum available ', content=Label(text='No spectrum available for this object'), size_hint=(None, None),
                              size=(400, 100))
                popup.open()

    def build(self):
        # Please enter the path of ds9 executable here:
        # self.pathds9 = 'C:\\SAOImageDS9\\ds9.exe'
        os_def = platform.system()
        print(os_def)
        if os_def == 'Linux':
            self.pathds9 = '/usr/local/bin/ds9'
            print('If your DS9 is not in /usr/local/bin/ds9 please edit the right path')
        if os_def == 'Windows':
            self.pathds9 = 'C:\\SAOImageDS9\\ds9.exe'
            print('If your DS9 is not in C:\\SAOImageDS9\\ds9.exe please edit the right path')
        # this is for mac but don't know the path
        if os_def == 'Darwin':
            self.pathds9 = 'ds9'
            print('Edit the right path to your ds9 executable depending on your OS')
        else:
            print('Edit the right path to your ds9 executable depending on your OS')

        self.pathtofile = './files_to_visualize/'

        self.listimage = sorted([os.path.basename(x) for x in glob.glob(self.pathtofile + '*.fits')])
        self.counter = 0
        self.number_graded = 0
        self.COUNTER_MIN = 0
        self.COUNTER_MAX = len(self.listimage)

        # self.listnames = self.listimage
        self.classification = ['None'] * len(self.listimage)
        self.subclassification = ['None'] * len(self.listimage)
        self.comment = [' '] * len(self.listimage)
        self.scale_min = 0
        self.scale_max = 1
        self.limit_max = 1
        self.limit_min = 0
        self.step = (self.scale_max - self.scale_min) / 10.
        self.colormap = 'gray'  # 'gist_yarg'

        self.scale_state = 'asinh'
        self.diplaystate = 0
        self.df = self.obtain_df()
        '''
        self._keyboard = Window.request_keyboard(self,self._keyboard_closed)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        '''

        self.oo = ColoredFigureCanvasKivyAgg(0.0, 0.0, 0.0, 0.0, plt.gcf(), size_hint_x=0.9)

        superBox = BoxLayout(orientation='vertical')

        horizontalBoxup = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        self.tname = Label(text=self.listimage[self.counter], font_size=20, size_hint_y=0.1)

        horizontalBox = BoxLayout(orientation='horizontal')

        # button1 = Button(text="One",size_hint_x=0.1)

        self.slider1 = CustomSlider(orientation='vertical', size_hint_x=0.1, min=self.limit_min, max=self.limit_max,
                                    step=self.step, value=self.scale_min)
        self.slider2 = CustomSlider(orientation='vertical', size_hint_x=0.1, min=self.limit_min, max=self.limit_max,
                                    step=self.step, value=self.scale_max)
        self.slider1.bind(value=self.min_slider_release)
        self.slider2.bind(value=self.max_slider_release)
        horizontalBox.add_widget(self.slider1)
        horizontalBox.add_widget(self.slider2)
        self.draw_plot(self.scale_state)

        horizontalBox.add_widget(self.oo)

        verticalBox1 = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        verticalBox = BoxLayout(orientation='horizontal', size_hint_y=0.15)

        button3 = Button(text="Sure Lens", background_color=(0.4, 1, 0, 1))
        button32 = Button(text="Flexion", background_color=(0.4, 1, 0, 1))

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
        buttoncolormap1 = Button(text="Inverted")
        buttoncolormap2 = Button(text="Bb8")
        buttoncolormap3 = Button(text="Gray")
        buttonscale1.bind(on_press=partial(self.change_scale, 'linear'))
        buttonscale2.bind(on_press=partial(self.change_scale, 'sqrt'))
        buttonscale3.bind(on_press=partial(self.change_scale, 'log'))
        buttonscale4.bind(on_press=partial(self.change_scale, 'asinh'))
        buttoncolormap1.bind(on_press=partial(self.change_colormap, 'gist_yarg'))
        buttoncolormap2.bind(on_press=partial(self.change_colormap, 'hot'))
        buttoncolormap3.bind(on_press=partial(self.change_colormap, 'gray'))

        savebutton = Button(text="Save csv", background_color=(0, 1, 0.4, 1), font_size=25, size_hint_x=0.2)
        savebutton.bind(on_press=self.save_csv)
        commentbutton = Button(text="Comment", background_color=(0, 1, 0.4, 1), font_size=25, size_hint_x=0.2)
        commentbutton.bind(on_press=self.add_comment)
        LSbutton = Button(text="LS", font_size=25, size_hint_x=0.1)
        LSbutton.bind(on_press=self.get_legacy_survey)
        sprectrabutton= Button(text="spectrum", font_size=25, size_hint_x=0.2)
        sprectrabutton.bind(on_press=self.get_sdss_spectra)


        self.textnumber = TextInput(text=str(self.counter), multiline=False, font_size=25, size_hint_x=0.1)
        self.textnumber.bind(on_text_validate=self.change_number)
        self.tclass = Label(text=self.classification[self.counter], font_size=25, size_hint_x=0.1)
        self.tsubclass = Label(text=self.subclassification[self.counter], font_size=25, size_hint_x=0.1)
        tnumber = Label(text=str(' / ' + str(self.COUNTER_MAX - 1)), font_size=25, size_hint_x=0.1)
        buttonds9 = Button(text="ds9", font_size=25, size_hint_x=0.1)
        buttonds9.bind(on_press=self.open_ds9)

        horizontalBoxup.add_widget(LSbutton)
        horizontalBoxup.add_widget(buttonds9)
        horizontalBoxup.add_widget(sprectrabutton)
        horizontalBoxup.add_widget(savebutton)
        horizontalBoxup.add_widget(commentbutton)
        horizontalBoxup.add_widget(self.tclass)
        horizontalBoxup.add_widget(self.tsubclass)
        horizontalBoxup.add_widget(self.textnumber)
        horizontalBoxup.add_widget(tnumber)

        verticalBox.add_widget(button3)

        verticalBox.add_widget(button4)
        verticalBox.add_widget(button32)
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
        verticalBox1.add_widget(buttoncolormap1)
        verticalBox1.add_widget(buttoncolormap2)
        verticalBox1.add_widget(buttoncolormap3)

        superBox.add_widget(horizontalBoxup)
        superBox.add_widget(horizontalBox)

        superBox.add_widget(verticalBox1)
        superBox.add_widget(verticalBox)
        superBox.add_widget(self.tname)

        return superBox

    # Instantiate and run the kivy app


if __name__ == '__main__':
    BoxLayoutQUASARS().run()


