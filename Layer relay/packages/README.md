# Layer Relay 下载与运行

- **Layer-relay-Windows-x64.zip**：Windows 64 位运行包。下载后完整解压，双击 `Layer relay.exe`，不需要安装 Godot。
- **Layer-relay-source.zip**：Godot 工程源码包。解压后用 Godot 4.7.2 打开 `project.godot`，按 F5 运行。
- **SHA256SUMS.txt**：两份压缩包的 SHA-256 校验值。

当前包含完整 50 关，设置页显示“正在开发中……”。方向键或 WASD 移动，X/空格升降，Z 撤销，R 重开，H 提示，Enter 暂停。

进度保存在 Godot 的 `user://layer_relay.cfg`，与项目文件、下载目录分开。旧前 31 关记录会兼容迁移。

源码也直接保存在本文件夹的上级目录。重新打包：在上级目录运行 `python tools/package_release.py`；需要 Godot 4.7.2 和对应 Windows 导出模板，可用 `--godot` 指定 Godot 程序。

本次交付已检查 ZIP 完整性与 SHA-256，并将 Windows 包解压到独立目录，直接启动其中的 EXE，正常退出且无脚本错误。设置页已做实际画面检查，迁移后的前端流程回归通过。
