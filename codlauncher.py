import os
import subprocess
import tkinter as tk
import tkinter.messagebox as messagebox
from configparser import ConfigParser, NoOptionError
from tkinter import filedialog, ttk

from codlauncher_data import *

CONFIG_FILE = "codlauncher.cfg"


class CODLauncherGUI:
    def __init__(self):
        self.config = ConfigParser()
        self.base_path = os.getcwd()
        if not self.config.read(CONFIG_FILE):
            self.setup_config()
        self.setup_GUI()

    def setup_config(self):
        self.config.add_section("launcher")
        self.config.add_section("paths")
        self.config.set("launcher", "default_name", "Unknown Soldier")
        self.update_config()

    def setup_GUI(self):
        # Constants for button properties
        BUTTON_WIDTH = 15
        BUTTON_HEIGHT = 2
        BUTTON_PADX = 10
        BUTTON_PADY = 5
        BUTTON_HIGHLIGHT_THICKNESS = 2
        BUTTONS_PER_ROW = 5

        self.root = tk.Tk()
        self.root.title("COD Launcher")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")

        self.default_name = self.config.get("launcher", "default_name")
        name_label = tk.Label(self.root, text="Player Name:")
        name_label.pack()
        name_frame = tk.Frame(self.root)
        name_frame.pack()
        self.player_name = tk.StringVar(self.root, value=self.default_name)
        name_entry = tk.Entry(name_frame, textvariable=self.player_name)
        name_entry.pack(side=tk.LEFT)
        name_button = tk.Button(
            name_frame, text="Update Name", command=self.update_name
        )
        name_button.pack(side=tk.LEFT, padx=BUTTON_PADX)

        binary_buttons_frame = tk.Frame(self.root)
        binary_buttons_frame.pack()

        alterware = tk.Button(
            binary_buttons_frame,
            text="Set AlterWare Binary",
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            highlightthickness=BUTTON_HIGHLIGHT_THICKNESS,
            command=lambda: self.add_binary(
                "alterware_binary", "alterware-launcher.exe"
            ),
        )
        alterware.grid(row=0, column=0)

        plutonium = tk.Button(
            binary_buttons_frame,
            text="Set Plutonium Binary",
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            highlightthickness=BUTTON_HIGHLIGHT_THICKNESS,
            command=lambda: self.add_binary(
                "plutonium_binary", "plutonium-bootstrapper-win32.exe"
            ),
        )
        plutonium.grid(row=0, column=1)

        path_buttons_frame = tk.Frame(self.root)
        path_buttons_frame.pack()

        i = 0
        for game in options.keys():
            button_command = lambda game=game: self.select_path(game)
            button = tk.Button(
                path_buttons_frame,
                text=f"Change {game} Path",
                width=BUTTON_WIDTH,
                height=BUTTON_HEIGHT,
                padx=BUTTON_PADX,
                pady=BUTTON_PADY,
                highlightthickness=BUTTON_HIGHLIGHT_THICKNESS,
                command=button_command,
            )
            button.grid(row=i // BUTTONS_PER_ROW, column=i % BUTTONS_PER_ROW)
            i += 1

        game_buttons_frame = tk.Frame(self.root)
        game_buttons_frame.pack()

        i = 0
        for game, modes in options.items():
            for option in modes:
                mode = option["mode"]
                button_command = lambda game=game, option=option: self.run_mode(
                    game, option
                )
                button = tk.Button(
                    game_buttons_frame,
                    text=f"{game} {mode.capitalize()}",
                    width=BUTTON_WIDTH,
                    height=BUTTON_HEIGHT,
                    padx=BUTTON_PADX,
                    pady=BUTTON_PADY,
                    highlightthickness=BUTTON_HIGHLIGHT_THICKNESS,
                    command=button_command,
                )
                button.grid(row=i // BUTTONS_PER_ROW, column=i % BUTTONS_PER_ROW)
                i += 1

        exit = tk.Button(
            self.root,
            text="Exit",
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            highlightthickness=BUTTON_HIGHLIGHT_THICKNESS,
            command=self.root.quit,
        )
        exit.pack()

    def add_binary(self, config_key, filename):
        binary_path = filedialog.askopenfilename(filetypes=[("", filename)])
        if binary_path:
            self.config.set("paths", config_key, binary_path)
            self.update_config()
            messagebox.showinfo(
                "Binary Path Added",
                f"{config_key.capitalize()} Binary Path: {binary_path}",
            )

    def select_path(self, game):
        path = filedialog.askdirectory()
        if path:
            self.save_path(game, path)
            messagebox.showinfo("Path Selected", f"Path for {game} saved: {path}")

    def save_path(self, game, path):
        self.config.set("paths", game, path)
        self.update_config()

    def update_name(self):
        self.config.set("launcher", "default_name", self.player_name.get())
        self.update_config()

    def update_config(self):
        with open(CONFIG_FILE, "w") as file:
            self.config.write(file)

    def run_mode(self, game, option):
        os.chdir(self.base_path)
        self.update_name()
        try:
            abs_mode_dir = self.config.get("paths", game)
        except NoOptionError as e:
            error_message = f"Failed to run the mode: {e}"
            messagebox.showerror("Error", error_message)
            return

        bin_path = None
        command = None
        name = f'+name "{self.player_name.get()}"'
        bots = " +set fs_mode mods/bots"
        gamemode = option["gamemode"]

        if any([x in gamemode for x in ["t4", "t5", "t6", "iw5mp"]]):
            # Plutonium
            bin_path = self.config.get("paths", "plutonium_binary")
            dir_path = os.path.dirname(bin_path)
            os.chdir(dir_path)
            command = f'"{bin_path}" {gamemode} "{abs_mode_dir}" -lan {name}'
            if "mp" in gamemode:
                command += bots
        elif any([x in gamemode for x in ["iw4", "iw5", "iw6", "s1"]]):
            # Alterware
            bin_path = self.config.get("paths", "alterware_binary")
            mod = option["mod-flag"]
            mode = option["mode"]
            command = f'"{bin_path}" {mod} -p "{abs_mode_dir}" --pass "-{mode} {name}"'
        elif gamemode == "h2sp":
            # h2-mod
            h2_path = self.config.get("paths", "h2")
            os.chdir(h2_path)
            bin_path = os.path.join(h2_path, "h2-mod.exe")
            command = f'"{bin_path}" -singleplayer {name}"'
        elif gamemode == "t7":
            # ezboiii
            t7_path = self.config.get("paths", "t7")
            os.chdir(t7_path)
            bin_path = os.path.join(t7_path, "boiii.exe")
            command = f'"{bin_path}" -launch {name}"'
        else:
            error_message = f"Invalid input: {gamemode}"
            messagebox.showerror("Error", error_message)
            return

        if not os.path.isfile(bin_path):
            error_message = f"binary not found: {bin_path}"
            messagebox.showerror("Error", error_message)
            return

        try:
            print(command)
            process = subprocess.run(command, shell=True)
        except subprocess.CalledProcessError as e:
            error_message = f"Failed to run the mode: {e}"
            messagebox.showerror("Error", error_message)
            return

    def start(self):
        self.root.mainloop()


if __name__ == "__main__":
    launcher_gui = CODLauncherGUI()
    launcher_gui.start()
