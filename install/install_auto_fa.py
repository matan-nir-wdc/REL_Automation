import os
import subprocess
import sys
import urllib.request
import platform
import subprocess
import sys

def install_pip3():
    try:
        # Check if pip3 is already installed
        subprocess.run([sys.executable, '-m', 'pip', '--version'], check=True)
        print("pip3 is already installed.")
    except subprocess.CalledProcessError:
        print("pip3 is not installed. Installing pip3...")
        # Install pip3
        subprocess.run([sys.executable, '-m', 'ensurepip', '--default-pip'], check=True)

def install_packages():
    packages = ['tqdm', 'pandas']
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
            print(f"{package} installed successfully.")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}.")



def check_python_version():
    try:
        # Check if python3 is installed
        output = subprocess.check_output(["python3", "--version"], stderr=subprocess.STDOUT)
        version_info = output.decode().strip().split()[1]
        major, minor, _ = map(int, version_info.split('.'))

        # Check if the installed Python is 64-bit
        is_64bit = sys.maxsize > 2 ** 32
        if major == 3 and is_64bit:
            return True
        else:
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def download_python_installer(url, installer_path):
    print(f"Downloading Python installer from {url}...")
    urllib.request.urlretrieve(url, installer_path)
    print("Download complete.")


def install_python(installer_path):
    print("Starting Python installation...")
    subprocess.run([installer_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"], check=True)
    print("Python installation complete.")


def main():
    if platform.system() != "Windows":
        print("This script is intended to be run on Windows.")
        return

    python_download_url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
    installer_path = os.path.join(os.getcwd(), "python-3.12.0-amd64.exe")

    if check_python_version():
        print("Python 3 (64-bit) is already installed.")
    else:
        print("Python 3 (64-bit) is not installed. Proceeding with download and installation.")
        download_python_installer(python_download_url, installer_path)
        install_python(installer_path)
        os.remove(installer_path)
        print("Python 3.12 (64-bit) installation script completed.")


if __name__ == "__main__":
    install_pip3()
    install_packages()
    main()