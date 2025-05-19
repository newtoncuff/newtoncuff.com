# PowerShell script to prune all Docker resources on a remote Linux server

# ---- Settings ----
$RemoteUser = "root"
$RemoteHost = "192.168.1.129"

# ---- SSH into remote server and run Docker system prune -a ----
$SshCommand = "ssh $RemoteUser@$RemoteHost 'docker system prune -a -f'"
Write-Host "Running: $SshCommand"
Invoke-Expression $SshCommand