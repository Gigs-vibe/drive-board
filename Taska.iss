[Setup]
AppId={{8A3F2C1D-4E5B-4F6A-9D7E-2B0C8F1A3E5D}
AppName=Taska
AppVersion=1.6.6
AppPublisher=Gigs-vibe
DefaultDirName={localappdata}\Programs\Taska
DefaultGroupName=Taska
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename=TaskaSetup
SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
DisableWelcomePage=yes
DisableDirPage=yes
DisableProgramGroupPage=yes
CloseApplications=yes
RestartApplications=yes
UninstallDisplayIcon={app}\Taska.exe

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Дополнительно:"; Flags: unchecked

[Files]
; onedir-сборка: вся папка (Taska.exe + _internal со всеми DLL) — нет распаковки в temp при запуске
Source: "dist\Taska\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Taska"; Filename: "{app}\Taska.exe"
Name: "{autodesktop}\Taska"; Filename: "{app}\Taska.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Taska.exe"; Description: "Запустить Taska"; Flags: nowait postinstall skipifsilent
Filename: "{app}\Taska.exe"; Flags: nowait; Check: WizardSilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
