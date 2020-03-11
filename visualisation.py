import math
import numpy as np
import sys
import os
import glob
import subprocess
import astropy.io.fits as pyfits
from astropy.wcs import WCS
from astropy.visualization import make_lupton_rgb
import matplotlib
if sys.version_info[0] < 3:
    from Tkinter import *
    from tkMessageBox import *
else:
    from tkinter import *
    from tkinter.messagebox import *
import PIL
from PIL import Image, ImageTk, ImageDraw
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.visualization import lupton_rgb
from astropy.io import fits

#############################################################################################
#Please enter the path of ds9 executable here:
#pathds9 = 'C:\\SAOImageDS9\\ds9.exe'
pathds9 = '/usr/local/bin/ds9'

#############################################################################################


def changemin_max():
    global scale_min
    global scale_max
    try:
        scale_min=float(minzone.get())
        scale_max =float(maxzone.get())
    except ValueError:
        showinfo("Error", "Bad values")
    if scale_min>=scale_max:
        showinfo("Error", "Bad values")

    if scale_state=='linear':
        linear()
    elif scale_state=='squared':
        squared()
    elif scale_state=='lupton':
        showinfo("Error", "Not available with lupton RGB")
    elif scale_state=='asinh':
        asinh()
    elif scale_state=='log':
        logarithm()
    else:
        print ('unknown scale')

def background_rms_image(cb,image):
    xg,yg = np.shape(image)
    cut0  = image[0:cb,0:cb]
    cut1  = image[xg-cb:xg,0:cb]
    cut2  = image[0:cb,yg-cb:yg]
    cut3  = image[xg-cb:xg,yg-cb:yg]
    std   = np.std([cut0,cut1,cut2,cut3])
    return std

#def showplot_rgb(rimage,gimage,bimage):
#    bgr = background_rms_image(8,rimage)
#    bgg = background_rms_image(8,gimage)
#    bgb = background_rms_image(8,bimage)
#    map = lupton_rgb.AsinhZScaleMapping(rimage, gimage, bimage,pedestal=[bgr,bgg,bgb],Q=5)
#    color_image = map.make_rgb_image(rimage, gimage, bimage)
#    return color_image


def sqrt_sc(inputArray, scale_min=None, scale_max=None):
    #this definition was taken from lenstronomy
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

def scale_val(image_array):
    if len(np.shape(image_array)) == 2:
        image_array = [image_array]
    vmin = np.min([background_rms_image(5,image_array[i]) for i in range(len(image_array))])
    xl,yl=np.shape(image_array[0])
    box_size = 14 #in pixel
    xmin = int((xl)/2-(box_size/2))
    xmax = int((xl)/2+(box_size/2))
    vmax = np.max([image_array[i][xmin:xmax,xmin:xmax] for i in range(len(image_array))])
    return vmin,vmax

def showplot_rgb(rimage,gimage,bimage):
    vmin,vmax=scale_val([rimage,gimage,bimage])
    img = np.zeros((rimage.shape[0], rimage.shape[1], 3), dtype=float)
    img[:,:,0] = sqrt_sc(rimage, scale_min=vmin, scale_max=vmax)
    img[:,:,1] = sqrt_sc(gimage, scale_min=vmin, scale_max=vmax)
    img[:,:,2] = sqrt_sc(bimage, scale_min=vmin, scale_max=vmax)
    return img



def new_window1():
    global win1
    global histo
    global pilImage2
    global minzone
    global maxzone

    try:
        if win1.state() == "normal": win1.focus()
    except:
        imageData, height, width = numpyarray_from_fits(pathtofile + listimage[counter])
        flat=imageData.flatten()

        figure1 = plt.Figure(figsize=(500, 350), dpi=500)
        counts, bins = np.histogram(flat)
        plt.style.use('dark_background')
        plt.hist(bins[:-1], bins, weights=counts)
        plt.savefig('histo.png', bbox_inches='tight')
        pilImage2 = Image.open('histo.png')
        plt.close()
        histo = PIL.ImageTk.PhotoImage(image=pilImage2)#.resize((500, 400)))

        win1 = Toplevel()
        #win1.geometry("300x300+500+200")
        win1["bg"] = 'black'

        canvas2 = Canvas(win1, width=580, height=430, bg='black')
        canvas2.pack(side=TOP, padx=0, pady=0)
        canvas2.create_image(0, 0, image=histo, anchor=NW)
        os.remove('histo.png')
        ButtonOK = Button(win1, text="      OK      ", command=changemin_max)
        ButtonOK.pack(side=BOTTOM, padx=40, pady=2)
        minzone = Entry(win1, width=15)
        minzone.insert(0, "min value")


        minzone.pack(side=LEFT, padx=20, pady=10)
        maxzone = Entry(win1, width=15)
        maxzone.insert(0, "max value")
        maxzone.pack(side=RIGHT, padx=20, pady=10)
        win1.update_idletasks()

