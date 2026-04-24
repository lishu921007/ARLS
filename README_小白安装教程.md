# 行政复议答复事项管理系统（本地一键安装版 v4）

这是 **v4 最终兜底版**。

这次安装脚本已经把常见问题尽量都自动处理了：
1. npm 镜像源失效
2. npm 自身在 Windows 上崩溃
3. Windows 批处理卡住
4. 前端 `node_modules` 残缺 / `package-lock.json` 脏状态 / vite 缺失

## 你只需要做这些

1. 安装 Python 3.11+（勾选 Add Python to PATH）
2. 安装 Node.js LTS
3. 完整解压压缩包
4. 双击 `一键安装.bat`
5. 安装完成后双击 `启动系统.bat`

默认地址：
- http://127.0.0.1:18080

默认账号：
- admin / admin123

## v4 多了什么

如果前端安装失败，脚本会自动按这个思路兜底：
- 正常 `npm install`
- 清缓存后重试
- 使用 `npx -y npm@10 install` 兜底
- 再不行就自动执行“强制重装前端”：
  - 删除 `node_modules`
  - 删除 `package-lock.json`
  - 重新 `npm install`

这样就把你之前手动成功的那套逻辑也吸收进去了。

## 如果还失败

不要自己调试，直接把这个文件发给我：
- `logs/install.log`
