# imports
import matplotlib
matplotlib.use("Agg")
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
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
import matplotlib.pyplot as plt
from functools import partial
from kivy.core.window import Window
import platform
from matplotlib.backends.backend_agg import FigureCanvasAgg
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle, Color


class ColoredFigureCanvasKivyAgg(FigureCanvasKivyAgg):
    def __init__(self, colorarg1,colorarg2,colorarg3,colorarg4,figure, **kwargs):
        self.color_arg1=colorarg1
        self.color_arg2 = colorarg2
        self.color_arg3 = colorarg3
        self.color_arg4 = colorarg4
        super(ColoredFigureCanvasKivyAgg, self).__init__(figure,**kwargs)
    def draw(self):
        '''
        Draw the figure using the agg renderer
        '''
        self.canvas.clear()
        FigureCanvasAgg.draw(self)
        if self.blitbox is None:
            l, b, w, h = self.figure.bbox.bounds
            w, h = int(w), int(h)
            buf_rgba = self.get_renderer().buffer_rgba()
        else:
            bbox = self.blitbox
            l, b, r, t = bbox.extents
            w = int(r) - int(l)
            h = int(t) - int(b)
            t = int(b) + h
            reg = self.copy_from_bbox(bbox)
            buf_rgba = reg.to_string()
        
        texture = Texture.create(size=(w, h))
        texture.flip_vertical()
        facecolor = 'white'
        color = facecolor#self.figure.get_facecolor()
        with self.canvas:
            Color(*color)
            Rectangle(pos=self.pos, size=(w, h))
            #Color(self.color_arg1, self.color_arg2, self.color_arg3, self.color_arg4)
            Color(1,1,1,1)
            self.img_rect = Rectangle(texture=texture, pos=self.pos,
                                      size=(w,h))
        texture.blit_buffer(bytes(buf_rgba), colorfmt='rgba', bufferfmt='ubyte')
        self.img_texture = texture




class CommentDialog(Popup):

    def __init__(self,originalBoxLayout):
        super(CommentDialog,self).__init__()
        self.originalBox=originalBoxLayout
        self.content = BoxLayout(orientation="horizontal")
        self.content1 = BoxLayout(orientation="vertical",size_hint_x=0.2)
        self.content2 = BoxLayout(orientation="vertical",size_hint_x=0.8)
        self.name_input = TextInput(text='Type your comment here. Please do not use line break')

        self.save_button = Button(text='Add')
        self.save_button.bind(on_press=self.enterComment)

        self.cancel_button = Button(text='Cancel')
        self.cancel_button.bind(on_press=self.cancel)

        self.content1.add_widget(self.save_button)
        self.content2.add_widget(self.name_input)
        self.content1.add_widget(self.cancel_button)
        self.content.add_widget(self.content1)
        self.content.add_widget(self.content2)

    def cancel(self, *args):
        print ("cancel")
        self.dismiss()
    def enterComment(self, *args):
        self.originalBox.comment[self.originalBox.counter]= self.name_input.text
        print(self.originalBox.comment[self.originalBox.counter])
        self.dismiss()


class LSDialog(Popup):

    def __init__(self,ra,dec,savedir):
        super(LSDialog,self).__init__()
        self.content = BoxLayout(orientation="vertical")
        self.content1 = BoxLayout(orientation="horizontal",size_hint_y=0.9)

        self.img1 = Image(source=savedir+str(ra) + '_' + str(dec) + 'dr8.jpg')
        self.img2 = Image(source=savedir+str(ra) + '_' + str(dec) + 'dr8-resid.jpg')
        self.cancel_button = Button(text='Close',size_hint_y=0.1)
        self.cancel_button.bind(on_press=self.cancel)
        self.content1.add_widget(self.img1)
        self.content1.add_widget(self.img2)
        self.content.add_widget(self.content1)
        self.content.add_widget(self.cancel_button)
    def cancel(self,*args):
        self.dismiss()








