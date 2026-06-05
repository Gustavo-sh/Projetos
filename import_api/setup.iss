[Setup]
AppName=Importador de Metas
AppVersion=1.0.0
AppPublisher=AeC
DefaultDirName={autopf}\ImportadorMetas
DefaultGroupName=Importador de Metas
OutputDir=output
OutputBaseFilename=Setup_ImportadorMetas
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=icone.ico

[Files]
Source: "dist\app_importacao\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Importador de Metas"; Filename: "{app}\app_importacao.exe"
Name: "{commondesktop}\Importador de Metas"; Filename: "{app}\app_importacao.exe"

[Run]
Filename: "{app}\app_importacao.exe"; Description: "Executar Importador de Metas"; Flags: nowait postinstall skipifsilent