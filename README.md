# Nautilus Image Toolkit

A Nautilus extension to provide simple image manipulation actions like converting formats and removing backgrounds.

## Dependencies

This extension requires ImageMagick, `nautilus-python` and the Python GObject libraries. Please install them using your system's package manager before installing the extension.

**On Fedora / Red Hat:**

```bash
sudo dnf install imagemagick python3-gobject nautilus-python
```

**On Ubuntu / Debian:**

```bash
sudo apt install imagemagick python3-gi nautilus-python
```

**On Arch Linux:**

```bash
sudo pacman -S imagemagick python-gobject nautilus-python
```

## Installation

To install the Nautilus Image Toolkit, clone the repository and run the setup script:

```bash
git clone https://github.com/weltonfelix/nautilus-image-toolkit.git
cd nautilus-image-toolkit
```

```bash
chmod +x install.sh
./install.sh
```

And then restart Nautilus:

```bash
nautilus -q
```

### Manual Installation

If you prefer to install manually, copy the `ImageToolkitExtension.py` file to your Nautilus extensions directory, which is typically located at `~/.local/share/nautilus-python/extensions/`. You can create this directory if it does not exist:

```bash
mkdir -p ~/.local/share/nautilus-python/extensions/
cp ImageToolkitExtension.py ~/.local/share/nautilus-python/extensions/
```

## Uninstallation

To uninstall the Nautilus Image Toolkit, you can run the uninstall script:

```bash
chmod +x uninstall.sh
./uninstall.sh
```

### Manual Uninstallation

If you prefer to uninstall manually, simply remove the `ImageToolkitExtension.py` file from your Nautilus extensions directory:

```bash
rm ~/.local/share/nautilus-python/extensions/ImageToolkitExtension.py
```

## Usage

Once installed, you can right-click on an image file in Nautilus to access the context menu options provided by the Nautilus Image Toolkit. The available actions include:

- Convert image formats (e.g., PNG to JPEG)
- Remove backgrounds from images

## Development

If you want to contribute to the Nautilus Image Toolkit, you can set up a development environment by cloning the repository and installing the required dependencies. Make sure you have Python 3 and pip installed.

### Development Dependencies

**Fedora / Red Hat:**

```bash
sudo dnf install cairo-devel nautilus-python python3-gobject gcc gobject-introspection-devel cairo-gobject-devel pkg-config python3-devel gtk4
```

**Ubuntu / Debian:**

```bash
sudo apt install libcairo2-dev python3-gi nautilus-python gcc gir1.2-gtk-4.0 python3-gobject-2.0 pkg-config python3-dev
```

**Arch Linux:**

```bash
sudo pacman -S cairo nautilus-python python-gobject gcc gtk4
```

And then install the Python dependencies:

```bash
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

If you would like to contribute to the Nautilus Image Toolkit, please fork the repository and submit a pull request. Contributions are welcome!

## Issues

If you encounter any issues or have feature requests, please open an issue on the GitHub repository. We appreciate your feedback and contributions to improve the Nautilus Image Toolkit.