def logarithm():
    global scale_state
    scale_state = 'log'

    imageData, height, width = numpyarray_from_fits(pathtofile + listimage[counter])

    figure1 = plt.Figure(figsize=(50, 50), dpi=100)
    #scale_min = np.amin(imageData)
    #scale_max = np.amax(imageData)

    factor = math.log10(scale_max - scale_min)
    indices0 = np.where(imageData < scale_min)
    indices1 = np.where((imageData >= scale_min) & (imageData <= scale_max))
    indices2 = np.where(imageData > scale_max)
    imageData[indices0] = 0.0
    imageData[indices2] = 1.0
    try:
        imageData[indices1] =  np.log10(imageData[indices1]) / (factor*1.0)

        plt.imshow(imageData, cmap='gray', origin='lower')
        plt.axis('off')
        plt.savefig('foolog.png', bbox_inches='tight')
        plt.close()
        pilImage = Image.open('foolog.png')
        global photo
        photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

        canvas.create_image(0, 0, image=photo, anchor=NW)
        os.remove('foolog.png')
        fenetre.update_idletasks()
    except:
        print ("Error on math.log10 for ", (imageData[i][j] - scale_min))


def linear():
    global scale_state
    scale_state='linear'
    imageData, height, width = numpyarray_from_fits(pathtofile + listimage[counter])
    figure1 = plt.Figure(figsize=(50, 50), dpi=100)
    #scale_min = np.amin(imageData)
    #scale_max = np.amax(imageData)
    imageData = imageData.clip(min=scale_min, max=scale_max)
    imageData = (imageData - scale_min) / (scale_max - scale_min)
    indices = np.where(imageData < 0)
    imageData[indices] = 0.0
    indices = np.where(imageData > 1)
    imageData[indices] = 1.0


    plt.imshow(imageData, cmap='gray', origin='lower')
    plt.axis('off')
    plt.savefig('lin.png', bbox_inches='tight')
    plt.close()

    pilImage = Image.open('lin.png')
    global photo
    photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

    canvas.create_image(0, 0, image=photo, anchor=NW)
    os.remove('lin.png')
    fenetre.update_idletasks()

def open_image_in_ds9(pathds9,pathtofile,name):

    p=subprocess.Popen([pathds9, pathtofile+name])
    returncode = p.wait()

def open_ds9():

    name=listimage[counter]
    open_image_in_ds9(pathds9, pathtofile, name)

def squared():
    global scale_state
    scale_state='squared'
    imageData, height, width = numpyarray_from_fits(pathtofile + listimage[counter])
    figure1 = plt.Figure(figsize=(50, 50), dpi=100)
    #scale_min = np.amin(imageData)
    #scale_max = np.amax(imageData)
    imageData = imageData.clip(min=scale_min, max=scale_max)
    imageData = imageData - scale_min
    indices = np.where(imageData < 0)
    imageData[indices] = 0.0
    imageData = np.sqrt(imageData)
    imageData = imageData / math.sqrt(scale_max - scale_min)
    plt.imshow(imageData, cmap='gray', origin='lower')
    plt.axis('off')
    plt.savefig('sqrt.png', bbox_inches='tight')
    plt.close()

    pilImage = Image.open('sqrt.png')
    global photo
    photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

    canvas.create_image(0, 0, image=photo, anchor=NW)
    os.remove('sqrt.png')
    fenetre.update_idletasks()

def asinh():
    global scale_state
    scale_state='asinh'
    imageData, height, width = numpyarray_from_fits(pathtofile + listimage[counter])
    figure1 = plt.Figure(figsize=(50, 50), dpi=100)
    #scale_min = np.amin(imageData)*1.
    #scale_max = np.amax(imageData)*1.
    factor = np.arcsinh((scale_max - scale_min) / 2.0)
    indices0 = np.where(imageData < scale_min)
    indices1 = np.where((imageData >= scale_min) & (imageData <= scale_max))
    indices2 = np.where(imageData > scale_max)
    imageData[indices0] = 0.0
    imageData[indices2] = 1.0
    imageData[indices1] = np.arcsinh((imageData[indices1] - scale_min) / 2.0) / factor
    plt.imshow(imageData, cmap='gray', origin='lower')
    plt.axis('off')
    plt.savefig('sinh.png', bbox_inches='tight')
    plt.close()

    pilImage = Image.open('sinh.png')
    global photo
    photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

    canvas.create_image(0, 0, image=photo, anchor=NW)
    os.remove('sinh.png')
    fenetre.update_idletasks()


