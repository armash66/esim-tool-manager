import threading
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

from config import load_config, save_config
from dependency import DependencyChecker, DependencyState
from logger import get_logger
from platform_adapter import get_platform_adapter
from registry import get_all_detectors, get_detector, get_installer, get_updater, list_tools, TOOLS

logger = get_logger()


class ESimToolManagerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("eSim Tool Manager — Desktop GUI")
        self.root.geometry("820x580")
        self.root.minsize(700, 480)

        self.checker = DependencyChecker()
        self.adapter = get_platform_adapter()

        self._setup_ui()
        self.refresh_status()

    def _setup_ui(self):
        # Top Header Frame
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill=tk.X)

        title = ttk.Label(
            header,
            text="eSim Tool Manager",
            font=("Segoe UI" if self.adapter.get_name() == "Windows" else "DejaVu Sans", 16, "bold"),
        )
        title.pack(side=tk.LEFT)

        platform_lbl = ttk.Label(
            header,
            text=f"Platform: {self.adapter.get_name()}",
            font=("Segoe UI" if self.adapter.get_name() == "Windows" else "DejaVu Sans", 10, "italic"),
        )
        platform_lbl.pack(side=tk.LEFT, padx=15)

        refresh_btn = ttk.Button(header, text="🔄 Refresh", command=self.refresh_status)
        refresh_btn.pack(side=tk.RIGHT)

        # Status Summary Frame
        self.status_bar = ttk.Frame(self.root, padding=(10, 5))
        self.status_bar.pack(fill=tk.X)

        self.status_lbl = ttk.Label(
            self.status_bar,
            text="Environment Status: Checking...",
            font=("Segoe UI" if self.adapter.get_name() == "Windows" else "DejaVu Sans", 11, "bold"),
        )
        self.status_lbl.pack(side=tk.LEFT)

        # Tools Treeview Table
        table_frame = ttk.Frame(self.root, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "category", "status", "version", "path")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        self.tree.heading("name", text="Tool")
        self.tree.heading("category", text="Category")
        self.tree.heading("status", text="Status")
        self.tree.heading("version", text="Installed Version")
        self.tree.heading("path", text="Path")

        self.tree.column("name", width=110, anchor=tk.W)
        self.tree.column("category", width=100, anchor=tk.W)
        self.tree.column("status", width=120, anchor=tk.W)
        self.tree.column("version", width=120, anchor=tk.W)
        self.tree.column("path", width=330, anchor=tk.W)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Actions Button Toolbar
        toolbar = ttk.Frame(self.root, padding=10)
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="🩺 Doctor Diagnostics", command=self.run_doctor).pack(side=tk.LEFT, padx=5)
        self.install_btn = ttk.Button(toolbar, text="📥 Install Selected Tool", command=self.install_selected)
        self.install_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="🔄 Check Updates", command=self.check_updates).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="🌐 Path Environment", command=self.show_path_env).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="⚙️ Configuration", command=self.show_config).pack(side=tk.RIGHT, padx=5)

        # Activity Output Log Window
        log_frame = ttk.LabelFrame(self.root, text="Activity Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.log_text = tk.Text(log_frame, height=6, state=tk.DISABLED, wrap=tk.WORD)
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscroll=log_scroll.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def log(self, message: str):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        logger.info(f"GUI: {message}")

    def refresh_status(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        report = self.checker.check_all()
        core_missing = False

        for tool_name, info in TOOLS.items():
            status = report["tools"].get(tool_name)
            if not status:
                continue

            name = info["name"]
            category = info["category"]
            has_installer = bool(get_installer(tool_name))

            if status.state == DependencyState.INSTALLED:
                st_text = "✓ Installed"
                ver_text = status.version if status.version else "(unavailable)"
                path_text = status.path if status.path else ""
            elif status.state == DependencyState.BROKEN:
                st_text = "⚠ Broken"
                ver_text = status.version if status.version else "-"
                path_text = status.path if status.path else ""
                if has_installer:
                    core_missing = True
            elif status.state == DependencyState.NOT_INSTALLED:
                st_text = "✗ Not installed" if has_installer else "○ Unmanaged"
                ver_text = "-"
                path_text = ""
                if has_installer:
                    core_missing = True
            else:
                st_text = "○ Unmanaged"
                ver_text = "-"
                path_text = ""

            self.tree.insert("", tk.END, values=(name, category, st_text, ver_text, path_text))

        if not core_missing:
            self.status_lbl.config(text="Overall Core Status: READY", foreground="green")
        else:
            self.status_lbl.config(text="Overall Core Status: NOT READY", foreground="red")

        self.log("Status refreshed.")

    def run_doctor(self):
        self.log("Running Doctor Diagnostics...")
        report = self.checker.check_all()
        msg_lines = ["eSim Environment Doctor Diagnostics\n"]
        for t_name, status in report["tools"].items():
            msg_lines.append(f"{status.name}: {status.state} (version={status.version or 'N/A'}, on_path={status.is_on_path})")

        env = report["environment"]
        msg_lines.append(f"\nInstall Dir: {env['install_dir_path']} (exists={env['install_dir_exists']})")
        messagebox.showinfo("Doctor Diagnostics", "\n".join(msg_lines))

    def install_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a tool from the table first.")
            return

        raw_val = str(self.tree.item(selected[0])["values"][0]).strip()
        tool_name = raw_val.lower()
        installer = get_installer(tool_name)
        if not installer:
            messagebox.showinfo("Unmanaged Tool", f"Installation workflow for {raw_val} is not managed.")
            return

        self.install_btn.config(state=tk.DISABLED)
        self.log(f"Starting installation for {raw_val}...")

        def _do_install():
            try:
                success = installer.install()
                if success:
                    self.log(f"Installation of {raw_val} completed successfully.")
                    self.root.after(0, lambda: messagebox.showinfo("Installation Complete", f"{raw_val} installation completed successfully."))
                    self.root.after(0, self.refresh_status)
                else:
                    self.log(f"Installation of {raw_val} failed.")
                    self.root.after(0, lambda: messagebox.showerror("Installation Failed", f"Installation of {raw_val} failed. Check log for details."))
            finally:
                self.root.after(0, lambda: self.install_btn.config(state=tk.NORMAL))

        threading.Thread(target=_do_install, daemon=True).start()

    def check_updates(self):
        self.log("Checking updates for managed tools...")
        results = []
        for tool_name, info in TOOLS.items():
            updater = get_updater(tool_name)
            if updater:
                st = updater.check_update()
                status_msg = "Up to date" if not st["needs_update"] else f"Update available: {st['latest_version']}"
                results.append(f"{info['name']}: {status_msg}")
            else:
                results.append(f"{info['name']}: Update check unmanaged")

        messagebox.showinfo("Updates Status", "\n".join(results))
        self.log("Updates check complete.")

    def show_path_env(self):
        report = self.checker.check_all()
        bin_paths = []
        for t_name, status in report["tools"].items():
            if status.state == DependencyState.INSTALLED and status.path:
                bin_paths.append(str(Path(status.path).parent))

        instructions = self.adapter.format_path_instructions(bin_paths)
        messagebox.showinfo("Path Environment Instructions", instructions)

    def show_config(self):
        cfg = load_config()
        msg = f"Install Directory:\n  {cfg.get('install_directory')}\n\nAuto Update:\n  {cfg.get('auto_update')}"
        messagebox.showinfo("Configuration Settings", msg)


def launch_gui():
    root = tk.Tk()
    app = ESimToolManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
