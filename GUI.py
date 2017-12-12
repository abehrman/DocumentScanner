from tkinter import *
from tkinter import messagebox

import cv2
from PIL import Image
from PIL import ImageTk

import scan_utilities

"""Rect Tracker class for Python Tkinter Canvas"""
boxes = []

def groups(glist, numPerGroup=2):
    result = []

    i = 0
    cur = []
    for item in glist:
        if not i < numPerGroup:
            result.append(cur)
            cur = []
            i = 0

        cur.append(item)
        i += 1

    if cur:
        result.append(cur)

    return result


def average(points):
    aver = [0, 0]

    for point in points:
        aver[0] += point[0]
        aver[1] += point[1]

    return aver[0] / len(points), aver[1] / len(points)


class RectTracker:
    def __init__(self, canvas):
        self.canvas = canvas
        self.item = None

    def draw(self, start, end, **opts):
        """Draw the rectangle"""
        return self.canvas.create_rectangle(*(list(start) + list(end)), **opts)

    def autodraw(self, **opts):
        """Setup automatic drawing; supports command option"""
        self.start = None
        self.canvas.bind("<Button-1>", self.__update, '+')
        self.canvas.bind("<B1-Motion>", self.__update, '+')
        self.canvas.bind("<ButtonRelease-1>", self.__stop, '+')

        self._command = opts.pop('command', lambda *args: None)
        self.rectopts = opts

    def __update(self, event):
        if not self.start:
            self.start = [event.x, event.y]
            return

        if self.item is not None:
            self.canvas.delete(self.item)
        self.item = self.draw(self.start, (event.x, event.y), **self.rectopts)
        self._command(self.start, (event.x, event.y))

    def __stop(self, event):
        label = popupWindow(self.canvas, self.start, event.x, event.y)

        self.start = None
        self.canvas.delete(self.item)
        self.item = None

    def hit_test(self, start, end, tags=None, ignoretags=None, ignore=[]):
        """
        Check to see if there are items between the start and end
        """
        ignore = set(ignore)
        ignore.update([self.item])

        # first filter all of the items in the canvas
        if isinstance(tags, str):
            tags = [tags]

        if tags:
            tocheck = []
            for tag in tags:
                tocheck.extend(self.canvas.find_withtag(tag))
        else:
            tocheck = self.canvas.find_all()
        tocheck = [x for x in tocheck if x != self.item]
        if ignoretags:
            if not hasattr(ignoretags, '__iter__'):
                ignoretags = [ignoretags]
            tocheck = [x for x in tocheck if x not in self.canvas.find_withtag(it) for it in ignoretags]

        self.items = tocheck

        # then figure out the box
        xlow = min(start[0], end[0])
        xhigh = max(start[0], end[0])

        ylow = min(start[1], end[1])
        yhigh = max(start[1], end[1])

        items = []
        for item in tocheck:
            if item not in ignore:
                x, y = average(groups(self.canvas.coords(item)))
                if (xlow < x < xhigh) and (ylow < y < yhigh):
                    items.append(item)

        return items


class popupWindow(object):
    global boxes

    def __init__(self, master, start, eventx, eventy):
        top = self.top = Toplevel(master)
        self.l = Label(top, text="Hello World")
        self.l.pack()
        self.e = Entry(top)
        self.e.pack()
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()
        self.eventx = eventx
        self.eventy = eventy
        self.start = start

    def cleanup(self):
        box = {'name': self.e.get(),
               'start': self.start,
               'end': (self.eventx, self.eventy)}
        boxes.append(box)

        self.top.destroy()


def main():
    global boxes
    canv = Canvas(width=500, height=500)
    img = Image.open('biz_card_prepped.png')
    tkImg = ImageTk.PhotoImage(img)
    canv.config(width=tkImg.width(), height=tkImg.height())
    canv.create_image((tkImg.width() / 2, tkImg.height() / 2), image=tkImg)
    canv.pack(fill=BOTH, expand=YES)

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

    # command
    def onDrag(start, end):
        global x, y
        items = rect.hit_test(start, end)
        for x in rect.items:
            if x not in items:
                canv.itemconfig(x, fill='grey')
            else:
                canv.itemconfig(x, fill='blue')

    rect.autodraw(fill="", width=2, command=onDrag)

    mainloop()

    boxes = scan_utilities.process_image(cv2.imread('biz_card_prepped.png'), boxes)
    message = []

    for box in boxes:
        message.append('{}: {}'.format(box['name'], box['value']))

    messagebox.showinfo('Fields', '\n'.join(message))

if __name__ == '__main__':
    main()