def previous_next(timesignal):
    global photo
    global counter
    global scale_min
    global scale_max

    if timesignal=='past':
        if counter-1<0:
            showinfo("Error", "This is the first image")
        else:
            counter=counter-1
            image, height, width = numpyarray_from_fits(pathtofile + listimage[counter])
            scale_min = np.amin(image)
            scale_max = np.amax(image)
            figure1 = plt.Figure(figsize=(50, 50), dpi=100)

            if scale_state == 'squared':
                squared()

            elif scale_state == 'asinh':
                asinh()
            elif scale_state == 'log':
                logarithm()
            else:

                plt.imshow(image, cmap='gray', origin='lower')
                plt.axis('off')
                plt.savefig('foo.png', bbox_inches='tight')
                plt.close()
                pilImage = Image.open('foo.png')

                photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

                canvas.create_image(0, 0, image=photo, anchor=NW)
                os.remove('foo.png')
                fenetre.update_idletasks()
    else:
        if counter+1<=number_graded:
            counter=counter+1
            image, height, width = numpyarray_from_fits(pathtofile + listimage[counter])
            scale_min = np.amin(image)
            scale_max = np.amax(image)
            figure1 = plt.Figure(figsize=(50, 50), dpi=100)
            if scale_state == 'squared':
                squared()

            elif scale_state == 'asinh':
                asinh()
            elif scale_state == 'log':
                logarithm()
            else:
                plt.imshow(image, cmap='gray', origin='lower')
                plt.axis('off')
                plt.savefig('foo.png', bbox_inches='tight')
                plt.close()
                pilImage = Image.open('foo.png')

                photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

                canvas.create_image(0, 0, image=photo, anchor=NW)
                os.remove('foo.png')
                fenetre.update_idletasks()
        else:
            showinfo("Error", "Please grade this image first!")






def update_lens(grade):
    global photo
    global counter
    global number_graded
    global scale_min
    global scale_max

    if counter < COUNTER_MAX:
        listnames[counter] = listimage[counter][:-5]
        classification[counter] = str(grade)
        number_graded=number_graded+1
        counter = counter + 1
        if counter==COUNTER_MAX:
            image, height, width = numpyarray_from_fits(pathtofile + listimage[counter-1])
            scale_min = np.amin(image)
            scale_max = np.amax(image)
            figure1 = plt.Figure(figsize=(50, 50), dpi=100)

            if scale_state == 'squared':
                squared()

            elif scale_state == 'asinh':
                asinh()
            elif scale_state == 'log':
                logarithm()

            else:
                plt.imshow(image, cmap='gray', origin='lower')
                plt.axis('off')
                plt.savefig('foo.png', bbox_inches='tight')
                plt.close()
                pilImage = Image.open('foo.png')

                photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

                canvas.create_image(0, 0, image=photo, anchor=NW)
                os.remove('foo.png')
                fenetre.update_idletasks()
        else:
            image, height, width = numpyarray_from_fits(pathtofile+listimage[counter])
            scale_min = np.amin(image)
            scale_max = np.amax(image)
            figure1 = plt.Figure(figsize=(50, 50), dpi=100)

            if scale_state == 'squared':
                squared()

            elif scale_state == 'asinh':
                asinh()
            elif scale_state == 'log':
                logarithm()

            else:
                plt.imshow(image, cmap='gray', origin='lower')
                plt.axis('off')
                plt.savefig('foo.png', bbox_inches='tight')
                plt.close()
                pilImage = Image.open('foo.png')

                photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

                canvas.create_image(0, 0, image=photo, anchor=NW)
                os.remove('foo.png')
                fenetre.update_idletasks()
    else:
        showinfo("Error", 'No more images to analyse')
        np.savetxt('./classifications/classification_from' +listnames[0] +'to'+listnames[-1]+".csv",
                   np.transpose(np.array([listnames, classification], dtype='U40')), delimiter=",", fmt='%s')
    return



