; Sleash Browser — Inno Setup Installer Script
; Requires: Inno Setup 6  →  https://jrsoftware.org/isdl.php
; After PyInstaller build, open this file in Inno Setup and click Compile.

#define AppName      "Sleash"
#define AppVersion   "1.0.0"
#define AppPublisher "Your Company Name"
#define AppURL       "https://yourwebsite.com"
#define AppExeName   "Sleash.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/support
AppUpdatesURL={#AppURL}

; Install to user folder — no admin/UAC prompt needed
DefaultDirName={localappdata}\{#AppName}
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

; Installer output
OutputDir=dist\installer
OutputBaseFilename=SleashSetup-{#AppVersion}
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#AppExeName}

; Compression (makes installer smaller)
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; Prevent running old version during install
CloseApplications=yes
CloseApplicationsFilter=*.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";    Description: "Create a &desktop shortcut";     GroupDescription: "Additional shortcuts:"; Flags: checked
Name: "startupicon";    Description: "Launch Sleash when Windows starts"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
; All PyInstaller output files
Source: "dist\Sleash\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\{#AppName}";                          Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}";                Filename: "{uninstallexe}"

; Desktop shortcut (optional — user chooses during install)
Name: "{commondesktop}\{#AppName}";                  Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

; Startup (optional)
Name: "{userstartup}\{#AppName}";                    Filename: "{app}\{#AppExeName}"; Tasks: startupicon

[Registry]
; Register as a browser (optional — lets Windows offer Sleash in "Open with")
Root: HKCU; Subkey: "Software\Clients\StartMenuInternet\Sleash"; ValueType: string; ValueName: ""; ValueData: "{#AppName}"
Root: HKCU; Subkey: "Software\Clients\StartMenuInternet\Sleash\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"""

[Run]
; Offer to launch after install
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName} now"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up user data folder on uninstall (optional — comment out to keep bookmarks)
; Type: filesandordirs; Name: "{app}"

[Code]
// Show a welcome message with key info
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Caption :=
    'This will install Sleash ' + '{#AppVersion}' + ' on your computer.' + #13#10 + #13#10 +
    'Sleash is a lightweight, privacy-focused browser.' + #13#10 +
    '  • Built-in ad & tracker blocker' + #13#10 +
    '  • No telemetry or background services' + #13#10 +
    '  • Low memory usage' + #13#10 + #13#10 +
    'Click Next to continue.';
end;
