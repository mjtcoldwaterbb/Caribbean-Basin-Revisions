@echo off
setlocal
cd /d "%~dp0"

echo [1/3] Building site from Obsidian source...
python build_site.py
if errorlevel 1 goto :fail

echo [2/3] Staging changes...
git add -A
git diff --cached --quiet
if %errorlevel%==0 (
    echo No changes detected after build. Nothing to publish.
    goto :done
)

if "%~1"=="" (
    set "MSG=Update living essay"
) else (
    set "MSG=%*"
)

echo [3/3] Committing and pushing...
git commit -m "%MSG%"
if errorlevel 1 goto :fail

git push origin main
if errorlevel 1 goto :fail

echo Publish complete.
goto :done

:fail
echo Publish failed. Review output above for details.
endlocal
exit /b 1

:done
endlocal
exit /b 0
