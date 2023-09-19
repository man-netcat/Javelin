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
        self.config.add_section("client_paths")
        self.config.add_section("game_paths")
        self.update_config()

    def setup_GUI(self):
        self.root = tk.Tk()
        self.root.title("COD Launcher")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.launcher_tab = ttk.Frame(self.notebook)
        self.options_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.launcher_tab, text="Launcher")
        self.notebook.add(self.options_tab, text="Options")

        self.setup_launcher_tab()
        self.setup_options_tab()

    def setup_launcher_tab(self):
        self.game_frames = []
        frame_index = 0

        for game, modes in options.items():
            if not self.config.get("game_paths", game, fallback=""):
                continue

            game_frame = ttk.LabelFrame(self.launcher_tab, text=game)
            game_frame.grid(
                row=frame_index // 3,
                column=frame_index % 3,
                padx=10,
                pady=5,
                sticky="nsew",
            )
            frame_index += 1

            buttons_frame = tk.Frame(game_frame)
            buttons_frame.pack(fill="both", expand=True)

            for option in modes:
                mode = option["mode"]
                button_command = lambda game=game, option=option: self.run_game(
                    game, option
                )
                tk.Button(
                    buttons_frame,
                    text=f"{game} {mode.capitalize()}",
                    width=15,
                    height=2,
                    padx=0,
                    pady=0,
                    highlightthickness=2,
                    command=button_command,
                ).pack(side="left", padx=5)

            self.game_frames.append(game_frame)

        if not self.game_frames:
            no_game_label = tk.Label(
                self.launcher_tab, text="No game added", font=("Helvetica", 12)
            )
            no_game_label.pack(fill="both", expand=True)

    def setup_options_tab(self):
        name_label = tk.Label(self.options_tab, text="Player Name:")
        name_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        player_name = self.config.get(
            "launcher", "default_name", fallback="Unknown Soldier"
        )

        player_name_stringvar = tk.StringVar(self.options_tab, value=player_name)
        self.name_entry = tk.Entry(self.options_tab, textvariable=player_name_stringvar)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        client_paths_frame = ttk.LabelFrame(self.options_tab, text="Client Paths")
        client_paths_frame.grid(
            row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew"
        )

        game_paths_frame = ttk.LabelFrame(self.options_tab, text="Game Paths")
        game_paths_frame.grid(
            row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew"
        )

        self.client_paths_entries: dict[str, ttk.Entry] = {}
        self.game_paths_entries: dict[str, ttk.Entry] = {}

        row_num = 1
        for client in ["AlterWare", "Plutonium"]:
            label = f"{client} Path:"
            path = self.config.get("client_paths", client, fallback="")
            ttk.Label(client_paths_frame, text=label).grid(
                row=row_num, column=0, padx=5, pady=2, sticky="w"
            )
            entry = ttk.Entry(client_paths_frame, width=100)
            entry.insert(0, path)
            entry.grid(row=row_num, column=1, padx=5, pady=2, sticky="ew")
            ttk.Button(
                client_paths_frame,
                text="Browse",
                command=lambda client=client: self.select_path(client),
            ).grid(row=row_num, column=2, padx=5, pady=2, sticky="ew")
            self.client_paths_entries[client] = entry
            row_num += 1

        row_num = 1
        for game, _ in options.items():
            label = f"{game} Path:"
            path = self.config.get("game_paths", game, fallback="")
            ttk.Label(game_paths_frame, text=label).grid(
                row=row_num, column=0, padx=5, pady=2, sticky="w"
            )
            entry = ttk.Entry(game_paths_frame, width=100)
            entry.insert(0, path)
            entry.grid(row=row_num, column=1, padx=5, pady=2, sticky="ew")
            ttk.Button(
                game_paths_frame,
                text="Browse",
                command=lambda game=game: self.select_path(game),
            ).grid(row=row_num, column=2, padx=5, pady=2, sticky="ew")
            self.game_paths_entries[game] = entry
            row_num += 1

        ttk.Button(self.options_tab, text="Save", command=self.save_options).grid(
            row=3, column=0, columnspan=2, padx=10, pady=5
        )

    def select_path(self, app):
        path = filedialog.askdirectory()
        if path:
            self.config.set("game_paths", app, path)
            messagebox.showinfo("Path Selected", f"Path for {app} saved: {path}")

            if app in ["AlterWare", "Plutonium"]:
                entry = self.client_paths_entries[app]
            else:
                entry = self.game_paths_entries[app]
            entry.delete(0, "end")
            entry.insert(0, path)

    def save_options(self):
        self.config.set("launcher", "default_name", self.name_entry.get())

        for client in ["AlterWare", "Plutonium"]:
            entry = self.client_paths_entries[client]
            path = entry.get()
            if path:
                self.config.set("client_paths", client, path)

        for game, _ in options.items():
            entry = self.game_paths_entries[game]
            path = entry.get()
            if path:
                self.config.set("game_paths", game, path)

        self.update_config()

        messagebox.showinfo(
            "Options Saved", "Changes have been saved to the config file."
        )

    def update_config(self):
        with open(CONFIG_FILE, "w") as file:
            self.config.write(file)

    def run_game(self, game, option):
        os.chdir(self.base_path)
        try:
            abs_mode_dir = self.config.get("game_paths", game)
        except NoOptionError as e:
            error_message = f"Failed to run the game: {e}"
            messagebox.showerror("Error", error_message)
            return

        bin_path = None
        command = None
        name = self.config.get("launcher", "default_name", fallback="Unknown Soldier")
        name_str = f' +name "{name}"'
        bots = " +set fs_mode mods/bots"
        gamemode = option["gamemode"]

        if any([x in gamemode for x in ["t4", "t5", "t6", "iw5mp"]]):
            # Plutonium
            dir_path = self.config.get("client_paths", "Plutonium")
            bin_path = os.path.join(dir_path, "bin", "plutonium-bootstrapper-win32.exe")
            os.chdir(dir_path)
            command = f'"{bin_path}" {gamemode} "{abs_mode_dir}" -lan {name_str}'
            if "mp" in gamemode:
                command += bots
        elif any([x in gamemode for x in ["iw4", "iw5", "iw6", "s1"]]):
            # Alterware
            dir_path = self.config.get("client_paths", "AlterWare")
            bin_path = os.path.join(dir_path, "alterware-launcher.exe")
            os.chdir(dir_path)
            bin = option["bin"]
            mode = option["mode"]
            command = (
                f'"{bin_path}" {bin} -p "{abs_mode_dir}" --pass "-{mode} {name_str}"'
            )
        elif "h2" in gamemode:
            # h2-mod
            game_path = self.config.get("game_paths", game)
            os.chdir(game_path)
            bin = f"{option['bin']}.exe"
            bin_path = os.path.join(game_path, bin)
            mode = option["mode"]
            command = f'"{bin_path}" -singleplayer -mod "mods/{mode}" {name_str}"'
        elif any([x in gamemode for x in ["t7", "iw7"]]):
            # ezboiii and iw7-mod
            game_path = self.config.get("game_paths", game)
            os.chdir(game_path)
            bin = f"{option['bin']}.exe"
            bin_path = os.path.join(game_path, bin)
            command = f'"{bin_path}" -launch {name_str}"'
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
            error_message = f"Failed to run the game: {e}"
            messagebox.showerror("Error", error_message)
            return

    def start(self):
        self.root.mainloop()


if __name__ == "__main__":
    launcher_gui = CODLauncherGUI()
    launcher_gui.start()
