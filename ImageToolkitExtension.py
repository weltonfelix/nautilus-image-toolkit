import os
from pathlib import Path
import threading
from typing import Optional, Callable
import gi
import subprocess

gi.require_version("Notify", "0.7")
from gi.repository import Nautilus, GObject, Notify, GLib
from urllib.parse import unquote, urlparse


class Notifier:
    """A simple notifier class to handle notifications."""

    def __init__(self):
        Notify.init("ImageToolkitExtension")

    def _show_notification(self, title: str, message: str, icon: str):
        """The actual notification logic that must run on the main thread."""
        notification = Notify.Notification.new(title, message, icon)
        notification.show()

    def notify_info(self, title: str, message: str):
        """Schedules an informational notification to be shown on the main thread."""
        GLib.idle_add(self._show_notification, title, message, "dialog-information")

    def notify_error(self, title: str, message: str):
        """Schedules an error notification to be shown on the main thread."""
        GLib.idle_add(self._show_notification, title, message, "dialog-error")


class ImageHelperCommand:
    """Base class for image manipulation commands using ImageMagick."""

    def __init__(self, file_uri: str, notifier: Optional[Notifier] = None):
        self.file_path = unquote(urlparse(file_uri).path)
        self.notifier = notifier if notifier else Notifier()

    def get_file(self) -> str:
        """Return the file name from the file path."""
        return os.path.basename(self.file_path)

    def get_file_directory(self) -> str:
        """Return the directory of the file."""
        return os.path.dirname(self.file_path)

    def get_name(self) -> str:
        """Return the name of the file without its extension."""
        return os.path.splitext(self.get_file())[0]

    def get_extension(self) -> str:
        """Return the file extension in lowercase."""
        return os.path.splitext(self.get_file())[1].lower()

    def get_file_name(self) -> str:
        """Return the file name without the directory path."""
        return self.file_path.split("/")[-1]

    def execute(self):
        """Execute the command. This method should be implemented by subclasses."""
        raise NotImplementedError("Subclasses should implement this method")

    def _generate_output_path(self, name: str, extension: str) -> str:
        """Generate a unique output path for the converted image."""
        output_path = os.path.join(self.get_file_directory(), f"{name}{extension}")

        # Ensure the output path is unique
        # by appending a number if the file already exists
        if os.path.exists(output_path):
            base, ext = os.path.splitext(output_path)
            i = 1
            while os.path.exists(output_path):
                output_path = f"{base} ({i}){ext}"
                i += 1
        return output_path

    def _run(
        self,
        command: list[str],
        output_path: str,
        on_success: Optional[Callable] = None,
    ):
        """Run the ImageMagick command in a separate thread."""

        thread = threading.Thread(
            target=self._runner, args=[command, output_path, on_success]
        )
        thread.start()

    def _runner(
        self,
        command: list[str],
        output_path: str,
        on_success: Optional[Callable] = None,
    ):
        """Run the command and handle exceptions."""
        try:
            proc = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = proc.communicate()
            if proc.returncode != 0:
                # If the command failed, raise an error with the output
                output = stdout.decode("utf-8") if stdout else ""
                stderr = stderr.decode("utf-8") if stderr else ""
                self.notifier.notify_error(
                    "ImageMagick Error",
                    f"Command failed with error:\n{stderr}\nOutput:\n{output}",
                )
                raise subprocess.CalledProcessError(
                    proc.returncode, command, output=stdout, stderr=stderr
                )

        except FileNotFoundError:
            self.notifier.notify_error(
                "ImageMagick Not Found",
                "Please install ImageMagick to use this feature.",
            )
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode("utf-8", errors="ignore").strip()
            self.notifier.notify_error(
                "ImageMagick Failed",
                f"Error processing {self.input_path.name}: {error_message}",
            )
        else:
            if on_success:
                GLib.idle_add(on_success)


class ConvertToPngCommand(ImageHelperCommand):
    """Command to convert an image to PNG format using ImageMagick."""

    def execute(self, on_success: Optional[Callable] = None):
        output_path = self._generate_output_path(self.get_name(), ".png")
        # Use ImageMagick's convert command to convert the image to PNG
        command = [
            "magick",
            self.file_path,
            output_path,
        ]

        self._run(command, output_path, on_success)


