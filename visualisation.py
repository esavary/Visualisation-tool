import math
import numpy as np
import sys
import os
import glob
import astropy.io.fits as pyfits
from astropy.wcs import WCS
if sys.version_info[0] < 3:
    from Tkinter import *
    from tkMessageBox import *
else:
    from tkinter import *
    from tkinter.messagebox import *
import PIL
from PIL import Image, ImageTk, ImageDraw
import matplotlib.pyplot as plt



def logarithm():
    imageData, height, width = numpyarray_from_fits(pathtofile + listimage[counter])

    figure1 = plt.Figure(figsize=(50, 50), dpi=100)
    scale_min = np.amin(imageData)
    scale_max = np.amax(imageData)

    factor = math.log10(scale_max - scale_min)
    indices0 = np.where(imageData < scale_min)
    indices1 = np.where((imageData >= scale_min) & (imageData <= scale_max))
    indices2 = np.where(imageData > scale_max)
    imageData[indices0] = 0.0
    imageData[indices2] = 1.0
    try:
        imageData[indices1] =  np.log10(imageData[indices1]) / (factor*1.0)

        plt.imshow(imageData, cmap='gray')
        plt.axis('off')
        plt.savefig('foolog.png', bbox_inches='tight')

        pilImage = Image.open('foolog.png')
        global photo
        photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

        canvas.create_image(0, 0, image=photo, anchor=NW)
        os.remove('foolog.png')
        fenetre.update_idletasks()
    except:
        print "Error on math.log10 for ", (imageData[i][j] - scale_min)


def linear():
    imageData, height, width = numpyarray_from_fits(pathtofile + listimage[counter])
    figure1 = plt.Figure(figsize=(50, 50), dpi=100)
    scale_min = np.amin(imageData)
    scale_max = np.amax(imageData)
    imageData = imageData.clip(min=scale_min, max=scale_max)
    imageData = (imageData - scale_min) / (scale_max - scale_min)
    indices = np.where(imageData < 0)
    imageData[indices] = 0.0
    indices = np.where(imageData > 1)
    imageData[indices] = 1.0


    plt.imshow(imageData, cmap='gray')
    plt.axis('off')
    plt.savefig('lin.png', bbox_inches='tight')

    pilImage = Image.open('lin.png')
    global photo
    photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

    canvas.create_image(0, 0, image=photo, anchor=NW)
    os.remove('lin.png')
    fenetre.update_idletasks()

def squared():
    imageData, height, width = numpyarray_from_fits(pathtofile + listimage[counter])
    figure1 = plt.Figure(figsize=(50, 50), dpi=100)
    scale_min = np.amin(imageData)
    scale_max = np.amax(imageData)
    imageData = imageData.clip(min=scale_min, max=scale_max)
    imageData = imageData - scale_min
    indices = np.where(imageData < 0)
    imageData[indices] = 0.0
    imageData = np.sqrt(imageData)
    imageData = imageData / math.sqrt(scale_max - scale_min)
    plt.imshow(imageData, cmap='gray')
    plt.axis('off')
    plt.savefig('sqrt.png', bbox_inches='tight')

    pilImage = Image.open('sqrt.png')
    global photo
    photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

    canvas.create_image(0, 0, image=photo, anchor=NW)
    os.remove('sqrt.png')
    fenetre.update_idletasks()

def asinh():
    imageData, height, width = numpyarray_from_fits(pathtofile + listimage[counter])
    figure1 = plt.Figure(figsize=(50, 50), dpi=100)
    scale_min = np.amin(imageData)*1.
    scale_max = np.amax(imageData)*1.
    factor = np.arcsinh((scale_max - scale_min) / 2.0)
    indices0 = np.where(imageData < scale_min)
    indices1 = np.where((imageData >= scale_min) & (imageData <= scale_max))
    indices2 = np.where(imageData > scale_max)
    imageData[indices0] = 0.0
    imageData[indices2] = 1.0
    imageData[indices1] = np.arcsinh((imageData[indices1] - scale_min) / 2.0) / factor
    plt.imshow(imageData, cmap='gray')
    plt.axis('off')
    plt.savefig('sinh.png', bbox_inches='tight')

    pilImage = Image.open('sinh.png')
    global photo
    photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

    canvas.create_image(0, 0, image=photo, anchor=NW)
    os.remove('sinh.png')
    fenetre.update_idletasks()


