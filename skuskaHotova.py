from matplotlib import pyplot as plt
from matplotlib.widgets import Button, TextBox
import tkinter as tk
from tkinter import filedialog
import pydicom 
import numpy as np
import pathlib
from PIL import Image
import pandas as pd

class DICOMViewer(object):
    ind=0    
    def __init__(self, show=True):
		
		#
        self.fig, self.ax = plt.subplots()
        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])
        plt.subplots_adjust(bottom=0.2)
        self.canvas = self.fig.canvas
		
		
        drawColor = "r"
		
        self.rectDrawer = RectDrawer(self, drawColor)
	
        self.currentDrawer = None
		
		
        self.buttons = {"open image file": self.openDICOMFile,
                        "Anotate": self.rectDrawer,
						"Save anotations": self.saveAnnotationsToFile,
                        "Generate anotations as picture":self.MakeAnotedFile
                        } 
		
        self.makeGUIButtons()
		 
        self.shortcutKeyMap = {	"ctrl+o": "open image file", 
                         "ctrl+a": "anotuj", 
                         "+": "uloz"}
		
        self.canvas.mpl_connect('key_press_event', self.keyPress)
		
        self.annotationFile = None
        self.dicomFile = None
		
        if show:
            plt.show()
	
    def makeGUIButtons(self):
		
		
        buttonPosX = 0.25
        self.buttonObjects = []
        for buttonText in self.buttons:
			
			
            bLen = 0.05*(len(buttonText)-4)/(6.0)+0.1
			
            axButton = plt.axes([buttonPosX, 0.05, bLen, 0.075])
            button = Button(axButton, buttonText)
            buttonCallback = self.buttons[buttonText]
            button.on_clicked(buttonCallback)
            self.buttonObjects.append(button)
            buttonPosX += bLen+0.01
            
       
            
    
    def buttonMulltyDicom(self,event):
        axprev = plt.axes([0.1, 0.5, 0.1, 0.075])
        axnext = plt.axes([0.83, 0.5, 0.1, 0.075])
        self.bnext = Button(axnext, 'next')
        self.bnext.on_clicked(self.dalsi)
        self.buttonObjects.append(self.bnext)
        self.bprev = Button(axprev, 'back')
        self.bprev.on_clicked(self.predosli)
        self.buttonObjects.append(self.bprev)
    
    def actualS(self,actual,maxS):
        
        text=actual+1,"/",maxS+1
        bLen = 0.15*(len(text)-1)/(6.0)+0.1
        axbox = plt.axes([0.45, 0.14, bLen, 0.055])
        self.text_box = TextBox(axbox,'',text)
        plt.show()
        
   
    def openDICOMFile(self, event):
        
		
        self.dicomFile = self.openDICOMFileDialog()
        

        if not self.dicomFile: 
            return
		
        if True in [self.dicomFile.endswith(ext) for ext in [".png", ".jpg", "bmp"]]:
            img = plt.imread(self.dicomFile)
        else:	
		
            try: 
                self.ds = pydicom.read_file(self.dicomFile)
                img1 = self.ds.pixel_array.imag
                global k
                global arrayMax
                
                
                k=1
                if img1.ndim == 2:
                    img = img1
                    axprev = plt.axes([0.1, 0.5, 0.1, 0.075])
                    axnext = plt.axes([0.83, 0.5, 0.1, 0.075])
                    self.bnext = Button(axnext, 'next')
                    self.bprev = Button(axprev, 'back')
                    DICOMViewer.actualS(self, 0, 0)
                    
                elif img1.ndim == 3:
                    arrayMax=len(img1.T)
                    img = img1[k,:,:]
                    DICOMViewer.buttonMulltyDicom(self,event)
                    DICOMViewer.actualS(self, self.ind, arrayMax)
                   
                    
            except pydicom.filereader.InvalidDicomError:
                print ("error, file not a DICOM file")
                return
		
        self.ax.imshow(img, interpolation="nearest", cmap=plt.gray())
		
        self.ax.set_xlim(self.ax.get_xlim())
        self.ax.set_ylim(self.ax.get_ylim())
		
        
        return self.ds
        
    def openDICOMFileDialog(self):
		
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename()
        root.destroy()

        return path


    def uloz(self,data):
        
        self.rectDrawer.objectData.append(data)
        print(self.rectDrawer.objectData)
        
		
        for line in self.rectDrawer.currentLine:
            line.set_animated(False)
			
            self.background = None
            self.canvas.draw()
   
    def dalsi(self,event):
        
        self.ind += 10
        if self.ind>=arrayMax:
            self.ind=arrayMax
        
        self.ax.clear()
        plt.show()
        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])
        img=self.ds.pixel_array
        self.ax.imshow(img[self.ind,:,:], interpolation="nearest", cmap=plt.gray())
		
        self.ax.set_xlim(self.ax.get_xlim())
        self.ax.set_ylim(self.ax.get_ylim())
		
        DICOMViewer.actualS(self, self.ind, arrayMax)
    def predosli(self,event):
        self.ind -= 1
        if self.ind<=0:
           self.ind=0
        self.ax.clear()
        plt.show()
        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])
        img=self.ds.pixel_array
        self.ax.imshow(img[self.ind,:,:], interpolation="nearest", cmap=plt.gray())
		
        self.ax.set_xlim(self.ax.get_xlim())
        self.ax.set_ylim(self.ax.get_ylim())
		
        DICOMViewer.actualS(self, self.ind, arrayMax)
        
    def keyPress(self, event):
		
        key = event.key
		
        if not key in self.shortcutKeyMap: 
            if not self.currentDrawer:
                return
			
            self.currentDrawer.handleKey(key) 
        if self.shortcutKeyMap[key]=="uloz":
            
            self.uloz(rdata)
       
        else: 
			
            drawerName = self.shortcutKeyMap[key]
            print(drawerName)
            self.buttons[drawerName](self)
	
    def saveAnnotationsToFile(self, event):
        
       
        
        self.annotationFile = self.dicomFile+"_"+str(self.ind+1)+ "_annotations.txt"
        
		
        if self.dicomFile == None: 
			
            return
		
		
        if self.currentDrawer:
            self.currentDrawer._disconnect()
		
		
        ln ="x0: {x0}, y0: {y0}, x1: {x1}, y1: {y1}"
		
        with open(self.annotationFile, "w") as fh:
			
			
            for drawerName in self.buttons:
				
                drawerObject = self.buttons[drawerName]
				
                if not hasattr(drawerObject, "objectData"):
                    continue
				
                for dataObject in drawerObject.objectData:
                    dataObject["objectType"] = drawerName
                    textToPrint = ln.format(**dataObject) + "\n"
                    fh.write(textToPrint)
            self.rectDrawer.objectData=[]
    def MakeAnotedFile(self, fileName):
        Help=[]
        x0=[]
        y0=[]
        x1=[]
        y1=[]
        lines=[]
        FinalData=[]
        Suradnica=[]
        
        self.border=[]
        
        self.Lastano = self.openDICOMFileDialog()
        
        try:
            a=int(self.Lastano.split("/")[-1].split(".")[0])
        except:
            a=0
        for poctS in range(arrayMax):
            self.AnoFile = self.dicomFile+"_"+str(poctS+1)+ "_annotations.txt"
            file = pathlib.Path(self.AnoFile)
            if file.exists ():
                with open (self.AnoFile, 'rt') as myfile: 
                    
                    for i,line in enumerate(myfile) : 
                        
                        k=line.split()
                        
                        lines.append(k)
                        
                
                i=0
                while i<len(lines):
                    
                    for k in lines[i]:
                        
                        
                        if k=='x0:':
                            Suradnica='x0'
                            continue
                        if k=='y0:':
                            Suradnica='y0'
                            continue
                        if k=='x1:':
                            Suradnica='x1'
                            continue
                        if k=='y1:':
                            Suradnica='y1'
                            continue
                        
                        
                        if Suradnica=='x0':
                            for cislo in k :
                                if cislo!=',':
                                    Help.append(cislo)
                            Help[:]=["".join(Help[:])]     
                            x0=Help
                            Help=[]
                            
                            continue
                        
                        
                        if Suradnica=='y0':
                            for cislo in k :
                                if cislo!=',':
                                    Help.append(cislo)
                            Help[:]=["".join(Help[:])]     
                            y0=Help
                            Help=[]
                            continue
                        
                        
                        if Suradnica=='x1':
                            for cislo in k :
                                if cislo!=',':
                                    Help.append(cislo)
                            Help[:]=["".join(Help[:])]     
                            x1=Help
                            Help=[]
                            continue
                        
                        
                        if Suradnica=='y1':
                            for cislo in k :
                                if cislo!=',':
                                    Help.append(cislo)
                                cislo=[]
                            Help[:]=["".join(Help[:])]   
                            y1=Help
                            Help=[]
                        
                        wholeX0,_ = map(int,x0[0].split("."))
                        wholeX1,_ = map(int,x1[0].split("."))
                        wholeY0,_ = map(int,y0[0].split("."))
                        wholeY1,_ = map(int,y1[0].split("."))
                        FinalData=self.ds.pixel_array[poctS,wholeX0:wholeX1,wholeY0:wholeY1]
                        Suradnice=[wholeX0,wholeX1,wholeY0,wholeY1]
                        a+=1
                        #np.save("C:\\Users\\adams\\Desktop\\Aneurism\\"+str(a)+'.npy', FinalData, allow_pickle=True)
                        new_image = self.ds.pixel_array[poctS].astype(float)
                        scaled_image = (np.maximum(new_image, 0) / new_image.max()) * 255.0
                        scaled_image = np.uint8(scaled_image)
                        final_image = Image.fromarray(scaled_image)
                        final_image.save("C:\\Users\\adams\\Desktop\\Aneurism\\"+str(a)+'.png')
                        df = pd.DataFrame(Suradnice)
                        #df.to_excel("C:\\Users\\adams\\Desktop\\Aneurism\\"+str(a)+'.xlsx', index = False)
                        i+=1
                lines=[]  
        
