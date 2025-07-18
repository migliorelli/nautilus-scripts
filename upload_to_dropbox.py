# This scripts needs you to define the environment variable DROPBOX_ACCESS_TOKEN in your system
# i.e export DROPBOX_ACCESS_TOKEN="your_access_token_here"

from gi.repository import Nautilus, GObject, Notify
import os
import threading
import requests as r
import json

DROPBOX_API_URL = "https://content.dropboxapi.com/2/files/upload"
DROPBOX_ACCESS_TOKEN = os.environ.get("DROPBOX_ACCESS_TOKEN")
APP_NAME = "UploadToDropbox"

Notify.init(APP_NAME)


class UploadToDropboxExtension(GObject.GObject, Nautilus.MenuProvider):
    def notify(self, title, message):
        def show_notification():
            print(f"[{APP_NAME}]: {title} - {message}")
            notification = Notify.Notification.new(title, message)
            notification.show()

        GObject.idle_add(show_notification)

    def upload_file(self, file_name, file_data):
        headers = {
            "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps(
                {
                    "path": f"/{file_name}",
                    "mode": "overwrite",
                    "autorename": True,
                    "mute": False,
                    "strict_conflict": False,
                }
            ),
        }

        response = r.post(DROPBOX_API_URL, headers=headers, data=file_data)

        if response.ok:
            self.notify("Upload OK", f"{file_name} uploaded.")
        else:
            self.notify("Error", f"Error uploading {file_name}: {response.text}")

    def process_files(self, files):
        for file in files:
            file_path = file.get_location().get_path()
            file_name = file.get_name()

            if file.is_directory():
                for root, _, filenames in os.walk(file_path):
                    for filename in filenames:
                        full_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(full_path, start=file_path)
                        server_path = os.path.join(file_name, relative_path)
                        self.upload_file(server_path, open(full_path, "rb").read())

                continue

            with open(file_path, "rb") as f:
                file_data = f.read()
                self.upload_file(file_name, file_data)

    def upload_to_dropbox(self, menu, files):
        if not files:
            return

        if not DROPBOX_ACCESS_TOKEN:
            return self.notify(
                "Dropbox Token Missing", "Set DROPBOX_ACCESS_TOKEN in your environment."
            )

        self.notify("Upload Started", f"Uploading {len(files)} file(s) to Dropbox...")

        def worker():
            self.process_files(files)

        threading.Thread(target=worker, daemon=True).start()

    def get_file_items(self, files):
        if not files:
            return []

        item = Nautilus.MenuItem(
            name="UploadToDropboxExtension::Upload",
            label="Upload to Dropbox",
            tip="Upload selected files to Dropbox",
        )

        item.connect("activate", self.upload_to_dropbox, files)

        return [item]
