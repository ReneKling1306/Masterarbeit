import fileinput
import sys
import customtkinter
import os
from tkinter import filedialog
import exiftool
from tkinter import messagebox
from xml.etree import cElementTree as ET
import datetime
import shutil
import webbrowser

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'jpe', 'png', 'jng', 'mng', 'tiff', 'tif', 'webp', 'jp2', 'jpf', 'jpm',
                      'heif', 'heic', 'hif', 'gif', 'eps', 'psd', 'avif', 'flif', 'mp4'}
ALLOWED_LICENSE_EXTENSIONS = {'xmp'}


def allowed_file(imagename):
    return '.' in imagename and imagename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def callback(url):
    webbrowser.open_new(url)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        customtkinter.set_default_color_theme("green")

        try:
            self.wm_iconbitmap(
                f'{os.path.join(os.path.dirname(__file__))}/ExifTool/AII_Logo.ico')
        except:
            pass

        self.title("AII-License")
        self.geometry("800x550")
        self.minsize(650, 480)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.license_picker_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="License Picker",
                                                             fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                             anchor="w", command=self.license_picker_back_event)
        self.license_picker_button.grid(row=1, column=0, sticky="ew")

        self.licensing_tool_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Licensing Tool",
                                                             fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                             anchor="w", command=self.licensing_tool_button_event)
        self.licensing_tool_button.grid(row=2, column=0, sticky="ew")

        self.link1 = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="AIImageLicense.com",
                                             fg_color="transparent", text_color=("gray10", "gray90"))
        self.link1.grid(row=5, column=0, sticky="ew")
        self.link1.bind(
            "<Button-1>", lambda e: callback("http://127.0.0.1:5000"))

        self.link2 = customtkinter.CTkButton(self, corner_radius=0, height=40, text="Using ExiftTool Version 12.76",
                                             fg_color="transparent", text_color=("gray10", "gray90"))
        self.link2.grid(
            row=1, column=0, sticky="ew")
        self.link2.bind(
            "<Button-1>", lambda e: callback("https://exiftool.org/"))

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["System", "Dark", "Light",],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(
            row=6, column=0, padx=20, pady=20, sticky="s")

        # license_picker frame
        self.license_picker_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.license_picker_frame.grid_columnconfigure(0, weight=1)

        self.license_picker_radiobutton_var = customtkinter.IntVar(value=1)

        license_picker_question = customtkinter.CTkLabel(
            master=self.license_picker_frame, justify=customtkinter.CENTER, font=('Helvetica', 15), wraplength=300, text="Are you familiar with the different Licenses or do you need help choosing the appropriate one?")
        license_picker_question.place(relx=0.5, rely=0.2, anchor="center")

        license_picker_radiobutton_yes = customtkinter.CTkRadioButton(
            master=self.license_picker_frame, font=('Helvetica', 15), variable=self.license_picker_radiobutton_var, value=1, text="Yes, i know which License to choose")
        license_picker_radiobutton_yes.place(
            relx=0.5, rely=0.3, anchor="center")

        self.license_picker_license_select = customtkinter.CTkOptionMenu(
            self.license_picker_frame, font=('Helvetica', 15), width=200, values=["Permitted For Training", "BY", "NC", "NG", "BY-NC", "BY-NG", "NC-NG", "BY-NC-NG", "Do Not Train"])
        self.license_picker_license_select.place(
            relx=0.5, rely=0.4, anchor="center")
        self.license_picker_license_select.set("Choose a License")

        license_picker_radiobutton_no = customtkinter.CTkRadioButton(
            master=self.license_picker_frame, font=('Helvetica', 15), variable=self.license_picker_radiobutton_var, value=2, text="No, i need help choosing a License")
        license_picker_radiobutton_no.place(
            relx=0.5, rely=0.5, anchor="center")

        license_picker_next_button = customtkinter.CTkButton(
            master=self.license_picker_frame, font=('Helvetica', 15), width=150, command=self.choose_license_button_event, text="Next Step")
        license_picker_next_button.place(relx=0.5, rely=0.6, anchor="center")

        # allow_use frame
        self.allow_use_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.allow_use_frame.grid_columnconfigure(0, weight=1)

        self.allow_use_radiobutton_var = customtkinter.IntVar(value=1)

        allow_use_question = customtkinter.CTkLabel(
            master=self.allow_use_frame, justify=customtkinter.CENTER, font=('Helvetica', 15), wraplength=300, text="Do you want to allow the use of your image(s) for the training of AI-Models?")
        allow_use_question.place(relx=0.5, rely=0.3, anchor="center")

        allow_use_radiobutton_yes = customtkinter.CTkRadioButton(
            master=self.allow_use_frame, font=('Helvetica', 15), variable=self.allow_use_radiobutton_var, value=1, text="Yes, i allow the use of my image(s)")
        allow_use_radiobutton_yes.place(relx=0.5, rely=0.4, anchor="center")

        allow_use_radiobutton_no = customtkinter.CTkRadioButton(
            master=self.allow_use_frame, font=('Helvetica', 15), variable=self.allow_use_radiobutton_var, value=2, text="No, i do not allow the use of my image(s)")
        allow_use_radiobutton_no.place(relx=0.5, rely=0.5, anchor="center")

        allow_use_next_button = customtkinter.CTkButton(
            master=self.allow_use_frame, font=('Helvetica', 15), width=150, command=self.attribution_frame_button_event, text="Next Step")
        allow_use_next_button.place(relx=0.5, rely=0.6, anchor="center")

        allow_use_back_button = customtkinter.CTkButton(
            master=self.allow_use_frame, command=self.license_picker_back_event, font=('Helvetica', 15), text="Back", width=150)
        allow_use_back_button.place(relx=0.5, rely=0.7, anchor="center")

        # attribution frame
        self.attribution_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.attribution_frame.grid_columnconfigure(0, weight=1)

        self.attribution_radiobutton_var = customtkinter.IntVar(value=2)

        attribution_question = customtkinter.CTkLabel(
            master=self.attribution_frame, justify=customtkinter.CENTER, font=('Helvetica', 15), wraplength=300, text="Do you want to be credited for the use of your image(s) for the training of AI-Models?")
        attribution_question.place(relx=0.5, rely=0.3, anchor="center")

        attribution_radiobutton_yes = customtkinter.CTkRadioButton(
            master=self.attribution_frame, font=('Helvetica', 15), variable=self.attribution_radiobutton_var, value=1, text="Yes, i want to be credited for the use of my image(s)")
        attribution_radiobutton_yes.place(relx=0.5, rely=0.4, anchor="center")

        attribution_radiobutton_no = customtkinter.CTkRadioButton(
            master=self.attribution_frame, font=('Helvetica', 15), variable=self.attribution_radiobutton_var, value=2, text="No, i do not want to be credited for the use of my image(s)")
        attribution_radiobutton_no.place(relx=0.5, rely=0.5, anchor="center")

        attribution_next_button = customtkinter.CTkButton(
            master=self.attribution_frame, font=('Helvetica', 15), width=150, command=self.non_commercial_frame_button_event, text="Next Step")
        attribution_next_button.place(relx=0.5, rely=0.6, anchor="center")

        attribution_back_button_ = customtkinter.CTkButton(
            master=self.attribution_frame, command=self.choose_license_button_event, font=('Helvetica', 15), text="Back", width=150)
        attribution_back_button_.place(relx=0.5, rely=0.7, anchor="center")

        # non_commercial frame
        self.non_commercial_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.non_commercial_frame.grid_columnconfigure(0, weight=1)

        self.non_commercial_radiobutton_var = customtkinter.IntVar(
            value=1)

        non_commercial_question = customtkinter.CTkLabel(
            master=self.non_commercial_frame, justify=customtkinter.CENTER, font=('Helvetica', 15), wraplength=300, text="Do you want to also allow the use of you image(s) for the training of AI-Models that possess commercial intentions?")
        non_commercial_question.place(relx=0.5, rely=0.3, anchor="center")

        non_commercial_radiobutton_yes = customtkinter.CTkRadioButton(
            master=self.non_commercial_frame, font=('Helvetica', 15), variable=self.non_commercial_radiobutton_var, value=1, text="Yes, i allow the use of my image(s) for commercial AI-Models")
        non_commercial_radiobutton_yes.place(
            relx=0.5, rely=0.4, anchor="center")

        non_commercial_radiobutton_no = customtkinter.CTkRadioButton(
            master=self.non_commercial_frame, font=('Helvetica', 15), variable=self.non_commercial_radiobutton_var, value=2, text="No, i do not allow the use of my image(s) for commercial AI-Models")
        non_commercial_radiobutton_no.place(
            relx=0.5, rely=0.5, anchor="center")

        non_commercial_next_button = customtkinter.CTkButton(
            master=self.non_commercial_frame, font=('Helvetica', 15), width=150, command=self.non_generative_frame_button_event, text="Next Step")
        non_commercial_next_button.place(relx=0.5, rely=0.6, anchor="center")

        non_commercial_back_button = customtkinter.CTkButton(
            master=self.non_commercial_frame, command=self.attribution_frame_button_event, font=('Helvetica', 15), text="Back", width=150)
        non_commercial_back_button.place(relx=0.5, rely=0.7, anchor="center")

        # non_generative frame
        self.non_generative_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.non_generative_frame.grid_columnconfigure(0, weight=1)

        self.non_generative_radiobutton_var = customtkinter.IntVar(
            value=1)

        non_generative_question = customtkinter.CTkLabel(
            master=self.non_generative_frame, justify=customtkinter.CENTER, font=('Helvetica', 15), wraplength=300, text="Do you want to also allow the use of you image(s) for the training of generative AI-Models?")
        non_generative_question.place(relx=0.5, rely=0.3, anchor="center")

        non_generative_radiobutton_yes = customtkinter.CTkRadioButton(
            master=self.non_generative_frame, font=('Helvetica', 15), variable=self.non_generative_radiobutton_var, value=1, text="Yes, i allow the use of my image(s) for generative AI-Models")
        non_generative_radiobutton_yes.place(
            relx=0.5, rely=0.4, anchor="center")

        non_generative_radiobutton_no = customtkinter.CTkRadioButton(
            master=self.non_generative_frame, font=('Helvetica', 15), variable=self.non_generative_radiobutton_var, value=2, text="No, i do not allow the use of my image(s) for generative AI-Models")
        non_generative_radiobutton_no.place(
            relx=0.5, rely=0.5, anchor="center")

        non_generative_next_button = customtkinter.CTkButton(
            master=self.non_generative_frame, font=('Helvetica', 15), width=150, command=self.add_info_frame_button, text="Next Step")
        non_generative_next_button.place(relx=0.5, rely=0.6, anchor="center")

        non_generative_back_button = customtkinter.CTkButton(
            master=self.non_generative_frame, command=self.non_commercial_frame_button_event, font=('Helvetica', 15), text="Back", width=150)
        non_generative_back_button.place(relx=0.5, rely=0.7, anchor="center")

        # add_info frame
        self.add_info_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")

        self.label_license = customtkinter.CTkLabel(
            master=self.add_info_frame, justify=customtkinter.CENTER, font=('Helvetica', 20), text="")
        self.label_license.place(relx=0.5, rely=0.1, anchor="center")

        add_info_question = customtkinter.CTkLabel(
            master=self.add_info_frame, justify=customtkinter.CENTER, font=('Helvetica', 15), wraplength=300, text="Do you wish to add attribution information to the License? If you have chosen a BY license you are required to add at least one form of attribution.")
        add_info_question.place(relx=0.5, rely=0.2, anchor="center")

        self.entry_creator = customtkinter.CTkEntry(
            master=self.add_info_frame, width=300, font=('Helvetica', 20), placeholder_text="Enter: Creator(s)")
        self.entry_creator.place(relx=0.5, rely=0.4, anchor="center")

        self.entry_email = customtkinter.CTkEntry(
            master=self.add_info_frame, width=300, font=('Helvetica', 20), placeholder_text="Enter: Email")
        self.entry_email.place(relx=0.5, rely=0.5, anchor="center")

        self.entry_contact = customtkinter.CTkEntry(
            master=self.add_info_frame, width=300, font=('Helvetica', 20), placeholder_text="Enter: Contact Website")
        self.entry_contact.place(relx=0.5, rely=0.6, anchor="center")

        self.entry_udd = customtkinter.CTkEntry(
            master=self.add_info_frame, width=300, font=('Helvetica', 20), placeholder_text="Enter: User Defined Data")
        self.entry_udd.place(relx=0.5, rely=0.7, anchor="center")

        add_info_next_button = customtkinter.CTkButton(
            self.add_info_frame, text="Next Step", font=('Helvetica', 15), command=self.licensing_frame_button_event, width=150)
        add_info_next_button.place(relx=0.5, rely=0.8, anchor="center")

        add_info_back_button = customtkinter.CTkButton(
            master=self.add_info_frame, command=self.license_picker_button_event, font=('Helvetica', 15), text="Back", width=150)
        add_info_back_button.place(relx=0.5, rely=0.9, anchor="center")

        # licensing frame
        self.licensing_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")

        self.label_license_tool = customtkinter.CTkLabel(
            master=self.licensing_frame, justify=customtkinter.CENTER, font=('Helvetica', 20), text="")
        self.label_license_tool.place(relx=0.5, rely=0.1, anchor="center")

        licensing_download_button = customtkinter.CTkButton(
            master=self.licensing_frame, font=('Helvetica', 15), command=self.download_license, text="Download License", width=150)
        licensing_download_button.place(relx=0.5, rely=0.3, anchor="center")

        licensing_image_button = customtkinter.CTkButton(
            master=self.licensing_frame, font=('Helvetica', 15), text="Choose your Image(s)", command=self.selectImage_2, width=170)
        licensing_image_button.place(relx=0.5, rely=0.4, anchor="center")

        self.licensing_selection = customtkinter.CTkLabel(
            master=self.licensing_frame, font=('Helvetica', 15), justify=customtkinter.LEFT, text='')
        self.licensing_selection.place(relx=0.5, rely=0.5, anchor="center")

        self.sumbit_button_picker = customtkinter.CTkButton(
            master=self.licensing_frame, font=('Helvetica', 15), text="Submit", command=self.insert_license_picker, state=customtkinter.DISABLED, width=150)
        self.sumbit_button_picker.place(relx=0.5, rely=0.7, anchor="center")

        self.licensing_done = customtkinter.CTkLabel(
            master=self.licensing_frame, font=('Helvetica', 15), justify=customtkinter.LEFT, text='',  wraplength=400)
        self.licensing_done.place(relx=0.5, rely=0.8, anchor="center")

        licensing_back_button = customtkinter.CTkButton(
            master=self.licensing_frame, font=('Helvetica', 15), command=self.add_info_frame_button, text="Back", width=150)
        licensing_back_button.place(relx=0.5, rely=0.9, anchor="center")

        # licensing_tool frame
        self.licensing_tool_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")

        self.licensing_tool_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.licensing_tool_frame.grid_columnconfigure(0, weight=1)

        licensing_tool_image_button = customtkinter.CTkButton(
            master=self.licensing_tool_frame, font=('Helvetica', 15), text="Choose your Image(s)", command=self.selectImage, width=170)
        licensing_tool_image_button.place(relx=0.5, rely=0.2, anchor="center")

        self.licensing_tool_selection = customtkinter.CTkLabel(
            master=self.licensing_tool_frame, font=('Helvetica', 15), justify=customtkinter.LEFT, text='')
        self.licensing_tool_selection.place(
            relx=0.5, rely=0.3, anchor="center")

        licensing_tool_license_button = customtkinter.CTkButton(
            master=self.licensing_tool_frame, font=('Helvetica', 15), text="Choose your License", command=self.selectLicense, width=170)
        licensing_tool_license_button.place(
            relx=0.5, rely=0.4, anchor="center")

        self.licensing_tool_license_selection = customtkinter.CTkLabel(
            master=self.licensing_tool_frame, font=('Helvetica', 15), justify=customtkinter.LEFT, text='')
        self.licensing_tool_license_selection.place(
            relx=0.5, rely=0.5, anchor="center")

        self.sumbit_button_tool = customtkinter.CTkButton(
            master=self.licensing_tool_frame, font=('Helvetica', 15), text="Submit", command=self.insert_license_tool, state=customtkinter.DISABLED, width=150)
        self.sumbit_button_tool.place(relx=0.5, rely=0.6, anchor="center")

        self.licensing_done_tool = customtkinter.CTkLabel(
            master=self.licensing_tool_frame, font=('Helvetica', 15), justify=customtkinter.LEFT, text='',  wraplength=400)
        self.licensing_done_tool.place(relx=0.5, rely=0.7, anchor="center")

        # default frame
        self.select_frame_by_name("license_picker_frame")

    def selectImage_2(self):
        filetypes = (
            ('All files', '*.*'),
        )
        global filenames_picker
        files = filedialog.askopenfilenames(
            title='Open files',
            initialdir='/',
            filetypes=filetypes)
        if files != "":
            filenames_picker = files
            for file in files:
                filename = file.split('/')[len(file.split('/'))-1]
                self.licensing_selection.configure(text=filename)
            self.sumbit_button_picker.configure(state="normal")

    def selectImage(self):
        filetypes = (
            ('All files', '*.*'),
        )
        global filenames_tool
        global licensename
        files = filedialog.askopenfilenames(
            title='Open files',
            initialdir='/',
            filetypes=filetypes)
        if files != "":
            filenames_tool = files
            for file in files:
                filename = file.split('/')[len(file.split('/'))-1]
                self.licensing_tool_selection.configure(text=filename)
            if 'licensename' in globals():
                try:
                    self.sumbit_button_tool.configure(state="normal")
                except:
                    pass

    def selectLicense(self):
        filetypes = (
            ('XMP files', '*.xmp'),
        )
        global licensename
        global filenames_tool
        file = filedialog.askopenfilename(
            title='Open files',
            initialdir='/',
            filetypes=filetypes)
        if file != "":
            licensename = file
            self.licensing_tool_license_selection.configure(text=licensename.split(
                '/')[len(licensename.split('/'))-1])
            if 'filenames_tool' in globals():
                try:
                    self.sumbit_button_tool.configure(state="normal")
                except:
                    pass

    def download_license(self):
        path = filedialog.askdirectory()
        if path != "":
            creator = self.entry_creator.get().strip()
            email = self.entry_email.get().strip()
            contact = self.entry_contact.get().strip()
            udd = self.entry_udd.get().strip()
            license = "AII " + license_picker

            condition = ""
            if 'Permitted For Training' not in license and 'Do Not Train' not in license:
                condition = "Training is allowed when:"
                if 'BY' in license:
                    condition += " Attribution is given;"
                if 'NC' in license:
                    condition += " Use is non-commercial;"
                if 'NG' in license:
                    condition += " Use is non-generative;"
            try:
                tree = ET.parse(
                    f'{os.path.join(os.path.dirname(__file__))}/ExifTool/License.xmp')
                root = tree.getroot()
                root.find(
                    './/{http://ns.myname.com/AIContact/1.0/}LicensorName').text = creator
                root.find('.//{http://ns.myname.com/AIContact/1.0/}LicensorEmail').find(
                    './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text = email
                root.find('.//{http://ns.myname.com/AIContact/1.0/}LicensorURL').find(
                    './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text = contact
                root.find('.//{http://ns.myname.com/AIContact/1.0/}UserDefinedData').find(
                    './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text = udd
                root.find('.//{http://ns.myname.com/AILicense/1.0/}LicenseCondition').find(
                    './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text = condition
                root.find('.//{http://ns.myname.com/AILicense/1.0/}License').find(
                    './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text = license
                root.find('.//{http://ns.myname.com/AILicense/1.0/}LicenseURL').find(
                    './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text = f'www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}'
                filename = f"{license}_License.xmp"
                counter = 1
                while os.path.exists(os.path.join(path, filename)):
                    # If the file exists, modify the filename with a counter
                    counter += 1
                    filename = f"{license}_License({counter}).xmp"
                tree.write(os.path.join(path, filename))
            except:
                messagebox.showerror(title="Error: License.xmp not found",
                                     message="The License.xmp file could not be found.")
                return 0
            with open(os.path.join(path, filename), "a") as f:
                f.write("\n<?xpacket end='w'?>\n")
            with open(os.path.join(path, filename), "r+") as f:
                old = f.read()  # read everything in the file
                f.seek(0)  # rewind
                f.write("<?xpacket begin='' id='W5M0MpCehiHzreSzNTczkc9d'?>\n" + old)
            for line in fileinput.input(os.path.join(path, filename), inplace=True):
                line = line.replace("ns0", "x")
                line = line.replace("ns2", "AIContact")
                line = line.replace("ns3", "AILicense")
                sys.stdout.write(line)
            messagebox.showinfo(title=f"Success: License has been created",
                                message=f"You can find your license file under {os.path.join(path, filename)}.")

    def insert_license_picker(self):
        creator = self.entry_creator.get().strip()
        email = self.entry_email.get().strip()
        contact = self.entry_contact.get().strip()
        udd = self.entry_udd.get().strip()
        license = "AII " + license_picker
        timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")
        folder_time = datetime.datetime.now().strftime("%m-%d_%H-%M-%S")
        folder = 'AII_' + license_picker + '_' + folder_time

        condition = ""
        if 'Permitted For Training' not in license and 'Do Not Train' not in license:
            condition = "Training is allowed when:"
            if 'BY' in license:
                condition += " Attribution is given;"
            if 'NC' in license:
                condition += " Use is non-commercial;"
            if 'NG' in license:
                condition += " Use is non-generative;"

        directory = os.path.dirname(filenames_picker[0])
        path = os.path.join(directory, folder)
        try:
            os.mkdir(path)
        except:
            pass
        filename_error = False
        for image in filenames_picker:
            if image and allowed_file(image):
                shutil.copy(image, path)
            else:
                filename_error = True
        if filename_error == True:
            messagebox.showwarning(title="Warning: Invalid Filetype",
                                   message=f'You have selected an invalid file type.\nCurrently supported file types are: {ALLOWED_EXTENSIONS}\nThe remaining files will still be licensed.')
        try:
            with exiftool.ExifTool(executable=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/exiftool.exe', config_file=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/License.config') as et:
                if license == 'AII Do Not Train':
                    et.execute(
                        f'-EXIF:Copyright=Do Not Train',
                        f'-IPTC:CopyrightNotice=Do Not Train',
                        f'-XMP-AIContact:LicensorName={creator}', f'-XMP-AIContact:LicensorEmail={email}', f'-XMP-AIContact:LicensorURL={contact}',
                        f'-XMP-AIContact:UserDefinedData={udd}', f'-XMP-AILicense:LicensingDate={timestamp}',
                        f'-XMP-AILicense:License={license}', f'-XMP-AILicense:LicenseURL=www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}',
                        f'-XMP-AILicense:LicenseCondition={condition}', '-overwrite_original', f'{path}/.')
                else:
                    et.execute(
                        f'-EXIF:Copyright=This work is licensed for AI use under the {license}-License',
                        f'-IPTC:CopyrightNotice=This work is licensed for AI use under the {license}-License',
                        f'-XMP-AIContact:LicensorName={creator}', f'-XMP-AIContact:LicensorEmail={email}', f'-XMP-AIContact:LicensorURL={contact}',
                        f'-XMP-AIContact:UserDefinedData={udd}', f'-XMP-AILicense:LicensingDate={timestamp}',
                        f'-XMP-AILicense:License={license}', f'-XMP-AILicense:LicenseURL=www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}',
                        f'-XMP-AILicense:LicenseCondition={condition}', '-overwrite_original', f'{path}/.')
        except:
            messagebox.showerror(title="Error: ExifTool not found",
                                 message="The ExifTool application or configuration file could not be found.")
            return 0
        self.licensing_done.configure(
            text=f"Done. You can find the licensed image(s) under: {path}")

    def insert_license_tool(self):
        aiilicenses = ['AII BY', 'AII NC', 'AII NG', 'AII BY-NC', 'AII BY-NG',
                       'AII NC-NG', 'AII BY-NC-NG', 'AII Permitted For Training', 'AII Do Not Train']
        try:
            tree = ET.parse(licensename)
            root = tree.getroot()
            creator = root.find(
                './/{http://ns.myname.com/AIContact/1.0/}LicensorName').text
            if creator == None:
                creator = ''
            email = root.find('.//{http://ns.myname.com/AIContact/1.0/}LicensorEmail').find(
                './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text
            if email == None:
                email = ''
            udd = root.find('.//{http://ns.myname.com/AIContact/1.0/}UserDefinedData').find(
                './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text
            if udd == None:
                udd = ''
            contact = root.find('.//{http://ns.myname.com/AIContact/1.0/}LicensorURL').find(
                './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text
            if contact == None:
                contact = ''
            condition = root.find('.//{http://ns.myname.com/AILicense/1.0/}LicenseCondition').find(
                './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text
            license = root.find('.//{http://ns.myname.com/AILicense/1.0/}License').find(
                './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text
            if license not in aiilicenses:
                raise Exception('Wrong license')
            licenseURL = root.find('.//{http://ns.myname.com/AILicense/1.0/}LicenseURL').find(
                './/{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text
        except:
            messagebox.showerror(title="Error: Invalid License",
                                 message="The xmp file provided does not contain a valid license.")
            return 0
        condition = ""
        if 'Permitted For Training' not in license and 'Do Not Train' not in license:
            condition = "Training is allowed when:"
            if 'BY' in license:
                condition += " Attribution is given;"
            if 'NC' in license:
                condition += " Use is non-commercial;"
            if 'NG' in license:
                condition += " Use is non-generative;"
        timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")
        folder_time = datetime.datetime.now().strftime("%m-%d_%H-%M-%S")
        folder = license + '_' + folder_time
        directory = os.path.dirname(filenames_tool[0])
        path = os.path.join(directory, folder)
        try:
            os.mkdir(path)
        except:
            pass
        filename_error = False
        for image in filenames_tool:
            if image and allowed_file(image):
                shutil.copy(image, path)
            else:
                filename_error = True
        if filename_error == True:
            messagebox.showwarning(title="Warning: Invalid Filetype",
                                   message=f'You have selected an invalid file type.\nCurrently supported file types are: {ALLOWED_EXTENSIONS}\nThe remaining files will still be licensed.')
        try:
            with exiftool.ExifTool(executable=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/exiftool.exe', config_file=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/License.config') as et:
                if license == 'AII Do Not Train':
                    et.execute(
                        f'-EXIF:Copyright=Do Not Train',
                        f'-IPTC:CopyrightNotice=Do Not Train',
                        f'-XMP-AIContact:LicensorName={creator}', f'-XMP-AIContact:LicensorEmail={email}', f'-XMP-AIContact:LicensorURL={contact}',
                        f'-XMP-AIContact:UserDefinedData={udd}', f'-XMP-AILicense:LicensingDate={timestamp}',
                        f'-XMP-AILicense:License={license}', f'-XMP-AILicense:LicenseURL=www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}',
                        f'-XMP-AILicense:LicenseCondition={condition}', '-overwrite_original', f'{path}/.')
                else:
                    et.execute(
                        f'-EXIF:Copyright=This work is licensed for AI use under the {license}-License',
                        f'-IPTC:CopyrightNotice=This work is licensed for AI use under the {license}-License',
                        f'-XMP-AIContact:LicensorName={creator}', f'-XMP-AIContact:LicensorEmail={email}', f'-XMP-AIContact:LicensorURL={contact}',
                        f'-XMP-AIContact:UserDefinedData={udd}', f'-XMP-AILicense:LicensingDate={timestamp}',
                        f'-XMP-AILicense:License={license}', f'-XMP-AILicense:LicenseURL=www.aiilicense.com/licenses/{"".join(license.replace(" ", "-"))[4:].lower()}',
                        f'-XMP-AILicense:LicenseCondition={condition}', '-overwrite_original', f'{path}/.')
        except:
            messagebox.showerror(title="Error: ExifTool not found",
                                 message="The ExifTool application or configuration file could not be found.")
            return 0
        self.licensing_done_tool.configure(
            text=f"Done. You can find the licensed image(s) under: {path}")

    def select_frame_by_name(self, name):
        # set button color for selected button
        picker_frames = ["license_picker_frame", "allow_use_frame", "attribution_frame",
                         "non_commercial_frame", "non_generative_frame", "add_info", "licensing"]
        self.license_picker_button.configure(
            fg_color=("gray75", "gray25") if name in picker_frames else "transparent")
        self.licensing_tool_button.configure(
            fg_color=("gray75", "gray25") if name == "licensing_tool" else "transparent")

        # show selected frame
        if name == "license_picker_frame":
            self.license_picker_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.license_picker_frame.grid_forget()
        if name == "allow_use_frame":
            self.allow_use_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.allow_use_frame.grid_forget()
        if name == "attribution_frame":
            self.attribution_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.attribution_frame.grid_forget()
        if name == "non_commercial_frame":
            self.non_commercial_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.non_commercial_frame.grid_forget()
        if name == "non_generative_frame":
            self.non_generative_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.non_generative_frame.grid_forget()
        if name == "licensing_tool":
            self.licensing_tool_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.licensing_tool_frame.grid_forget()
        if name == "add_info":
            self.add_info_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.add_info_frame.grid_forget()
        if name == "licensing":
            self.licensing_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.licensing_frame.grid_forget()

    def license_picker_back_event(self):
        self.select_frame_by_name("license_picker_frame")

    def license_picker_button_event(self):
        global license_picker
        license_picker = ""
        if self.license_picker_radiobutton_var.get() == 1:
            self.select_frame_by_name("license_picker_frame")
        elif self.allow_use_radiobutton_var.get() == 2:
            self.select_frame_by_name("allow_use_frame")
        else:
            self.select_frame_by_name("non_generative_frame")

    def licensing_tool_button_event(self):
        self.select_frame_by_name("licensing_tool")

    def choose_license_button_event(self):
        global license_picker
        if self.license_picker_radiobutton_var.get() == 1:
            license_picker = self.license_picker_license_select.get()
            if license_picker != 'Choose a License':
                self.label_license.configure(text=license_picker)
                self.label_license_tool.configure(text=license_picker)
                self.select_frame_by_name("add_info")
        else:
            license_picker = ""
            self.select_frame_by_name("allow_use_frame")

    def licensing_frame_button_event(self):
        if "BY" in license_picker:
            if self.entry_creator.get() != '' or self.entry_email.get() != '' or self.entry_contact.get() != '':
                self.select_frame_by_name('licensing')
        else:
            self.select_frame_by_name('licensing')

    def attribution_frame_button_event(self):
        selected_option = self.allow_use_radiobutton_var.get()
        global license_picker
        if selected_option == 2:
            license_picker = "Do Not Train"
            self.label_license.configure(text=license_picker)
            self.label_license_tool.configure(text=license_picker)
            self.select_frame_by_name("add_info")
        else:
            self.select_frame_by_name("attribution_frame")

    def non_commercial_frame_button_event(self):
        self.select_frame_by_name("non_commercial_frame")

    def non_generative_frame_button_event(self):
        self.select_frame_by_name("non_generative_frame")

    def add_info_frame_button(self):
        global license_picker
        if license_picker == "":
            if self.attribution_radiobutton_var.get() == 1:
                license_picker += 'BY'
            if self.non_commercial_radiobutton_var.get() == 2:
                if len(license_picker) > 1:
                    license_picker += '-NC'
                else:
                    license_picker += 'NC'
            if self.non_generative_radiobutton_var.get() == 2:
                if len(license_picker) > 1:
                    license_picker += '-NG'
                else:
                    license_picker += 'NG'
            if len(license_picker) < 1:
                license_picker += 'Permitted For Training'
        self.label_license.configure(text=license_picker)
        self.label_license_tool.configure(text=license_picker)
        self.select_frame_by_name("add_info")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    app = App()
    app.mainloop()