def alert():
    showinfo("alerte", "Bravo!")

def update_lens():
    global photo
    global counter
    counter = counter + 1
    if counter < COUNTER_MAX:
        listnames.append(listimage[counter][:-5])
        classification.append('1')

        image, height, width = numpyarray_from_fits(pathtofile+listimage[counter])
        figure1 = plt.Figure(figsize=(50, 50), dpi=100)

        plt.imshow(image, cmap='gray')
        plt.axis('off')
        plt.savefig('foo.png', bbox_inches='tight')
        pilImage = Image.open('foo.png')

        photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

        canvas.create_image(0, 0, image=photo, anchor=NW)
        os.remove('foo.png')
        fenetre.update_idletasks()
    else:
        print('No more images to analyse')
        np.savetxt('./classifications/classification_from' +listnames[0] +'to'+listnames[-1]+".csv",
                   np.transpose(np.array([listnames,classification], dtype='S25')), delimiter=",", fmt='%s')
    return
def update_non_lens():
    global photo
    global counter
    counter = counter + 1
    if counter < COUNTER_MAX:
        listnames.append(listimage[counter][:-5])
        classification.append('0')

        image, height, width = numpyarray_from_fits(pathtofile+listimage[counter])
        figure1 = plt.Figure(figsize=(50, 50), dpi=100)

        plt.imshow(image, cmap='gray')
        plt.axis('off')
        plt.savefig('foo.png', bbox_inches='tight')
        pilImage = Image.open('foo.png')

        photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

        canvas.create_image(0, 0, image=photo, anchor=NW)
        os.remove('foo.png')
        fenetre.update_idletasks()

    else:
        print('No more images to analyse')
        np.savetxt('./classifications/classification_from' + listnames[0] + 'to' + listnames[-1] + ".csv",
                   np.transpose(np.array([listnames, classification], dtype='S25')), delimiter=",", fmt='%s')
    return


def numpyarray_from_fits(fits_path,ind_image=0):
    _img = pyfits.open(fits_path)[ind_image].data
    height, width = np.shape(_img)
    return _img,height, width


def save_csv():
    try:
        np.savetxt('./classifications/classification_from' + listnames[0] + 'to' + listnames[-1] + ".csv",
                   np.transpose(np.array([listnames, classification], dtype='S25')), delimiter=",", fmt='%s')

    except IndexError:
        showinfo("Error", "The list is empty")


if __name__ == '__main__':

    pathtofile='./files_to_visualize/'
    listimage=os.listdir(pathtofile)
    counter=0
    COUNTER_MAX=len(listimage)
    image, height, width=numpyarray_from_fits(pathtofile+listimage[0])
    listnames=[]
    classification=[]





    figure1 = plt.Figure(figsize=(50,50), dpi=100)
    plt.imshow(image, cmap='gray')
    plt.axis('off')
    plt.savefig('foo.png', bbox_inches='tight')
    fenetre = Tk()
    canvas=Canvas(fenetre, width=500, height=500, bg='ivory')
    canvas.pack(side=TOP, padx=0, pady=0)
    pilImage = Image.open('foo.png')

    photo = PIL.ImageTk.PhotoImage(image = pilImage.resize((500, 500)))

    canvas.create_image(250, 250, image=photo)
    os.remove('foo.png')
    Button(fenetre,text="LENS", command=update_lens).pack(side=LEFT, padx=60, pady=5)
    Button(fenetre,text="NON LENS", command=update_non_lens).pack(side=RIGHT, padx=60, pady=5)
    menubar = Menu(fenetre)

    menu1 = Menu(menubar, tearoff=0)
    menu1.add_command(label="Log", command=logarithm)
    menu1.add_command(label="Linear", command=linear)
    menu1.add_command(label="Sqrt", command=squared)
    menu1.add_command(label="Asinh", command=asinh)
    menu1.add_separator()
    menubar.add_cascade(label="Change scale", menu=menu1)
    menu2 = Menu(menubar, tearoff=0)
    menu2.add_command(label="Save CSV", command=save_csv)
    menu2.add_separator()
    menubar.add_cascade(label="Save", menu=menu2)
    fenetre.config(menu=menubar)
    fenetre.mainloop()
