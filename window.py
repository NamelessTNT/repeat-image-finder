from tkinter import *
from tkinter import ttk, filedialog
from tkinter.ttk import *
import tkinter.messagebox as messagebox

import os
import time
import ctypes
from send2trash import send2trash
from PIL import Image, ImageTk

import find_repeat

class RepeatFinder:
    """calls the find_repeat function and controls which repeated pair to show"""

    def __init__(self, _folder_path:StringVar, _hash_path:StringVar, _record_path:StringVar):
        self._folder = _folder_path
        self._hash = _hash_path
        self._record = _record_path
        self.repeat_list = []
        self.index = 0
        self.trash_files = []
        self.decision_records = {}

    def check_repeat(self):
        """calls the repeat finder and saves the result"""

        updated_list, new_list, hash_dict = find_repeat.generate_id_parallel(self._folder.get(),
                                                                             self._hash.get(),
                                                                             self._record.get())
        find_repeat.store_info(updated_list, hash_dict, self._hash.get(), self._record.get())
        # call and store
        self.repeat_list = new_list

    def index_step(self, flag):
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
        if self.repeat_list:
            return self.repeat_list[self.index]
        else:
            return None

    def get_record_length(self):
        """return the length of the record"""
        if self.repeat_list:
            return len(self.repeat_list)
        else:
            return None

    def reset_index(self):
        """reset the index"""
        self.index = 0

    def get_index(self):
        return self.index

    def add_delete_record(self, pic1, pic2):
        """add filepaths to the deletion list and execute deletion"""

        item = [0, 0]
        # record switch states
        if pic1.get_var():
            pic1.change_indicator_color("#EB5049")
            # change to red if selected
            item[0] = 1
            if pic1.get_path() not in self.trash_files:
                self.trash_files.append(pic1.get_path())
            # avoid adding repeated record
        else:
            pic1.change_indicator_color("#25AD34")

        if pic2.get_var():
            pic2.change_indicator_color("#EB5049")
            item[1] = 1
            if pic2.get_path() not in self.trash_files:
                self.trash_files.append(pic2.get_path())
        else:
            pic2.change_indicator_color("#25AD34")

        self.decision_records[str(self.index)] = item

    def set_viewer_button_state(self, pic1, pic2):
        """set the viewer's checkbutton state"""

        states = self.decision_records[str(self.index)]
        if states[0]:
            pic1.change_indicator_color("#EB5049")
            pic1.set_var(1)
        else:
            pic1.change_indicator_color("#25AD34")
            pic1.set_var(0)

        if states[1]:
            pic2.change_indicator_color("#EB5049")
            pic2.set_var(1)
        else:
            pic2.change_indicator_color("#25AD34")
            pic2.set_var(0)

    def execute_deletion(self):
        """delete selected files"""
        if self.trash_files:
            message = messagebox.askokcancel(title="Confirm deletion"
                                             ,message=
                                             f"Are you sure you want to delete {len(self.trash_files)} images?")
            if message:
                for item in self.trash_files:
                    send2trash(item)
                print(f"Successfully deleted {len(self.trash_files)} files.")

                index_delete = []
                for index, indicator in self.decision_records.items():
                    if indicator[0] or indicator[1]:
                        index_delete.append(int(index))
                index_delete.sort(reverse=True)
                for index in index_delete:
                    self.repeat_list.pop(index)
                self.decision_records = {}


class ImageViewer:
    """draws a picture in a frame, containing information like date and image size"""

    def __init__(self, master, image_path=""):
        self.master = master
        self.image_path = image_path
        self.var = IntVar()
        self.var.set(0)

        self.canvas = None
        self.textbox = None
        self.select_canvas = None
        # save widget information in the object for editing

        try:
            self.image = Image.open(image_path)
            self.photo = ImageTk.PhotoImage(self.image.resize((250, 250)))
            # puts the image in an object to avoid cleaning
        except (AttributeError, FileNotFoundError):
            self.image = Image.new("RGB", (250, 250), "#f0f0f0")
            self.photo = ImageTk.PhotoImage(self.image.resize((250, 250)))
        # deal with empty strings

        self.create_widget()

    def generate_text(self):
        """generate text for the textbox"""

        try:
            last_modified = time.strftime("%Y-%m-%d %H:%M:%S",
                                          time.localtime(os.path.getmtime(self.image_path)))
            file_size = os.path.getsize(self.image_path) / 1024
        except FileNotFoundError:
            return ""
        # if the input image_path is an empty string, the function would return an empty string too
        info = 'Image path: ' + self.image_path.replace("\\", '/') + \
               '\nImage size: ' + str(self.image.size) + \
               f'\nFile size: {file_size:.2f} kB' + \
               '\nLast modified: ' + last_modified
        return info

    def create_widget(self):
        """create the widgets"""

        self.textbox = Text(master=self.master, width=45, height=8, font=("Maple Mono NF CN Medium", 10))
        self.textbox.insert(END, self.generate_text())
        self.textbox.config(state="disabled")
        # create textbox

        self.canvas = Canvas(master=self.master, width=self.photo.width(), height=self.photo.height())
        self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        # place picture in a canvas

        checkbox = Checkbutton(master=self.master, text="Delete", variable=self.var)

        self.select_canvas = Canvas(master=self.master, width=30, height=self.photo.height())
        self.select_canvas.create_rectangle(0, 0,
                                            15, self.photo.height(),
                                            outline="#f0f0f0", width=2, fill="#f0f0f0")
        # make the rectangle invisible at first

        self.canvas.pack(side="left", padx=10, pady=10)
        self.textbox.pack(side="left", padx=10, pady=10)
        checkbox.pack(side="left", padx=10, pady=10)
        self.select_canvas.pack(side="left", padx=(5, 0), pady=10)

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

    def change_indicator_color(self, color):
        """change checkbox color"""
        self.select_canvas.create_rectangle(0, 0,
                                            15, self.photo.height(),
                                            outline="#f0f0f0", width=2, fill=color)

    def get_var(self):
        return self.var.get()

    def set_var(self, var):
        self.var.set(var)

    def get_path(self):
        return self.image_path


