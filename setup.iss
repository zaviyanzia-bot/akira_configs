[Setup]
AppId={{A35B6D18-F58D-43D5-B52B-FFE9C629A12D}
AppName=AKIRA
AppVersion=1.0.7
AppPublisher=Malik Zia
DefaultDirName={autopf}\Akira
DefaultGroupName=AKIRA
OutputDir=build_output
OutputBaseFilename=Akira_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
DisableProgramGroupPage=yes
DisableDirPage=no
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\logo.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "build_output\Akira\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "license_config.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Akira"; Filename: "{app}\Akira.exe"
Name: "{autodesktop}\Akira"; Filename: "{app}\Akira.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Akira.exe"; Flags: nowait postinstall

[UninstallRun]
Filename: "cmd.exe"; Parameters: "/c if exist ""{app}\device_id.txt"" (for /f ""tokens=*"" %i in ('type ""{app}\device_id.txt""') do curl -s -d ""device_id=%i&event=uninstall"" ""https://script.google.com/macros/s/AKfycbwnVLyth13MpEXA0Clh79Vr7VyuIJZMAb9R_fmn5SX1Biwxakr_4g5AmUQ5Jyxny9v-tA/exec"")"; Flags: runhidden
