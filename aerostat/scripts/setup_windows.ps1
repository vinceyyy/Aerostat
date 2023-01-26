param([switch]$Elevated)
function Test-Admin
{
    $currentUser = New-Object Security.Principal.WindowsPrincipal $([Security.Principal.WindowsIdentity]::GetCurrent() )
    $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}
if ((Test-Admin) -eq $false)
{
    if ($elevated)
    {
        # tried to elevate, did not work, aborting
    }
    else
    {
        Start-Process powershell.exe -Verb RunAs -ArgumentList ('-noprofile -noexit -file "{0}" -elevated' -f ($myinvocation.MyCommand.Definition))
    }
    exit
}
Write-Output "running with full privileges"


if (test-path "C:\ProgramData\chocolatey\choco.exe")
{
    $testchoco = powershell choco -v
    Write-Output "Chocolatey Version $testchoco is already installed"
}
else
{
    Write-Output "Chocolatey is not installed, installing now"
    Set-ExecutionPolicy Bypass -Scope Process -Force
    Invoke-WebRequest https://chocolatey.org/install.ps1 -UseBasicParsing | Invoke-Expression
}


$ProgramList = @{ "serverless" = "serverless"; "docker-desktop" = "docker" }
try
{
    ForEach ($Program in $ProgramList.GetEnumerator())
    {
        $ProgramInstallName = $Program.Key
        $ProgramInvokeCommand = $Program.Value + " --version"
        try
        {
            Invoke-Expression $ProgramInvokeCommand | Out-Null
            Write-Output "$ProgramInstallName already installed. Skipping..."
        }
        catch
        {
            Write-Output "Installing $ProgramInstallName"
            choco install $ProgramInstallName -y
            Write-Output "$ProgramInstallName installed"
        }
    }
    Write-Output "Serverless Framework and Docker Desktop are installed."
}
catch
{
    Write-Output "Error installing Chocolatey packages"
    Write-Output $_.Exception.Message
    exit
}
