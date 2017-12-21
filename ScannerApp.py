import tkinter as tk
from tkinter import filedialog
from GUI import RectTracker

import cv2
from PIL import Image
from PIL import ImageTk
import argparse

import scan_utilities

# Open canvas with template button

# Template button launches file selection dialog
class ScannerApplication(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        self.templateButton = tk.Button(self, text='Template', command=self.getTemplateFile)
        self.templateButton.grid()

        self.selectDocuments = tk.Button(self, text='Select Documents')
        self.selectDocuments.grid()

        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.grid()

    def getTemplateFile(self):
        self.templateFile = filedialog.askopenfilename(initialdir = "/",title = "Select file",
                                                       filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
        print(self.templateFile)
        selectAreas()


    def selectAreas(self):
        newWindow = tk.Toplevel(self.master)
        #top.wm_title 'Adam was here'
        canv = tk.Canvas(newWindow, width=500, height=500)
        img = Image.open(self.templateFile)
        tkImg = ImageTk.PhotoImage(img)
        canv.config(width=tkImg.width(), height=tkImg.height())
        canv.create_image((tkImg.width() / 2, tkImg.height() / 2), image=tkImg)
        canv.pack(fill=tk.BOTH, expand=tk.YES)

        rect = RectTracker(canv)
        x, y = None, None

        def cool_design(event):
            global x, y
            kill_xy()

            dashes = [3, 2]
            x = canv.create_line(event.x, 0, event.x, 1000, dash=dashes, tags='no')
            y = canv.create_line(0, event.y, 1000, event.y, dash=dashes, tags='no')

        def kill_xy(event=None):
            canv.delete('no')

        canv.bind('<Motion>', cool_design, '+')

        rect.autodraw(fill="", width=2)

if __name__ == '__main__':
    root = tk.Tk()
    app = ScannerApplication(root)
    root.title = 'Scanner Application'
    root.mainloop()

# Template doc is preprocessed, straightened, resized
# Template doc is presented for areas to be selected
# Areas returned as list for OCR
# Documents are opened, processed, results saved to table