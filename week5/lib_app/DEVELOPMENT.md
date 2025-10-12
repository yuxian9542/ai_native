# 开发工具使用指南

## 🚀 快速开始

### 1. 安装依赖
```bash
cd week5/lib_app
npm install
```

### 2. 启动开发服务器
```bash
npm run dev
```
- 自动打开浏览器访问 http://localhost:3000
- 支持热重载，修改文件后自动刷新
- 实时预览您的更改

## 📋 可用命令

| 命令 | 功能 | 说明 |
|------|------|------|
| `npm run dev` | 开发模式 | 启动带热重载的开发服务器 |
| `npm start` | 生产预览 | 启动静态文件服务器 |
| `npm run demo` | 演示页面 | 直接打开演示说明页面 |
| `npm run preview` | 预览模式 | 在端口 4173 启动预览服务器 |
| `npm run help` | 帮助信息 | 显示使用提示 |

## 🔥 开发工具特性

### 热重载 (Hot Reload)
- **自动刷新**：修改 HTML、CSS、JS 文件后浏览器自动刷新
- **状态保持**：某些情况下保持页面状态（如登录状态）
- **即时反馈**：立即看到代码更改的效果

### 移动设备测试
开发服务器会显示局域网地址，方便在手机上测试：
```
Local:   http://localhost:3000
Network: http://192.168.1.100:3000  ← 用这个地址在手机上访问
```

### 更好的错误提示
- 详细的错误信息显示在浏览器中
- 控制台输出更清晰的日志
- 自动处理 CORS 问题

## 🛠️ 开发工作流

### 典型的开发流程：
1. **启动开发服务器**：`npm run dev`
2. **编辑代码**：修改 HTML、CSS、JS 文件
3. **查看效果**：浏览器自动刷新显示更改
4. **测试功能**：在浏览器中测试新功能
5. **移动端测试**：使用网络地址在手机上测试
6. **部署准备**：使用 `npm start` 进行最终测试

### 推荐的开发环境：
- **编辑器**：VS Code（推荐安装 Live Server 扩展）
- **浏览器**：Chrome（开发者工具功能强大）
- **Node.js**：版本 14 或更高

## 🔧 故障排除

### 常见问题：

**Q: 端口 3000 被占用**
```bash
# 查看占用端口的进程
netstat -ano | findstr :3000
# 或者使用其他端口
npx live-server --port=3001
```

**Q: 热重载不工作**
- 检查文件是否保存
- 确认浏览器没有缓存问题（Ctrl+F5 强制刷新）
- 重启开发服务器

**Q: 无法访问网络地址**
- 检查防火墙设置
- 确认设备在同一局域网内
- 尝试关闭 VPN

**Q: Firebase 功能不正常**
- 检查 firebase-config.js 配置是否正确
- 确认 Firebase 项目设置正确
- 查看浏览器控制台错误信息

## 📱 移动端开发

### 在手机上测试：
1. 确保手机和电脑在同一 WiFi 网络
2. 启动开发服务器：`npm run dev`
3. 记录显示的网络地址（如 http://192.168.1.100:3000）
4. 在手机浏览器中访问该地址

### 响应式测试：
- 使用浏览器开发者工具的设备模拟器
- 测试不同屏幕尺寸的显示效果
- 验证触摸交互功能

## 🚀 部署准备

### 本地预览：
```bash
npm run preview  # 模拟生产环境
```

### 文件检查：
- 确认所有文件都已保存
- 检查控制台没有错误
- 测试所有功能正常工作

### 部署到 Firebase Hosting：
```bash
# 安装 Firebase CLI
npm install -g firebase-tools

# 登录 Firebase
firebase login

# 初始化项目
firebase init hosting

# 部署
firebase deploy
```

## 💡 开发技巧

### 1. 使用浏览器开发者工具
- **Elements**：检查和修改 HTML/CSS
- **Console**：查看 JavaScript 错误和日志
- **Network**：监控网络请求
- **Application**：查看 Firebase 数据和本地存储

### 2. 代码调试
```javascript
// 在代码中添加调试信息
console.log('用户信息:', user);
console.table(books);  // 表格形式显示数组
debugger;  // 设置断点
```

### 3. Firebase 调试
- 在 Firebase Console 中查看实时数据
- 使用 Firebase Emulator 进行本地测试
- 查看 Authentication 和 Firestore 的使用情况

## 📚 学习资源

- [Firebase 官方文档](https://firebase.google.com/docs)
- [Bootstrap 5 文档](https://getbootstrap.com/docs/5.1/)
- [MDN Web 开发指南](https://developer.mozilla.org/zh-CN/)
- [Chrome 开发者工具指南](https://developers.google.com/web/tools/chrome-devtools)

---

**提示**：开发过程中遇到问题，首先查看浏览器控制台的错误信息，这通常能提供解决问题的线索。
