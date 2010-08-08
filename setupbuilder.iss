[Files]
Source: dist\icon.ico; DestDir: {userappdata}\Snarl Tray Notifications
Source: dist\Snarl Tray Notifications.exe; DestDir: {userappdata}\Snarl Tray Notifications
Source: dist\LICENSE; DestDir: {userappdata}\Snarl Tray Notifications
Source: dist\Licenses\PySnarl\License.txt; DestDir: {userappdata}\Snarl Tray Notifications\Licenses\PySnarl
[Icons]
Name: {userstartup}\Snarl Tray Notifications; Filename: {userappdata}\Snarl Tray Notifications\Snarl Tray Notifications.exe; WorkingDir: {userappdata}\Snarl Tray Notifications; Flags: useapppaths
[Run]
Filename: {userappdata}\Snarl Tray Notifications\Snarl Tray Notifications.exe; Flags: postinstall nowait
[Setup]
AppCopyright=© 2010 Moises Aranas
AppName=Snarl Tray Notifications
AppVerName=Snarl Tray Notifications 0.5
CreateAppDir=false
DisableProgramGroupPage=true
UsePreviousGroup=false
DefaultGroupName=Snarl Tray Notifications
AppendDefaultGroupName=false
AlwaysUsePersonalGroup=true
AppVersion=0.5
AppPublisher=Moises Aranas
