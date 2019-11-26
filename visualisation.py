import math
import numpy as np
import sys
import os
import glob
import astropy.io.fits as pyfits
from astropy.wcs import WCS
from astropy.visualization import make_lupton_rgb

if sys.version_info[0] < 3:
    from Tkinter import *
    from tkMessageBox import *
else:
    from tkinter import *
    from tkinter.messagebox import *
import PIL
from PIL import Image, ImageTk, ImageDraw
import matplotlib.pyplot as plt
from astropy.visualization import lupton_rgb

def showplot_rgb(rimage,gimage,bimage):
    mr=max(rimage.flatten())
    mg=max(gimage.flatten())
    mb=max(bimage.flatten())
    minval = min(min((rimage/mr).flatten()),min((gimage/mg).flatten()),min((bimage/mb).flatten()))
    maxval = max(max((rimage/mr).flatten()),max((gimage/mg).flatten()),max((bimage/mb).flatten()))
    map = lupton_rgb.AsinhZScaleMapping(rimage, gimage, bimage)
    color_image = map.make_rgb_image(rimage, gimage, bimage)
    return color_image




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
        print ("Error on math.log10 for ", (imageData[i][j] - scale_min))


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


def previous_next(timesignal):
    global photo
    global counter
    if timesignal=='past':
        if counter-1<0:
            showinfo("Error", "This is the first image")
        else:
            counter=counter-1
            image, height, width = numpyarray_from_fits(pathtofile + listimage[counter])
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
        if counter+1<=number_graded:
            counter=counter+1
            image, height, width = numpyarray_from_fits(pathtofile + listimage[counter])
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
            showinfo("Error", "Please grade this image first!")






def update_lens(grade):
    global photo
    global counter
    global number_graded

    if counter < COUNTER_MAX:
        listnames[counter] = listimage[counter][:-5]
        classification[counter] = str(grade)
        number_graded=number_graded+1
        counter = counter + 1
        if counter==COUNTER_MAX:
            image, height, width = numpyarray_from_fits(pathtofile + listimage[counter-1])
        else:
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
        showinfo("Error", 'No more images to analyse')
        np.savetxt('./classifications/classification_from' +listnames[0] +'to'+listnames[-1]+".csv",
                   np.transpose(np.array([listnames, classification], dtype='U25')), delimiter=",", fmt='%s')
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
                   np.transpose(np.array([listnames[0:counter], classification[0:counter]], dtype='U25')), delimiter=",", fmt='%s')


def open_lupton():
    try:
        image_R, image_G,image_B ,height, width = numpyarray_from_fits(pathtofile + listimage[counter],color=True)
        image =showplot_rgb(image_R,image_G,image_B)
        plt.imshow(image)
        plt.axis('off')
        plt.savefig('lupton.png', bbox_inches='tight')

        pilImage = Image.open('lupton.png')
        global photo
        photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

        canvas.create_image(0, 0, image=photo, anchor=NW)
        os.remove('lupton.png')
        fenetre.update_idletasks()
    except ValueError:

        showinfo("Error", "Not a color image")


if __name__ == '__main__':

    pathtofile='./files_to_visualize/'
    listimage=os.listdir(pathtofile)
    counter=0
    number_graded=0
    COUNTER_MAX=len(listimage)
    image, height, width=numpyarray_from_fits(pathtofile+listimage[0])
    listnames=['None'] * len(listimage)
    classification=['None'] * len(listimage)





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
    menu1.add_separator()
    menubar.add_cascade(label="Change scale", menu=menu1)
    menu2 = Menu(menubar, tearoff=0)
    menu2.add_command(label="Save CSV", command=save_csv)
    menu2.add_separator()
    menubar.add_cascade(label="Save", menu=menu2)
    menu3 = Menu(menubar, tearoff=0)
    menu3.add_command(label="Lupton RGB", command=open_lupton)
    menu3.add_separator()
    menubar.add_cascade(label="Open as color image", menu=menu3)
    menu4 = Menu(menubar, tearoff=0)
    menu4.add_command(label="Backward", command= lambda: previous_next('past'))
    menu4.add_separator()
    menu4.add_command(label="Forward", command=lambda: previous_next('future'))
    menu4.add_separator()
    menubar.add_cascade(label="Change image", menu=menu4)
    fenetre.config(menu=menubar)
    fenetre.mainloop()

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
        print ("Error on math.log10 for ", (imageData[i][j] - scale_min))


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

def update_lens(grade):
    global photo
    global counter
    counter = counter + 1
    if counter < COUNTER_MAX:
        listnames.append(listimage[counter][:-5])
        classification.append(str(grade))

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
                   np.transpose(np.array([listnames,classification], dtype='U25')), delimiter=",", fmt='%s')
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
    try:
        np.savetxt('./classifications/classification_from' + listnames[0] + 'to' + listnames[-1] + ".csv",
                   np.transpose(np.array([listnames, classification], dtype='U25')), delimiter=",", fmt='%s')

    except IndexError:
        showinfo("Error", "The list is empty")
def open_lupton():
    try:
        image_R, image_G,image_B ,height, width = numpyarray_from_fits(pathtofile + listimage[counter],color=True)
        image =showplot_rgb(image_R,image_G,image_B)
        plt.imshow(image)
        plt.axis('off')
        plt.savefig('lupton.png', bbox_inches='tight')

        pilImage = Image.open('lupton.png')
        global photo
        photo = PIL.ImageTk.PhotoImage(image=pilImage.resize((500, 500)))

        canvas.create_image(0, 0, image=photo, anchor=NW)
        os.remove('lupton.png')
        fenetre.update_idletasks()
    except ValueError:

        showinfo("Error", "Not a color image")


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
    Button(fenetre,text="  3  ", command= lambda:update_lens(3)).pack(side=LEFT, padx=60, pady=5)
    Button(fenetre,text="  2  ", command=lambda:update_lens(2)).pack(side=LEFT, padx=60, pady=5)
    Button(fenetre, text="  1  ", command=lambda:update_lens(1)).pack(side=LEFT, padx=60, pady=5)
    Button(fenetre, text="  0  ", command=update_non_lens).pack(side=LEFT, padx=60, pady=5)
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
    menu3 = Menu(menubar, tearoff=0)
    menu3.add_command(label="Lupton RGB", command=open_lupton)
    menu3.add_separator()
    menubar.add_cascade(label="Open as color image", menu=menu3)
    fenetre.config(menu=menubar)
    fenetre.mainloop()
