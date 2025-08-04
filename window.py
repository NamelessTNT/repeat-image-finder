from tkinter import *
from tkinter import ttk, filedialog
# from tkinter.ttk import *

import json
import os
import ctypes

def get_path(receiver:StringVar, op_type:str):
    """
    Get the object path with a pop-up window
    :param receiver: The variable that saves the fetched path.
    :param op_type: The type of the object. Accepts 'folder' and 'file'.
    """
    if op_type == "folder":
        receiver.set(filedialog.askdirectory())
    elif op_type == "file":
        receiver.set(filedialog.askopenfilename())
    else:
        raise TypeError("invalid op_type")


main_window = Tk()
# main_style = ttk.Style()

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

folder_path = StringVar()
hash_path = StringVar()
record_path = StringVar()
# path variables

folder_button = Button(file_frame, text="Add Image Folder", width=25)
folder_button.config(command=lambda: get_path(folder_path, "folder"))
folder_entry = Entry(file_frame, textvariable=folder_path)
hash_button = Button(file_frame, text="Add Hash Record", width=25)
hash_button.config(command=lambda: get_path(hash_path, "file"))
hash_entry = Entry(file_frame, textvariable=hash_path)
record_button = Button(file_frame, text="Add repeat Record", width=25)
record_button.config(command=lambda: get_path(record_path, "file"))
record_entry = Entry(file_frame, textvariable=record_path)
# define widgets with their functions and bindings

folder_button.pack(padx=10, pady=10)
hash_button.pack(padx=10, pady=10)
record_button.pack(padx=10, pady=10)

main_window.mainloop()