; Build with: ISCC.exe packaging\installer.iss  (Inno Setup 6, pre-installed on
; GitHub's windows-latest runners). Produces one installer .exe with a Start
; Menu + Desktop shortcut and a normal Windows uninstaller entry.

#define AppName "FCG MIS Pulse"
; Overridden per release by the workflow (ISCC /DAppVersion=1.2.3, taken
; from the pushed tag); this default is only used for untagged test builds.
#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputBaseFilename=FCG-MIS-Pulse-Setup
OutputDir={#SourcePath}\..\installer_output
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "{#SourcePath}\..\dist\{#AppName}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppName}.exe"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppName}.exe"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\{#AppName}.exe"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
