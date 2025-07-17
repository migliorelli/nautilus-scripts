import gi

gi.require_version("Nautilus", "4.0")

from gi.repository import Nautilus, GObject


class OpenWithCodeExtension(GObject.GObject, Nautilus.MenuProvider):
    def launch_with_code(self, menu, files):
        import subprocess

        paths = [f.get_location().get_path() for f in files]
        subprocess.Popen(["code"] + paths)

    def get_file_items(self, files):
        if not files:
            return []

        item = Nautilus.MenuItem(
            name="OpenWithCodeExtension::OpenWithCode",
            label="Open with Code",
            tip="Open the selected file(s) with Visual Studio Code",
        )

        item.connect("activate", self.launch_with_code, files)
        return [item]

    def get_background_items(self, current_dir):
        item = Nautilus.MenuItem(
            name="OpenWithCodeExtension::OpenCurrntFolderWithCode",
            label="Open folder with Code",
            tip="Open current folder with Visual Studio Code",
        )

        item.connect("activate", self.launch_with_code, [current_dir])

        return [item]
