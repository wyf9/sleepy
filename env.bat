@echo off

set pip_cmd=".venv\Scripts\pip.exe" --require-virtualenv
goto start

:usage
echo Usage:
echo - env.bat create         ^| Create a virtualenv (use first)
echo - env.bat activate       ^| Activate an existing virtualenv
echo - env.bat install        ^| Install requirements without version lock
echo - env.bat install-locked ^| Install version-locked requirements
echo - env.bat freeze         ^| Save version-locked requirements file
goto eof

:start

if "%1" == "" (
    goto usage
) else if "%1" == "create" (
    if exist ".venv\Scripts\python.exe" (
        echo A virtualenv already exists, use 'env.bat activate' to activate it
        echo or delete the .venv folder to recreate
        exit /b 1
    ) else (
        python -m venv .venv --prompt sleepy
        goto eof
    )
) else if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found!
    echo Use 'env.bat create' to create a new one
    exit /b 1
) else if "%1" == "activate" (
    .venv\Scripts\activate
    goto eof
) else if "%1" == "deactivate" (
    .venv\Scripts\deactivate
    goto eof
) else if "%1" == "install-locked" (
    %pip_cmd% install -U -r requirements-lock.txt
    goto eof
) else if "%1" == "install" (
    %pip_cmd% install -U -r requirements.txt
    goto eof
) else if "%1" == "freeze" (
    echo # Generated on %date% %time% (Windows) > requirements-lock.txt
    echo. >> requirements-lock.txt
    %pip_cmd% freeze >> requirements-lock.txt
    goto eof
)

goto usage

:eof
exit /b 0