def numpyarray_from_fits(fits_path,ind_image=0,color=False):
    _img = pyfits.open(fits_path)[ind_image].data
    try:
        height, width = np.shape(_img)
        return _img,height, width
    except ValueError:
        n,height,width= np.shape(_img)
        if color==True:
            return _img[0],_img[1],_img[2],height,width
        else:
            return _img[0],height,width



def save_csv():
    if counter==0:
        showinfo("Error", "Empty list")
    else:
        np.savetxt('./classifications/classification_from' + listnames[0] + 'to' + listnames[counter] + ".csv",
                   np.transpose(np.array([listnames[0:counter], classification[0:counter]], dtype='U40')), delimiter=",", fmt='%s')


def open_lupton():
    global scale_state
    try:
        #image_R, image_G,image_B ,height, width = numpyarray_from_fits(pathtofile + listimage[counter],color=True)
        image_B, image_G,image_R=[fits.open(pathtofile + listimage[counter])[0].data,fits.open(pathtofile + listimage[counter])[1].data,fits.open(pathtofile + listimage[counter])[2].data]
        image =showplot_rgb(image_R,image_G,image_B)
        plt.imshow(image, origin='lower')
        plt.axis('off')
        plt.savefig('lupton.png', bbox_inches='tight')
        plt.close()

        pilImage = Image.open('lupton.png')
        global photo
        photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

        canvas.create_image(0, 0, image=photo, anchor=NW)
        os.remove('lupton.png')
        scale_state='lupton'
        fenetre.update_idletasks()
    except ValueError:

        showinfo("Error", "Not a color image")


if __name__ == '__main__':

    pathtofile='./files_to_visualize/'
    listimage=sorted(os.listdir(pathtofile))
    counter=0
    number_graded=0
    COUNTER_MAX=len(listimage)
    image, height, width=numpyarray_from_fits(pathtofile+listimage[0])
    listnames=['None'] * len(listimage)
    classification=['None'] * len(listimage)
    scale_min = np.amin(image)
    scale_max = np.amax(image)
    scale_state='linear'



    figure1 = plt.Figure(figsize=(50,50), dpi=100)
    plt.imshow(image, cmap='gray', origin='lower')
    plt.axis('off')
    plt.savefig('foo.png', bbox_inches='tight')
    plt.close()
    fenetre = Tk()
    canvas=Canvas(fenetre, width=500, height=500, bg='ivory')
    canvas.pack(side=TOP, padx=0, pady=0)
    pilImage = Image.open('foo.png')

    photo = PIL.ImageTk.PhotoImage(image = pilImage.resize((500, 500)))

    canvas.create_image(250, 250, image=photo)
    os.remove('foo.png')
    Button(fenetre,text="  3  ", command= lambda:update_lens(3)).pack(side=LEFT, padx=60, pady=5)
    Button(fenetre,text="  2  ", command=lambda:update_lens(2)).pack(side=LEFT, padx=60, pady=5)
    Button(fenetre, text="  1  ", command=lambda:update_lens(1)).pack(side=LEFT, padx=60, pady=5)
    Button(fenetre, text="  0  ", command=lambda:update_lens(0)).pack(side=LEFT, padx=60, pady=5)
    menubar = Menu(fenetre)

    menu1 = Menu(menubar, tearoff=0)
    menu1.add_command(label="Log", command=logarithm)
    menu1.add_command(label="Linear", command=linear)
    menu1.add_command(label="Sqrt", command=squared)
    menu1.add_command(label="Asinh", command=asinh)
    menu1.add_command(label="Histogram", command=new_window1)
    menu1.add_command(label="Lupton RGB", command=open_lupton)
    menu1.add_separator()
    menubar.add_cascade(label="Change scale", menu=menu1)
    menu2 = Menu(menubar, tearoff=0)
    menu2.add_command(label="Save CSV", command=save_csv)
    menu2.add_separator()
    menubar.add_cascade(label="Save", menu=menu2)
    menu4 = Menu(menubar, tearoff=0)
    menu4.add_command(label="Backward", command= lambda: previous_next('past'))
    menu4.add_separator()
    menu4.add_command(label="Forward", command=lambda: previous_next('future'))
    menu4.add_separator()
    menubar.add_cascade(label="Change image", menu=menu4)
    menu5 = Menu(menubar, tearoff=0)
    menu5.add_command(label="ds9", command=open_ds9)
    menu5.add_separator()
    menubar.add_cascade(label="Open with an external software", menu=menu5)
    fenetre.config(menu=menubar)
    fenetre.mainloop()
