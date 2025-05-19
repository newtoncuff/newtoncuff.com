# PowerShell script to run docker compose down for the 'newtoncuff' project on a remote Linux server

# ---- Settings ----
$RemoteUser = "root"
$RemoteHost = "192.168.1.129"
$RemoteDir = "/repository/newtoncuff.com"
$ProjectName = "newtoncuff"

# ---- SSH into remote server and run Docker Compose Down ----
$SshCommand = "ssh $RemoteUser@$RemoteHost 'cd $RemoteDir && docker compose -p $ProjectName down'"
Write-Host "Running: $SshCommand"
Invoke-Expression $SshCommand