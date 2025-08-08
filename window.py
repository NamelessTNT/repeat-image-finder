from tkinter import *
from tkinter import ttk, filedialog
from tkinter.ttk import *

import json
import os
import time
import ctypes
from PIL import Image, ImageTk

import find_repeat

# todo: finish prev & next button logic
# todo: index demonstration
# deletion marked by boxes

class RepeatFinder:
    """calls the find_repeat function and controls which repeated pair to show"""

    def __init__(self, _folder_path:StringVar, _hash_path:StringVar, _record_path:StringVar):
        self._folder = _folder_path
        self._hash = _hash_path
        self._record = _record_path
        self.repeat_list = []
        self.index = 0

    def check_repeat(self):
        """calls the repeat finder and saves the result"""

        updated_list, new_list, hash_dict = find_repeat.generate_id_parallel(self._folder.get(),
                                                                             self._hash.get(),
                                                                             self._record.get())
        find_repeat.store_info(updated_list, hash_dict, self._hash.get(), self._record.get())
        # call and store
        self.repeat_list = new_list

    def index_step(self, flag, pic1, pic2):
        """change index value based on the flag"""

        if self.repeat_list:
            list_length = len(self.repeat_list)
        else:
            return
        # gets list length if it's not empty

        if flag > 0:
            self.index += 1
        else:
            self.index -= 1

        while self.index >= list_length:
            self.index -= list_length
        while self.index < 0:
            self.index += list_length
        # make sure the index stays in a reasonable range

    def export_record(self):
        """export the record"""
        return self.repeat_list[self.index]

    def get_index(self):
        return self.index


class ImageViewer:
    """draws a picture in a frame, containing information like date and image size"""

    def __init__(self, master, image_path):
        self.master = master
        self.image_path = image_path
        self.var = IntVar()
        self.var.set(0)

        self.canvas = None
        self.textbox = None
        # save widget information in the object for editing

        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image.resize((250, 250)))
        # puts the image in an object to avoid cleaning

        self.create_widget()

    def generate_text(self):
        """generate text for the textbox"""

        last_modified = time.strftime("%Y-%m-%d %H:%M:%S",
                                      time.localtime(os.path.getmtime(self.image_path)))
        file_size = os.path.getsize(self.image_path) / 1024
        info = 'Image path: ' + self.image_path.replace("\\", '/') + \
               '\nImage size: ' + str(self.image.size) + \
               f'\nFile size: {file_size:.2f} kB' + \
               '\nLast modified: ' + last_modified
        return info

    def create_widget(self):
        """create the widgets"""

        self.textbox = Text(master=self.master, width=48, height=8, font=("Maple Mono NF CN Medium", 10))
        self.textbox.insert(END, self.generate_text())
        self.textbox.config(state="disabled")
        # create textbox

        self.canvas = Canvas(master=self.master, width=self.photo.width(), height=self.photo.height())
        self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        # place picture in a canvas

        checkbox = Checkbutton(master=self.master, text="Delete", variable=self.var)

        self.canvas.pack(side="left", padx=10, pady=10)
        self.textbox.pack(side="left", padx=10, pady=10)
        checkbox.pack(side="left", padx=10, pady=10)

    def modify_viewer(self, image_path):
        """update information according to image_path"""

        self.image_path = image_path
        self.var.set(0)

        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image.resize((250, 250)))
        self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        # change picture

        self.textbox.config(state="normal")
        self.textbox.delete("1.0", END)
        self.textbox.insert(END, self.generate_text())
        self.textbox.config(state="disabled")
        # textbox should be enabled first to edit its information

    def get_var(self):
        return self.var.get()


def refresh_state(finder: RepeatFinder, label: Label,
                  pic1: ImageViewer, pic2: ImageViewer):
    """cooperate with the refresh button"""
    if finder.repeat_list:
        label.configure(text="Complete!", foreground="#25AD34")
        pic1.modify_viewer(finder.export_record()[0])
        pic2.modify_viewer(finder.export_record()[1])
    main_window.update()

def get_path(receiver:StringVar, op_type:str):
    """
    Get the object path with a pop-up window
    :param receiver: The variable that saves the fetched path.
    :param op_type: The type of the object. Accepts 'folder' and 'file'.
    """

    if op_type == "folder":
        receiver.set(filedialog.askdirectory().replace("/", "\\"))
    elif op_type == "file":
        receiver.set(filedialog.askopenfilename())
    else:
        raise TypeError("invalid op_type")

def check_content():
    """check if all three boxes are filled with paths"""
    if folder_path.get() and hash_path.get() and record_path.get():
        start_button.configure(state="normal")


main_window = Tk()
main_style = ttk.Style()
main_style.configure(style="TButton", font=("LXGW Wenkai", 8))
main_style.configure(style="Starter.TButton", font=("LXGW Wenkai", 15))
main_style.configure(".", font=("LXGW Wenkai", 9))

