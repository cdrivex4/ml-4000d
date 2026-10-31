import os

os.makedirs('liveSDCard/ML/LOGS', exist_ok=True)
print('liveSDCard/ML/LOGS exists:', os.path.exists('liveSDCard/ML/LOGS'))

for doit in ['doit.bat', 'liveSDCard/doit.bat']:
    with open(doit, 'r', encoding='utf-8') as f:
        content = f.read()
    old_robo = 'robocopy "%SRC_DIR%\\ML" "W:\\ML" /E /PURGE /R:1 /W:1 /NP /NFL /NDL >nul'
    new_robo = 'robocopy "%SRC_DIR%\\ML" "W:\\ML" /E /PURGE /XD LOGS SETTINGS /R:1 /W:1 /NP /NFL /NDL >nul'
    if old_robo in content:
        content = content.replace(old_robo, new_robo, 1)
        with open(doit, 'w', encoding='utf-8', newline='\r\n') as f:
            f.write(content)
        print(f'{doit} updated!')
    else:
        print(f'{doit} already updated or string not found')
