# PowerShell script for efficient deployment - only copies changed files

# Settings
$RemoteUser = "root"
$RemoteHost = "192.168.1.129"
$RemoteDir = "/repository/newtoncuff.com"
$SSHKey = "$env:USERPROFILE\.ssh\id_ed25519"
$ProjectName = "newtoncuff"

# Create a manifest file of current files with their last modified times
$manifestPath = "$env:TEMP\deployment_manifest.json"
Write-Host "Using SCP with timestamp tracking for efficient transfers..." -ForegroundColor Cyan

# If a previous manifest exists, load it
$previousManifest = @{}
if (Test-Path $manifestPath) {
    Write-Host "Loading previous deployment manifest..." -ForegroundColor Cyan
    # Convert the JSON to hashtable without using -AsHashtable (for compatibility)
    $jsonContent = Get-Content $manifestPath -Raw | ConvertFrom-Json
    foreach ($property in $jsonContent.PSObject.Properties) {
        $previousManifest[$property.Name] = $property.Value
    }
}

# Build new manifest
$currentManifest = @{}
$changedFiles = @()

Write-Host "Scanning for changed files..." -ForegroundColor Cyan
# Process all files, excluding .git and node_modules
Get-ChildItem -Recurse -Exclude ".git","node_modules" | 
    Where-Object { -not ($_.FullName -like "*\.git\*" -or $_.FullName -like "*\node_modules\*") } | 
    ForEach-Object {
        # Get path relative to current directory
        $relativePath = $_.FullName.Substring($PWD.Path.Length + 1).Replace("\", "/")
        
        if (-not $_.PSIsContainer) {
            $lastWrite = (Get-Item $_.FullName).LastWriteTimeUtc.ToString("o")
            $currentManifest[$relativePath] = $lastWrite
            
            # Check if file is new or modified
            if (-not $previousManifest.ContainsKey($relativePath) -or 
                $previousManifest[$relativePath] -ne $lastWrite) {
                $changedFiles += $_
            }
        }
    }

# Save current manifest for next time
$currentManifest | ConvertTo-Json | Set-Content -Path $manifestPath

Write-Host "Found $($changedFiles.Count) changed files to transfer" -ForegroundColor Green

# Copy only changed files
foreach ($file in $changedFiles) {
    # Get the file's path relative to the current directory
    $relativePath = $file.FullName.Substring($PWD.Path.Length + 1).Replace("\", "/")
    
    # Build the remote directory path properly
    $parentDir = Split-Path -Parent $relativePath
    if ($parentDir) {
        $remoteParentDir = "$RemoteDir/$parentDir"
        
        # Create remote directory
        $mkdirCommand = "ssh -i `"$SSHKey`" $RemoteUser@$RemoteHost `"mkdir -p '$remoteParentDir'`""
        Write-Host "Creating directory: $remoteParentDir" -ForegroundColor Cyan
        Invoke-Expression $mkdirCommand
    }
    
    # Copy the file with proper path handling
    $remotePath = "$RemoteDir/$relativePath"
    Write-Host "Copying file: $relativePath to $remotePath" -ForegroundColor Cyan
    
    $scpCommand = "scp -i `"$SSHKey`" `"$($file.FullName)`" `"${RemoteUser}@${RemoteHost}:$remotePath`""
    Invoke-Expression $scpCommand
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error copying file $relativePath. Exit code: $LASTEXITCODE" -ForegroundColor Red
    }
}

# ---- SSH into remote server and run Docker Compose ----
$SshCommand = "ssh -i `"$SSHKey`" $RemoteUser@$RemoteHost 'cd $RemoteDir && docker compose -p $ProjectName up -d'"
Write-Host "Running: $SshCommand" -ForegroundColor Green
Invoke-Expression $SshCommand

Write-Host "Deployment completed!" -ForegroundColor Green