import os

for path in ['doit.bat', 'liveSDCard/doit.bat']:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    old_copy = ':: Optional: keep a copy of doit.bat on W:\ for easy future refresh\ncopy /y "%~f0" "W:\doit.bat" >nul 2>&1'
    new_copy = ':: If running from source, update W:\doit.bat immediately\nif /i not "%~dp0"=="W:\\" (\n    if exist "%~f0" copy /y "%~f0" "W:\\doit.bat" >nul 2>&1\n)'

    if old_copy in content:
        content = content.replace(old_copy, new_copy, 1)
    elif old_copy.replace('\n', '\r\n') in content:
        content = content.replace(old_copy.replace('\n', '\r\n'), new_copy.replace('\n', '\r\n'), 1)
    else:
        print(f'Warning: old_copy not found in {path}')

    old_pause = 'echo ===============================================================================\necho.\npause'
    new_pause = """echo ===============================================================================
echo.
echo [NOTE] Pressing any key will finish and automatically sync doit.bat on W:\\!
pause

:: If running directly from W:\\, safely self-update doit.bat from the source share before exit
if exist "%SRC_DIR%\\doit.bat" (
    (goto) 2>nul & copy /y "%SRC_DIR%\\doit.bat" "W:\\doit.bat" >nul 2>&1 & exit /b 0
) else if exist "%SRC_DIR%\\..\\doit.bat" (
    (goto) 2>nul & copy /y "%SRC_DIR%\\..\\doit.bat" "W:\\doit.bat" >nul 2>&1 & exit /b 0
)
exit /b 0"""

    if old_pause in content:
        content = content.replace(old_pause, new_pause, 1)
    elif old_pause.replace('\n', '\r\n') in content:
        content = content.replace(old_pause.replace('\n', '\r\n'), new_pause.replace('\n', '\r\n'), 1)
    else:
        print(f'Warning: old_pause not found in {path}')

    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(content)
    print(f'{path} updated successfully!')
