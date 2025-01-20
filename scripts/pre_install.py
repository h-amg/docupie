# pre_install.py

import subprocess
import sys
import platform


def run_command(command):
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        result.check_returncode()
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.stderr.strip())


def install_package(command, package_name):
    try:
        output = run_command(command)
        print(output)
        return output
    except RuntimeError as e:
        raise RuntimeError(f"Failed to install {package_name}: {e}")


def check_and_install():
    try:
        # Check and install Ghostscript
        try:
            run_command("gs --version")
        except RuntimeError:
            if platform.system() == "Darwin":  # macOS
                install_package("brew install ghostscript", "Ghostscript")
            elif platform.system() == "Linux":  # Linux
                install_package(
                    "sudo apt-get update && sudo apt-get install -y ghostscript",
                    "Ghostscript",
                )
            else:
                raise RuntimeError(
                    "Please install Ghostscript manually from https://www.ghostscript.com/releases/gsdnld.html"
                )

        # Check and install GraphicsMagick
        try:
            run_command("gm version")
        except RuntimeError:
            if platform.system() == "Darwin":  # macOS
                install_package("brew install graphicsmagick", "GraphicsMagick")
            elif platform.system() == "Linux":  # Linux
                install_package(
                    "sudo apt-get update && sudo apt-get install -y graphicsmagick",
                    "GraphicsMagick",
                )
            else:
                raise RuntimeError(
                    "Please install GraphicsMagick manually from http://www.graphicsmagick.org/download.html"
                )

    except RuntimeError as err:
        print(f"Error during installation: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    check_and_install()