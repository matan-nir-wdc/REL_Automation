# Check if pip3 is installed
if (-not (Get-Command pip3 -ErrorAction SilentlyContinue)) {
    Write-Host "pip3 is not installed. Installing pip3..."
    # Install pip3 using PowerShell's invoke-expression
    Invoke-Expression "python3 -m ensurepip"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install pip3. Please make sure python3 is installed and try again."
        exit 1
    }
    else {
        Write-Host "pip3 installed successfully."
    }
}
else {
    Write-Host "pip3 is already installed."
}

# Install packages using pip3
$packages = @("tqdm", "pandas")
foreach ($package in $packages) {
    Write-Host "Installing $package..."
    # Use pip3 to install the package
    pip3 install $package
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install $package."
    }
    else {
        Write-Host "$package installed successfully."
    }
}

:eof