ctypes.windll.shcore.SetProcessDpiAwareness(1)
# take control of window scaling
ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
# get scale coefficient
main_window.tk.call('tk', 'scaling', ScaleFactor/60)
# execute window scaling

main_window.title("Repeat Image Finder")
main_window.geometry('1500x700')
main_window.resizable(False, False)
main_window.configure(bg='#f0f0f0')
# basic window properties

file_frame = LabelFrame(main_window, text="Files")
file_frame.pack(side="left", fill="y", padx=10, pady=10)
# create frame for initial data collection

folder_path = StringVar(file_frame, value="D:\\30242\\Pictures\\Captured\\bg")
hash_path = StringVar(file_frame,
                      value="D:\\30242\\Documents\\Practice\\RepeatImageFinder\\stored_info\\hash.json")
record_path = StringVar(file_frame,
                        value="D:\\30242\\Documents\\Practice\\RepeatImageFinder\\stored_info\\repeat.json")
# path variables

repeat_finder = RepeatFinder(folder_path, hash_path, record_path)
# create finder object

folder_button = Button(file_frame, text="Browse...", width=8)
folder_button.config(command=lambda: get_path(folder_path, "folder"))
folder_entry = Entry(file_frame, textvariable=folder_path, font=("Maple Mono NF CN Medium", 9))
folder_entry.bind("<Button-1>", lambda event:check_content())
# bind clicks to activate the start button

hash_button = Button(file_frame, text="Browse...", width=8)
hash_button.config(command=lambda: get_path(hash_path, "file"))
hash_entry = Entry(file_frame, textvariable=hash_path, font=("Maple Mono NF CN Medium", 9))
hash_entry.bind("<Button-1>", lambda event:check_content())

record_button = Button(file_frame, text="Browse...", width=8)
record_button.config(command=lambda: get_path(record_path, "file"))
record_entry = Entry(file_frame, textvariable=record_path, font=("Maple Mono NF CN Medium", 9))
record_entry.bind("<Button-1>", lambda event:check_content())

start_button = Button(file_frame, text="Start", width=10,
                      state="disabled", style="Starter.TButton",
                      command=lambda: repeat_finder.check_repeat())

indicator_label = Label(file_frame, text="Waiting...", foreground="#EB5049")

refresh_button = Button(file_frame, text="Refresh", width=10,
                        command=lambda: refresh_state(repeat_finder, indicator_label, upper_box, lower_box))
# define widgets with their functions and bindings

Label(file_frame, text="Image Path", font=("LXGW Wenkai", 12)).pack(padx=10, pady=(30, 0))
folder_entry.pack()
folder_button.pack(anchor='e', padx=10, pady=5)

Label(file_frame, text="Hash record path", font=("LXGW Wenkai", 12)).pack(padx=10, pady=(30, 0))
hash_entry.pack()
hash_button.pack(padx=10, pady=5, anchor='e')

Label(file_frame, text="Repeat record path", font=("LXGW Wenkai", 12)).pack(padx=10, pady=(30, 0))
record_entry.pack()
record_button.pack(padx=10, pady=5, anchor='e')

start_button.pack(padx=10, pady=(45, 10), ipadx=5, ipady=10)
indicator_label.pack(padx=10)
refresh_button.pack(padx=10, pady=5, ipadx=5, ipady=10)

tab_image = LabelFrame(main_window, text="Image Comparison", labelanchor="nw")
tab_image.pack(side="left", fill="y", padx=10, pady=10)
# create actual tabs

pic_frame1 = Frame(tab_image)
pic_frame2 = Frame(tab_image)

upper_box = ImageViewer(pic_frame1, "testpic/aa.jpg")
lower_box = ImageViewer(pic_frame2, "testpic/Aya-bg.jpg")

pic_frame1.pack(side="top", padx=10, pady=10)
pic_frame2.pack(side="bottom", padx=10, pady=10)

option_frame = Frame(main_window)
option_frame.pack(side="right", padx=10, pady=10)

Label(option_frame, text="Total").pack(side="top", padx=10, pady=(10, 0))
rep_num = StringVar(option_frame, value="0")
Label(option_frame, textvariable=rep_num).pack(side="top")
Label(option_frame, text="Repeats").pack(side="top", padx=10, pady=(0, 10))

prev_button = Button(option_frame, text="< Prev")
prev_button.pack(side="top", padx=10, pady=10)
next_button = Button(option_frame, text="> Next")
next_button.pack(side="top", padx=10, pady=10)

Label(option_frame, text="Current").pack(side="top", padx=10, pady=10)
current_num = StringVar(option_frame, value="0")
Label(option_frame, textvariable=current_num).pack(side="top", padx=10, pady=10)
# content in option_frame

main_window.mainloop()