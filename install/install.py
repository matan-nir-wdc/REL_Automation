import os
import subprocess
import sys
import ctypes
import urllib.request

def install_pip():
    try:
        import pip
        print("pip is already installed")
    except ImportError:
        print("Installing pip...")
        urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
        subprocess.check_call([sys.executable, "get-pip.py"])
        os.remove("get-pip.py")
        print("pip installed successfully")

def install_packages():
    print("Installing pandas and tqdm...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "tqdm"])
    print("pandas and tqdm installed successfully")

def install_msi(msi_path):
    print(f"Installing MSI file: {msi_path}...")
    subprocess.check_call(['msiexec', '/i', msi_path, '/quiet', '/norestart'])
    print("MSI file installed successfully")

def is_dotnet_installed():
    try:
        # Check the registry for .NET Framework 4.8 or above
        key = r"SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full"
        registry_key = ctypes.windll.advapi32.RegOpenKeyExW(ctypes.windll.kernel32.HKEY_LOCAL_MACHINE, key, 0, (ctypes.c_int(0x20019)))
        value, _ = ctypes.windll.advapi32.RegQueryValueExW(registry_key, "Release", 0, None, None)
        ctypes.windll.advapi32.RegCloseKey(registry_key)
        if value >= 528040:
            print(".NET Framework 4.8 or above is already installed")
            return True
        else:
            print(".NET Framework 4.8 or above is not installed")
            return False
    except Exception as e:
        print(f"Error checking .NET Framework: {e}")
        return False

def install_dotnet_framework():
    dotnet_installer_url = "https://download.visualstudio.microsoft.com/download/pr/8d9d8e6b-ecb6-4bbd-9315-8d7ebf69cabb/1c3c6f8a0a0cddeef0a5b1e4ad8c2b90/dotnetfx48_full_x86_x64.exe"
    dotnet_installer_path = "dotnetfx48_full_x86_x64.exe"
    print("Downloading .NET Framework 4.8 installer...")
    urllib.request.urlretrieve(dotnet_installer_url, dotnet_installer_path)
    print("Installing .NET Framework 4.8...")
    subprocess.check_call([dotnet_installer_path, "/quiet", "/norestart"])
    os.remove(dotnet_installer_path)
    print(".NET Framework 4.8 installed successfully")

def main():
    install_pip()
    install_packages()
    msi_path = "eMonitorSetup_7_3_6.msi"  # Replace with the path to your MSI file
    install_msi(msi_path)
    if not is_dotnet_installed():
        install_dotnet_framework()

if __name__ == "__main__":
    main()
