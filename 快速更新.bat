@echo off
chcp 65001 >nul
echo ========================================
echo           TKTool 快速更新工具
echo ========================================
echo.
echo 选择操作:
echo 1. 配置GitHub仓库
echo 2. 版本更新工具
echo 3. 快速更新版本
echo 4. 检查更新
echo 5. 退出
echo.
set /p choice=请输入选择 (1-5): 

if "%choice%"=="1" (
    echo 正在打开GitHub配置工具...
    python scripts\setup_config.py --interactive
    pause
) else if "%choice%"=="2" (
    echo 正在打开版本更新工具...
    python scripts\update_version.py --interactive
    pause
) else if "%choice%"=="3" (
    echo 正在快速更新版本...
    python scripts\update_version.py --quick
    pause
) else if "%choice%"=="4" (
    echo 正在检查更新...
    python -c "from core.update_checker import UpdateChecker; UpdateChecker().manual_check_update()"
    pause
) else if "%choice%"=="5" (
    echo 再见！
    exit
) else (
    echo 无效选择，请重新运行脚本
    pause
)