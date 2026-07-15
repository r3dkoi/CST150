Confirmed MySQL Server was installed (via MySQL Installer, version 8.0.46) but mysql wasn't recognised in PowerShell — meaning the server existed, but its bin folder wasn't on PATH.
Verified the binary's location: C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe
Added that folder to my user PATH environment variable ([Environment]::SetEnvironmentVariable("Path", ...)).
Restarted the terminal — PATH changes only apply to new terminal sessions, not ones already open.
Ran mysql -u root -p — it now resolves and prompts for the root password.