# Boxlayout is the App class
class SaveDialog(Popup):

    def __init__(self,listnames,classification,subclassification,comments,**kwargs):
        super(SaveDialog,self).__init__()
        self.listnames=listnames
        self.classification=classification
        self.comment=comments
        self.subclassification = subclassification
        self.content = BoxLayout(orientation="vertical")
        self.content1 = BoxLayout(orientation="horizontal",size_hint_y=0.2)
        self.content2 = BoxLayout(orientation="horizontal",size_hint_y=0.8)
        self.name_input = TextInput(text='name')

        self.save_button = Button(text='Save')
        self.save_button.bind(on_press=self.save)

        self.cancel_button = Button(text='Cancel')
        self.cancel_button.bind(on_press=self.cancel)

        self.content1.add_widget(self.save_button)
        self.content2.add_widget(self.name_input)
        self.content1.add_widget(self.cancel_button)
        self.content.add_widget(self.content1)
        self.content.add_widget(self.content2)






    def save(self,*args):
        print( "save ",self.name_input.text)
        np.savetxt( './classifications/'+self.name_input.text+ '.csv',
                   np.transpose(np.array([self.listnames,self.classification,self.subclassification,self.comment], dtype='U40')),
                   delimiter=",", fmt='%s')
        self.dismiss()

    def cancel(self,*args):
        print ("cancel")
        self.dismiss()

class CustomSlider(Slider):
    def set_value(self,value):
        self.value=value

    def set_step(self,step):
        self.step=step
    def set_min(self,min):
        self.min=min

    def set_max(self, max):
        self.max = max



