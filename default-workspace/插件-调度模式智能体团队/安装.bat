@echo off
chcp 65001 >nul
title 安装：调度模式智能体团队（DSH 插件）
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================================
echo   DSH 插件安装器：调度模式智能体团队
echo ============================================================
echo.

echo [1/4] 检查 DSH 桌面端是否已退出...
tasklist /FI "IMAGENAME eq DeepSeek Harness.exe" /NH 2>nul | find /I "DeepSeek Harness.exe" >nul
if not errorlevel 1 (
  echo.
  echo   [错误] DSH 桌面端仍在运行。
  echo   官方要求：操作 desktop profile 前必须**完全退出** DSH。
  echo   请关闭所有 DSH 窗口（含托盘）后重新运行本文件。
  echo.
  pause
  exit /b 2
)
echo   OK - 桌面端未运行
echo.

echo [2/4] 定位 Node.js...
set "NODE="
if exist "D:\deep\resources\runtime\node\node.exe" set "NODE=D:\deep\resources\runtime\node\node.exe"
if not defined NODE if exist "%USERPROFILE%\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe" set "NODE=%USERPROFILE%\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe"
if not defined NODE for %%I in (node.exe) do if not defined NODE set "NODE=%%~$PATH:I"
if not defined NODE (
  echo   [错误] 找不到 node.exe。请安装 Node.js ^>=18 后重试。
  echo.
  pause
  exit /b 2
)
echo   OK - %NODE%
echo.

echo [3/4] 定位 DSH CLI...
set "DSHCLI="
if exist "D:\deep\resources\runtime\cli\bin\dsh.cmd" set "DSHCLI=D:\deep\resources\runtime\cli\bin\dsh.cmd"
if not defined DSHCLI if exist "%LOCALAPPDATA%\Programs\DeepSeek Harness\resources\runtime\cli\bin\dsh.cmd" set "DSHCLI=%LOCALAPPDATA%\Programs\DeepSeek Harness\resources\runtime\cli\bin\dsh.cmd"
if not defined DSHCLI (
  echo   [错误] 找不到桌面端自带的 dsh.cmd。
  echo   请把它的完整路径写到本目录的 dshcli.txt 后重试。
  echo.
  pause
  exit /b 2
)
echo   OK - %DSHCLI%
echo.

echo [4/4] 执行安装（会先备份 profile 的 package.json 与 cordis.patch.yml）...
echo ------------------------------------------------------------
"%NODE%" "%~dp0tools\install.cjs" --cli "%DSHCLI%"
set "RC=%ERRORLEVEL%"
echo ------------------------------------------------------------
echo.

if "%RC%"=="0" (
  echo ============================================================
  echo   安装成功
  echo ============================================================
  echo   下一步：
  echo     1^) 重启 DSH 桌面端
  echo     2^) 插件 - 已安装 - 应出现「调度模式智能体团队」
  echo     3^) 新建会话，推理模式选「调度模式」，输入 /team
  echo ============================================================
) else (
  echo ============================================================
  echo   安装失败（退出码 %RC%）
  echo ============================================================
  echo   常见原因：
  echo     - 桌面端没完全退出（含托盘/后台进程）
  echo     - 依赖 junction 未建好：再跑一次本文件
  echo     - 官方 CLI 路径不对：把路径写进 dshcli.txt
  echo ============================================================
)
echo.
pause