class DrawerObject(object):
    def __init__(self, viewer, color):
        self.viewer = viewer
        self.fig = viewer.fig
        self.ax = viewer.ax
        self.canvas = self.fig.canvas
        self.color = color
        self.objectData = []
        self.currentLine = None
        self.currentText = None
        self.background = None
        self.keyPressed = False
        self.x0 = None
        self.y0 = None 
        self.cmlp = None 
        self.cmm = None 
        self.cmlr = None 
        
        
    def __call__(self, event=None):
		
		
        if self.viewer.currentDrawer != None:
            self.viewer.currentDrawer._disconnect()
		
        self.viewer.currentDrawer = self
		
		
        self.cmlp = self.canvas.mpl_connect('button_press_event', self.mouseLeftPress)
        self.cmm = self.canvas.mpl_connect('motion_notify_event', self.mouseMove)
        self.cmlr = self.canvas.mpl_connect('button_release_event', self.mouseLeftRelease)
        
	
    def _disconnect(self):
		
        self.canvas.mpl_disconnect(self.cmlp)
        self.canvas.mpl_disconnect(self.cmm)
        self.canvas.mpl_disconnect(self.cmlr)
     
	
	
    def mouseLeftPress(self, event):
        pass
	
    def mouseMove(self, event):
        pass
	
    def mouseLeftRelease(self, event):
        pass
	
    def handleKey(self, key):
        pass
	
