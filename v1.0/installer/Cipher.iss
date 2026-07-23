; =============================================================================
; Cipher v1.0 — Windows Installer (Inno Setup 6)
; Professional installer for the Cipher neon arena sports game.
; =============================================================================

#define MyAppName "Cipher"
#define MyAppVersion "1.0"
#define MyAppPublisher "Cipher"
#define MyAppURL ""
#define MyAppExeName "Cipher.exe"
#define MyAppId "Cipher_NeonArena_v1"

[Setup]
; Unique AppId — do not change after release (identifies upgrades/uninstall)
AppId={{A7C3E91F-4B2D-4E8A-9C1F-CIPHER1A0B0C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; User chooses install location
AllowNoIcons=yes
; Output
OutputDir=..\dist
OutputBaseFilename=Cipher_v1.0_Setup
; Icon used for Setup.exe and shortcuts
SetupIconFile=..\cipher.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} v{#MyAppVersion}
; Compression
Compression=lzma2/ultra64
SolidCompression=yes
InternalCompressLevel=ultra64
; UI
WizardStyle=modern
WizardSizePercent=100
DisableWelcomePage=no
ShowLanguageDialog=no
; Privileges — allow per-user or admin install
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Architecture
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Misc
VersionInfoVersion=1.0.0.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
MinVersion=6.1sp1
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
WelcomeLabel1=Welcome to the {#MyAppName} Setup Wizard
WelcomeLabel2=This will install {#MyAppName} v{#MyAppVersion} on your computer.%n%nCipher is a neon arena sports game. Score. Defend. Dominate.%n%nIt is recommended that you close all other applications before continuing.
FinishedLabel=Setup has finished installing {#MyAppName} on your computer. The application may be launched by selecting the installed shortcuts.
FinishedHeadingLabel=Completing the {#MyAppName} Setup Wizard

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce
Name: "startmenu"; Description: "Create a &Start Menu shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce

[Files]
; Main game executable (onefile PyInstaller build)
Source: "..\dist\Cipher.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; Comment: "Cipher v{#MyAppVersion} — Neon Arena Sport"; Tasks: startmenu
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: startmenu
; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; Comment: "Cipher v{#MyAppVersion} — Neon Arena Sport"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent unchecked

[UninstallDelete]
; Remove leftover empty install dir if present
Type: dirifempty; Name: "{app}"
