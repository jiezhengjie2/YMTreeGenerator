
; 义脉树枝图生成器安装脚本
; 使用Inno Setup编译此脚本

[Setup]
AppName=义脉树枝图生成器
AppVersion=1.0
DefaultDirName={autopf}\YMTreeGenerator
DefaultGroupName=义脉树枝图生成器
OutputDir=installer
OutputBaseFilename=YMTreeGenerator_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\义脉树枝图生成器.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "*.py"; DestDir: "{app}\source"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "*.db"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\义脉树枝图生成器"; Filename: "{app}\义脉树枝图生成器.exe"
Name: "{group}\{cm:UninstallProgram,义脉树枝图生成器}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\义脉树枝图生成器"; Filename: "{app}\义脉树枝图生成器.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\义脉树枝图生成器.exe"; Description: "{cm:LaunchProgram,义脉树枝图生成器}"; Flags: nowait postinstall skipifsilent