def refresh_state(finder: RepeatFinder, label: Label,
                  pic1: ImageViewer, pic2: ImageViewer,
                  record_length:StringVar, current_pos:StringVar):
    """cooperate with the refresh button"""

    if finder.repeat_list:
        label.configure(text="Complete!", foreground="#25AD34")
        finder.reset_index()
        record_length.set(str(finder.get_record_length()))
        # get the number of repeated records and show it

        pic1.modify_viewer(finder.export_record()[0])
        pic2.modify_viewer(finder.export_record()[1])
        pic1.change_indicator_color("#f0f0f0")
        pic2.change_indicator_color("#f0f0f0")
        current_pos.set(str(finder.get_index() + 1))
        # modify picture and initial info

    main_window.update()

def step(finder: RepeatFinder, pic1: ImageViewer, pic2: ImageViewer,
         record_length:StringVar, record_index:StringVar, flag:int):
    """receives Prev and Next button event and act accordingly"""

    if finder.repeat_list:
        finder.index_step(flag)
        record_length.set(str(finder.get_record_length()))
        record_index.set(str(finder.get_index() + 1))
        # show numbers

        pic1.modify_viewer(finder.export_record()[0])
        pic2.modify_viewer(finder.export_record()[1])
        pic1.change_indicator_color("#f0f0f0")
        pic2.change_indicator_color("#f0f0f0")
        # modify pictures and set background color to default

        if str(finder.get_index()) in finder.decision_records.keys():
            finder.set_viewer_button_state(pic1, pic2)
        # set checkbox variable and the color bar accordingly

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

folder_path = StringVar(file_frame, value="")
hash_path = StringVar(file_frame,
                      value="stored_info/hash.json")
record_path = StringVar(file_frame,
                        value="stored_info/repeat.json")
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
                        command=lambda: refresh_state(repeat_finder, indicator_label,
                                                      upper_box, lower_box, rep_num, current_num))
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

pic_frame1 = LabelFrame(tab_image, text="Picture I")
pic_frame2 = LabelFrame(tab_image, text="Picture II")

upper_box = ImageViewer(pic_frame1)
lower_box = ImageViewer(pic_frame2)

pic_frame1.pack(side="top", padx=10, pady=10)
Separator(tab_image, orient="horizontal").pack(fill="x", padx=25, pady=(10, 0))
pic_frame2.pack(side="bottom", padx=10, pady=10)

option_frame = Frame(main_window)
option_frame.pack(side="right", padx=10, pady=10)

Label(option_frame, text="OPTIONS",
      font=("LXGW Wenkai", 9, "bold")).pack(side="top", padx=10, pady=(0, 110))
# dummy for symmetry
Label(option_frame, text="Total").pack(side="top", padx=10, pady=(10, 0))
rep_num = StringVar(option_frame, value="0")
Label(option_frame, textvariable=rep_num, font=("Maple Mono NF CN Medium", 9)).pack(side="top")
Label(option_frame, text="Repeats").pack(side="top", padx=10, pady=(0, 10))

prev_button = Button(option_frame, text="< Prev")
prev_button.configure(command=lambda: step(repeat_finder, upper_box, lower_box,
                                           rep_num, current_num, -1))
prev_button.pack(side="top", padx=10, pady=10)

confirm_button = Button(option_frame, text="Confirm")
confirm_button.configure(command=lambda: repeat_finder.add_delete_record(upper_box, lower_box))
confirm_button.pack(side="top", padx=10, pady=10)

next_button = Button(option_frame, text="> Next")
next_button.configure(command=lambda: step(repeat_finder, upper_box, lower_box,
                                           rep_num, current_num, 2))
next_button.pack(side="top", padx=10, pady=10)

Label(option_frame, text="Current").pack(side="top", padx=10, pady=(10, 0))
current_num = StringVar(option_frame, value="0")
Label(option_frame, textvariable=current_num, font=("Maple Mono NF CN Medium", 9)).pack(side="top")
# content in option_frame

delete_button = Button(option_frame, text="Delete")
delete_button.configure(command=lambda: repeat_finder.execute_deletion())
delete_button.pack(side="bottom", padx=10, pady=(110, 0), ipady=10)

main_window.mainloop()