class BoxLayout_main(App):

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == '1':
            self.classify('L',keyboard)
        elif keycode[1] == '2':
            self.classify('ML',keyboard)
        elif keycode[1] == '3':
            self.classify('NL',keyboard)
        elif keycode[1] == '4':
            self.classify('Merger',keyboard)
        elif keycode[1] == '5':
            self.classify('Merger',keyboard)
        elif keycode[1] == '6':
            self.classify('Ring',keyboard)
        return True




    def background_rms_image(self,cb, image):
    
    
        xg, yg = np.shape(image)
        cut0 = image[0:cb, 0:cb]
        cut1 = image[xg - cb:xg, 0:cb]
        cut2 = image[0:cb, yg - cb:yg]
        cut3 = image[xg - cb:xg, yg - cb:yg]
        l = [cut0, cut1, cut2, cut3]
        m = np.mean(np.mean(l, axis=1), axis=1)
        ml = min(m)
        mm = max(m)
        if mm > 5 * ml:
            s = np.sort(l, axis=0)
            nl = s[:-1]
            std = np.std(nl)
        else:
            std = np.std([cut0, cut1, cut2, cut3])
        return std

    def scale_val(self,image_array):
        if len(np.shape(image_array)) == 2:
            image_array = [image_array]
        vmin = np.min([self.background_rms_image(5, image_array[i]) for i in range(len(image_array))])
        xl, yl = np.shape(image_array[0])
        box_size = 14  # in pixel
        xmin = int((xl) / 2. - (box_size / 2.))
        xmax = int((xl) / 2. + (box_size / 2.))
        vmax = np.max([image_array[i][xmin:xmax, xmin:xmax] for i in range(len(image_array))])
        return vmin, vmax

    def numpyarray_from_fits(self,fits_path, ind_image=0, color=False):

        _img = pyfits.open(fits_path)[ind_image].data
        try:
            height, width = np.shape(_img)
            return _img, height, width
        except ValueError:
            n, height, width = np.shape(_img)
            if color == True:
                return _img[0], _img[1], _img[2], height, width
            else:
                return _img[0], height, width

    def draw_plot(self,scale_state,defaultvalue=True,max=1,min=0):


        image, height, width = self.numpyarray_from_fits(self.pathtofile + self.listimage[self.counter])

        if defaultvalue==True:
            self.scale_min, self.scale_max = self.scale_val(image)
            self.limit_max=np.amax(image)
            self.limit_min=np.amax(image)
            self.step = (self.limit_max - self.limit_min) / 10.

        else:
            self.scale_min = min
            self.scale_max = max

        if scale_state=='linear':

            image = image.clip(min=self.scale_min, max=self.scale_max)
            image = (image - self.scale_min) / (self.scale_max - self.scale_min)
            indices = np.where(image < 0)
            image[indices] = 0.0
            indices = np.where(image > 1)
            image[indices] = 1.0
        elif scale_state == 'log':
            print ('factor',self.scale_min)
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
        elif scale_state=='sqrt':
            try:
                image = image.clip(min=self.scale_min, max=self.scale_max)
                image = image - self.scale_min
                indices = np.where(image < 0)
                image[indices] = 0.0
                image = np.sqrt(image)
                image = image / math.sqrt(self.scale_max - self.scale_min)
            except ValueError:
                popup = Popup(title='Error ', content=Label(text='Sqrt of negative number'), size_hint=(None, None),
                              size=(400, 100))
                popup.open()
        elif scale_state=='asinh':
            factor = np.arcsinh((self.scale_max - self.scale_min) / 2.0)
            indices0 = np.where(image < self.scale_min)
            indices1 = np.where((image >= self.scale_min) & (image <= self.scale_max))
            indices2 = np.where(image > self.scale_max)
            image[indices0] = 0.0
            image[indices2] = 1.0
            image[indices1] = np.arcsinh((image[indices1] - self.scale_min) / 2.0) / factor

        #figure1 = plt.Figure(figsize=(50, 50), dpi=100)
        plt.gcf().set_facecolor('black')
        plt.imshow(image, cmap=self.colormap, origin='lower')
        plt.axis('off')
    def min_slider_release(self,event,val):
        if self.diplaystate>2:

            valueslider=val

            self.draw_plot(self.scale_state,defaultvalue=False,max=self.scale_max,min=valueslider)
            self.oo.draw_idle()
        else:
            self.diplaystate=self.diplaystate+1

    def max_slider_release(self,event,val):
        if self.diplaystate > 2:

            valueslider=val

            self.draw_plot(self.scale_state,defaultvalue=False,max=valueslider,min=self.scale_min)
            self.oo.draw_idle()
        else:
            self.diplaystate=self.diplaystate+1

    def update(self,event):
        self.diplaystate = 0
        plt.clf()
        self.textnumber.text = str(self.counter)
        self.draw_plot(self.scale_state)
        self.oo.draw_idle()
        self.tclass.text=self.classification[self.counter]
        self.tname.text = self.listimage[self.counter]
        self.tsubclass.text = self.subclassification[self.counter]


        self.slider1.set_step(float(self.step))
        self.slider1.set_min(float(self.scale_min))
        self.slider1.set_max(float(self.scale_max))
        self.slider1.set_value(float(self.scale_min))


        self.slider2.set_step(float(self.step))
        self.slider2.set_min(float(self.scale_min))
        self.slider2.set_max(float(self.scale_max))
        self.slider2.set_value(float(self.scale_max))


    def save_csv(self,event):
        popup = SaveDialog(self.listimage,self.classification,self.subclassification,self.comment,title=' ', content=Label(text='POPUP'), size_hint=(None, None),
                      size=(400, 100))
        popup.open()

    def add_comment(self, event):
        popup = CommentDialog(self)
        popup.open()

    def change_scale(self,scale_state,event,):

        self.scale_state=scale_state
        self.update(event)
    def change_colormap(self,colormap,event,):

        self.colormap=colormap
        self.update(event)


    def forward(self,event):
        self.diplaystate=0
        self.counter = self.counter + 1

        if self.counter>self.COUNTER_MAX-1:
            self.counter =self.COUNTER_MAX-1
            popup = Popup(title=' ', content=Label(text='No more images to classify'), size_hint=(None, None),
                          size=(400, 100))
            self.update(event)
            popup.open()
        else:
            self.update(event)

    def backward(self,event):
        self.diplaystate = 0
        self.counter = self.counter - 1
        if self.counter<self.COUNTER_MIN:
            self.counter=self.COUNTER_MIN
            self.update(event)
            popup = Popup(title=' ', content=Label(text='First image'), size_hint=(None, None),
                          size=(400, 100))
            popup.open()
        else:
            self.update(event)
    def change_number(self,event):
        try:
            number=int(self.textnumber.text)
        except ValueError:
            number =self.counter
            popup = Popup(title=' ', content=Label(text='Not an int'), size_hint=(None, None),
                          size=(400, 100))
            popup.open()

        if number < self.COUNTER_MIN:
            popup = Popup(title=' ', content=Label(text='Wrong number'), size_hint=(None, None),
                          size=(400, 100))
            popup.open()
        elif number>self.COUNTER_MAX-1:
            popup = Popup(title=' ', content=Label(text='Wrong number'), size_hint=(None, None),
                          size=(400, 100))
            popup.open()
        else:
            self.counter=number
            self.update(event)

    def open_image_in_ds9(self,pathds9, pathtofile, name):

        os.system(pathds9 + ' ' + pathtofile + name + ' ' + '-zoom 8')
        #os.system(pathds9 + ' ' + '-rgb - red '+pathtofile + name+' \ - green '+pathtofile + name+' \ - blue '+ pathtofile + name)

    def open_ds9(self,event):

        name = self.listimage[self.counter]
        self.open_image_in_ds9(self.pathds9, self.pathtofile, name)

    def classify(self,grade,col,event):
        if col==1:
            self.classification[self.counter] = str(grade)
            self.update_df()
            self.forward(event)
        elif col==2:
            self.subclassification[self.counter] = str(grade)
            self.update_df()

    def get_legacy_survey(self,event):
        s_path = './csv_catalog/'
        sam = glob.glob(s_path + '*.csv')
        if len(sam) == 1:
            sample = pd.read_csv(sam[0])
            ra = sample.iloc[self.counter]['ra']
            dec = sample.iloc[self.counter]['dec']
            savedir = './legacy_survey/'
            url = 'http://legacysurvey.org/viewer/cutout.jpg?ra=' + str(ra) + '&dec=' + str(
                dec) + '&layer=dr8&pixscale=0.06'
            savename = 'N' + str(self.counter)+ '_' + str(ra) + '_' + str(dec) + 'dr8.jpg'
            urllib.request.urlretrieve(url, savedir + savename)
            url = 'http://legacysurvey.org/viewer/cutout.jpg?ra=' + str(ra) + '&dec=' + str(
                dec) + '&layer=dr8-resid&pixscale=0.06'
            savename = 'N' + str(self.counter)+ '_' + str(ra) + '_' + str(dec) + 'dr8-resid.jpg'
            urllib.request.urlretrieve(url, savedir + savename)
            strpopup=savedir+'N' + str(self.counter)+ '_'
            popup=LSDialog(ra,dec,strpopup)
            popup.open()
        if len(sam) == 0:
            popup = Popup(title='Error', content=Label(text='Provide a csv file with ra,dec keywords for all the files in the folder'), size_hint=(None, None),
                          size=(600, 200))
            popup.open()

    def obtain_df(self):
        class_file = np.sort(glob.glob('./classifications/classification_autosave*.csv'))
        print (class_file, len(class_file))
        if len(class_file) >=1:
            print ('loop')
            print('reading '+str(class_file[len(class_file)-1]))
            df = pd.read_csv(class_file[len(class_file)-1])
            self.nf = len(class_file)
            self.classification = df['classification'].tolist()
            self.subclassification = df['subclassification'].tolist()
            self.comment = df['comment'].tolist()

            firstnone=self.classification.index('None')
            self.counter =firstnone


        else:
            df=[]
        if len(df) != len(self.listimage):
            print('creating classification_autosave'+str(len(class_file)+1)+'.csv')
            dfc = ['file_name', 'classification', 'subclassification','comment']
            self.nf = len(class_file) + 1
            df = pd.DataFrame(columns=dfc)
            df['file_name'] = self.listimage
            df['classification'] = self.classification
            df['subclassification'] = self.subclassification
            df['comment'] = self.comment

        return df

    def update_df(self):
        df = self.df
        cnt = self.counter# - 1
        df['file_name'].iloc[cnt] = self.listimage[cnt]
        df['classification'].iloc[cnt] = self.classification[cnt]
        df['subclassification'].iloc[cnt] = self.subclassification[cnt]
        df['comment'].iloc[cnt] = self.comment[cnt]
        print('updating '+'classification_autosave'+str(self.nf)+'.csv file')
        df.to_csv('./classifications/classification_autosave'+str(self.nf)+'.csv', index=False)

    def build(self):
        # Please enter the path of ds9 executable here:
        #self.pathds9 = 'C:\\SAOImageDS9\\ds9.exe'
        os_def = platform.system()
        print(os_def)
        if os_def == 'Linux':
            self.pathds9 = '/usr/local/bin/ds9'
            print('If your DS9 is not in /usr/local/bin/ds9 please edit the right path')
        if os_def == 'Windows': 
            self.pathds9 = 'C:\\SAOImageDS9\\ds9.exe'
            print('If your DS9 is not in C:\\SAOImageDS9\\ds9.exe please edit the right path')
        #this is for mac but don't know the path
        if os_def == 'Darwin':
            self.pathds9 = 'ds9'
            print('Edit the right path to your ds9 executable depending on your OS')
        else :
            print('Edit the right path to your ds9 executable depending on your OS')


        self.pathtofile = './files_to_visualize/'

        self.listimage = sorted([os.path.basename(x) for x in glob.glob(self.pathtofile+ '*.fits')])
        self.counter = 0
        self.number_graded = 0
        self.COUNTER_MIN =0
        self.COUNTER_MAX = len(self.listimage)

        #self.listnames = self.listimage
        self.classification = ['None'] * len(self.listimage)
        self.subclassification = ['None'] * len(self.listimage)
        self.comment = [' '] * len(self.listimage)
        self.scale_min = 0
        self.scale_max = 1
        self.limit_max=1
        self.limit_min = 0
        self.step=(self.scale_max-self.scale_min)/10.
        self.colormap='gray'#'gist_yarg'

        self.scale_state = 'asinh'
        self.diplaystate=0
        self.df = self.obtain_df()
        '''
        self._keyboard = Window.request_keyboard(self,self._keyboard_closed)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        '''



        self.oo = ColoredFigureCanvasKivyAgg(0.0,0.0,0.0,0.0,plt.gcf(),size_hint_x=0.9)

        superBox = BoxLayout(orientation='vertical')

        horizontalBoxup = BoxLayout(orientation='horizontal',size_hint_y=0.1)
        self.tname = Label(text=self.listimage[self.counter], font_size=20, size_hint_y=0.1)

        horizontalBox = BoxLayout(orientation='horizontal')

        #button1 = Button(text="One",size_hint_x=0.1)

        self.slider1 = CustomSlider(orientation='vertical',size_hint_x=0.1,min=self.limit_min, max=self.limit_max, step=self.step,value=self.scale_min)
        self.slider2 = CustomSlider(orientation='vertical', size_hint_x=0.1,min=self.limit_min, max=self.limit_max, step=self.step,value=self.scale_max)
        self.slider1.bind(value = self.min_slider_release)
        self.slider2.bind(value =self.max_slider_release)
        horizontalBox.add_widget(self.slider1)
        horizontalBox.add_widget(self.slider2)
        self.draw_plot(self.scale_state)

        horizontalBox.add_widget(self.oo)

        verticalBox1 = BoxLayout(orientation='horizontal',size_hint_y=0.1)
        verticalBox = BoxLayout(orientation='horizontal', size_hint_y=0.15)

        button3 = Button(text="Sure Lens",background_color=( 0.4,1,0,1))
        button32 = Button(text="Flexion", background_color=(0.4, 1, 0, 1))



        button4 = Button(text="Maybe Lens",background_color=( 0.4,1,0,1))

        button5 = Button(text="Non Lens",background_color=( 0.4,1,0,1))
        button6 = Button(text="Merger")
        button7 = Button(text="Spiral")
        button8 = Button(text="Ring")
        button9 = Button(text="Elliptical")
        button10 = Button(text="Disk")
        button3.bind(on_press=partial(self.classify, 'L',1))
        button32.bind(on_press=partial(self.classify, 'SA', 1))
        button4.bind(on_press=partial(self.classify, 'ML',1))
        button5.bind(on_press=partial(self.classify, 'NL',1))
        button6.bind(on_press=partial(self.classify, 'Merger',2))
        button7.bind(on_press=partial(self.classify, 'Spiral',2))
        button8.bind(on_press=partial(self.classify, 'Ring',2))
        button9.bind(on_press=partial(self.classify, 'Elliptical',2))
        button10.bind(on_press=partial(self.classify, 'Disk',2))


        buttonscale1= Button(text="Linear")
        buttonscale2 = Button(text="Sqrt")
        buttonscale3 = Button(text="Log")
        buttonscale4 = Button(text="Asinh")
        buttoncolormap1= Button(text="Inverted")
        buttoncolormap2 = Button(text="Bb8")
        buttoncolormap3 = Button(text="Gray")
        buttonscale1.bind(on_press=partial(self.change_scale, 'linear'))
        buttonscale2.bind(on_press=partial(self.change_scale, 'sqrt'))
        buttonscale3.bind(on_press=partial(self.change_scale, 'log'))
        buttonscale4.bind(on_press=partial(self.change_scale, 'asinh'))
        buttoncolormap1.bind(on_press=partial(self.change_colormap, 'gist_yarg'))
        buttoncolormap2.bind(on_press=partial(self.change_colormap, 'hot'))
        buttoncolormap3.bind(on_press=partial(self.change_colormap, 'gray'))


        savebutton=Button(text="Save csv",background_color=( 0,1,0.4,1),font_size=25, size_hint_x=0.3)
        savebutton.bind(on_press=self.save_csv)
        commentbutton = Button(text="Comment", background_color=(0, 1, 0.4, 1), font_size=25, size_hint_x=0.3)
        commentbutton.bind(on_press=self.add_comment)
        LSbutton = Button(text="LS", font_size=25, size_hint_x=0.1)
        LSbutton.bind(on_press=self.get_legacy_survey)
        self.textnumber = TextInput(text=str(self.counter), multiline=False,font_size=25, size_hint_x=0.1)
        self.textnumber.bind(on_text_validate=self.change_number)
        self.tclass = Label(text=self.classification[self.counter], font_size=25, size_hint_x=0.1)
        self.tsubclass = Label(text=self.subclassification[self.counter], font_size=25, size_hint_x=0.1)
        tnumber=Label(text=str(' / '+str(self.COUNTER_MAX-1)),font_size=25, size_hint_x=0.1)
        buttonds9 = Button(text="ds9",font_size=25, size_hint_x=0.1)
        buttonds9.bind(on_press=self.open_ds9)

        horizontalBoxup.add_widget(LSbutton)
        horizontalBoxup.add_widget(buttonds9)
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

        bforward=Button(text=" --> ")
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
    BoxLayout_main().run()
