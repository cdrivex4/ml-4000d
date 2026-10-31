p = 'doit.bat'
s = open(p, 'r', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in s else '\n'
s = s.replace('\r\n', '\n')

old = '''copy /y "%SRC%\\autoexec.bin" "W:\\autoexec.bin" >nul
if errorlevel 1 goto :pushfail
fc /b "%SRC%\\autoexec.bin" "W:\\autoexec.bin" >nul
if errorlevel 1 goto :pushfail
for %%F in (W:\\autoexec.bin) do echo       autoexec.bin verified: %%~zF bytes
'''
new = '''for %%F in ("%SRC%\\autoexec.bin") do echo       source autoexec.bin : %%~tF  %%~zF bytes
:: atomic-ish: copy to temp name, verify, then rename over the live file
del /f /q "W:\\autoexec.tmp" 2>nul
copy /y "%SRC%\\autoexec.bin" "W:\\autoexec.tmp" >nul
if errorlevel 1 goto :pushfail
fc /b "%SRC%\\autoexec.bin" "W:\\autoexec.tmp" >nul
if errorlevel 1 goto :pushfail
move /y "W:\\autoexec.tmp" "W:\\autoexec.bin" >nul
if errorlevel 1 goto :pushfail
set "H1="
set "H2="
for /f "skip=1 tokens=1" %%H in ('certutil -hashfile "%SRC%\\autoexec.bin" SHA256') do if not defined H1 set "H1=%%H"
for /f "skip=1 tokens=1" %%H in ('certutil -hashfile "W:\\autoexec.bin" SHA256') do if not defined H2 set "H2=%%H"
echo       SHA256 source : !H1!
echo       SHA256 on card: !H2!
if not "!H1!"=="!H2!" goto :pushfail
echo       autoexec.bin VERIFIED identical
'''
assert old in s
s = s.replace(old, new)

old2 = 'if exist "%SRC%\\TESTS.CFG" copy /y "%SRC%\\TESTS.CFG" "W:\\TESTS.CFG" >nul\n'
new2 = '''if exist "%SRC%\\TESTS.CFG" copy /y "%SRC%\\TESTS.CFG" "W:\\TESTS.CFG" >nul
if exist "%SRC%\\TESTS.CFG" fc /b "%SRC%\\TESTS.CFG" "W:\\TESTS.CFG" >nul
if errorlevel 1 goto :pushfail
'''
assert old2 in s
s = s.replace(old2, new2)

old3 = 'if exist "%ROOT%\\doit.bat" copy /y "%ROOT%\\doit.bat" "W:\\doit.bat" >nul\n'
new3 = '''if exist "%ROOT%\\doit.bat" copy /y "%ROOT%\\doit.bat" "W:\\doit.bat" >nul
if exist "%ROOT%\\doit.bat" fc /b "%ROOT%\\doit.bat" "W:\\doit.bat" >nul
if errorlevel 1 echo       [WARN] W:\\doit.bat did not verify
'''
assert old3 in s
s = s.replace(old3, new3)

# verify ML folder: robocopy list-only must report nothing left to copy
old4 = 'echo       ML folder synced\n'
new4 = '''robocopy "%SRC%\\ML" "W:\\ML" /E /XO /XD LOGS SETTINGS /L /NJH /NJS /NP /NDL /NC /NS >"%TEMP%\\ml_diff.txt"
findstr /r /c:"." "%TEMP%\\ml_diff.txt" >nul
if errorlevel 1 (echo       ML folder synced and verified) else echo       [WARN] ML folder differs after sync - see %TEMP%\\ml_diff.txt
'''
assert old4 in s
s = s.replace(old4, new4)
open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', nl))
print('ok')