class RectDrawer(DrawerObject):
	
    def mouseLeftPress(self, event):
		
        if event.inaxes!=self.ax: return 
        self.keyPressed = True
		
        self.x0 = event.xdata
        self.y0 = event.ydata
    		
        line1, = self.ax.plot([self.x0], [self.y0], self.color)
        line2, = self.ax.plot([self.x0], [self.y0], self.color)
        line3, = self.ax.plot([self.x0], [self.y0], self.color)
        line4, = self.ax.plot([self.x0], [self.y0], self.color)
    		
        self.currentLine = [line1, line2, line3, line4]
		
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
		
        for line in self.currentLine:
            line.set_animated(True)
            self.ax.draw_artist(line)
            self.canvas.blit(self.ax.bbox)

    def mouseMove(self, event):
		
        if event.inaxes!=self.ax: return 
        if not self.keyPressed: return 
		
        x = event.xdata
        y = event.ydata
		
        line1, line2, line3, line4 = self.currentLine
		
        self.canvas.restore_region(self.background)
		
		
        line1.set_data([self.x0, x], [self.y0, self.y0])
        self.ax.draw_artist(line1)
		
        line2.set_data([x, x], [self.y0, y])
        self.ax.draw_artist(line2)
        line3.set_data([x, self.x0], [y, y])
        self.ax.draw_artist(line3)
		
        line4.set_data([self.x0, self.x0], [y, self.y0])
        self.ax.draw_artist(line4)
		
        self.canvas.blit(self.ax.bbox)
	
    def mouseLeftRelease(self, event):
		
        if event.inaxes!=self.ax: return 
        self.keyPressed = False
		
        x = event.xdata
        y = event.ydata
        global rdata
        rdata = {"x0": self.x0,"y0": self.y0,"x1": x,"y1": y}
        
        
def main():
    viewer = DICOMViewer()
if __name__ == "__main__":
        main()
kkkk=DICOMViewer.openDICOMFile("",0)