class ConvertToJpegCommand(ImageHelperCommand):
    """Command to convert an image to JPEG format using ImageMagick."""

    def execute(self, on_success: Optional[Callable] = None):
        output_path = self._generate_output_path(self.get_name(), ".jpg")
        # Use ImageMagick's convert command to convert the image to JPEG
        command = [
            "magick",
            self.file_path,
            output_path,
        ]

        self._run(command, output_path, on_success)


class RemoveWhiteBackgroundCommand(ImageHelperCommand):
    """Command to remove the white background from an image using ImageMagick."""

    def execute(self, on_success: Optional[Callable] = None):
        output_path = self._generate_output_path(f"{self.get_name()}-no-bg", ".png")
        # Use ImageMagick's convert command to remove the background
        command = [
            "magick",
            self.file_path,
            "-fuzz",
            "20%",
            "-transparent",
            "white",
            output_path,
        ]

        self._run(command, output_path, on_success)


def all_files_are_images(files: list) -> bool:
    """Check if all selected files are images."""
    return all(["image/" in file.get_mime_type() for file in files])


def is_jpeg(file) -> bool:
    """Check if the file is a JPEG image."""
    return file.get_mime_type() == "image/jpeg" or file.get_mime_type() == "image/jpg"


def is_png(file) -> bool:
    """Check if the file is a PNG image."""
    return file.get_mime_type() == "image/png"


class ImageToolkitExtension(GObject.GObject, Nautilus.MenuProvider):
    """Nautilus extension for image manipulation using ImageMagick."""

    def __init__(self):
        super().__init__()
        Notify.init("ImageToolkitExtension")

    def get_file_items(self, files) -> Optional[list[Nautilus.MenuItem]]:
        """Return a list of menu items for the selected files."""
        if not all_files_are_images(files):
            return

        # Ensure that only one file is selected
        if len(files) != 1:
            return

        file = files[0]
        self.notifier = Notifier()

        top_menuitem = Nautilus.MenuItem(
            name="ImageToolkitExtension::Convert",
            label="Convert Image",
            tip="Convert the selected image to another format",
            icon="image-x-generic",
        )

        submenu = Nautilus.Menu()

        if not is_png(file):
            convert_to_png_item = Nautilus.MenuItem(
                name="ImageToolkitExtension::ConvertImageToPng",
                label="Convert to PNG",
                tip="Convert the selected image to PNG format",
                icon="",
            )
            convert_to_png_item.connect("activate", self.convert_image_to_png, file)
            submenu.append_item(convert_to_png_item)

        if not is_jpeg(file):
            convert_to_jpeg_item = Nautilus.MenuItem(
                name="ImageToolkitExtension::ConvertImageToJpeg",
                label="Convert to JPEG",
                tip="Convert the selected image to JPEG format",
                icon="",
            )
            convert_to_jpeg_item.connect("activate", self.convert_image_to_jpeg, file)
            submenu.append_item(convert_to_jpeg_item)

        remove_white_background_item = Nautilus.MenuItem(
            name="ImageToolkitExtension::RemoveWhiteBackground",
            label="Remove White Background",
            tip="Remove the white background from the selected image",
            icon="",
        )
        remove_white_background_item.connect(
            "activate", self.remove_white_background, file
        )

        top_menuitem.set_submenu(submenu)

        return [top_menuitem, remove_white_background_item]

    def convert_image_to_png(self, menu_item, file):
        """Convert the selected image to PNG format."""
        command = ConvertToPngCommand(file.get_uri(), notifier=self.notifier)
        command.execute(
            on_success=lambda: self.notifier.notify_info(
                "Image Conversion",
                f"Converted {command.get_file_name()} to PNG format.",
            ),
        )

    def convert_image_to_jpeg(self, menu_item, file):
        """Convert the selected image to JPEG format."""
        command = ConvertToJpegCommand(file.get_uri(), notifier=self.notifier)
        command.execute(
            on_success=lambda: self.notifier.notify_info(
                "Image Conversion",
                f"Converted {command.get_file_name()} to JPEG format.",
            )
        )

    def remove_white_background(self, menu_item, file):
        """Remove the white background from the selected image."""
        command = RemoveWhiteBackgroundCommand(file.get_uri(), notifier=self.notifier)
        command.execute(
            on_success=lambda: self.notifier.notify_info(
                "White Background Removal",
                f"Removed white background from {command.get_file_name()}.",
            )
        )
