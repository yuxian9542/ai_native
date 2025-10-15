# Firebase 详细设置文档

## 📋 目录
1. [Firebase 项目创建](#1-firebase-项目创建)
2. [启用 Authentication](#2-启用-authentication)
3. [配置 Google 登录](#3-配置-google-登录)
4. [启用 Firestore 数据库](#4-启用-firestore-数据库)
5. [设置安全规则](#5-设置安全规则)
6. [测试配置](#6-测试配置)
7. [常见问题解决](#7-常见问题解决)

---

## 1. Firebase 项目创建

### 步骤 1.1: 创建新项目
1. 访问 [Firebase Console](https://console.firebase.google.com/)
2. 点击 "创建项目" 或 "Add project"
3. 输入项目名称：`lib-mgmt-dynm`
4. 点击 "继续"
5. 选择是否启用 Google Analytics（可选）
6. 点击 "创建项目"

### 步骤 1.2: 添加 Web 应用
1. 在项目概览页面，点击 Web 图标 `</>`
2. 输入应用昵称：`图书管理系统`
3. 勾选 "为此应用设置 Firebase Hosting"
4. 点击 "注册应用"
5. 复制配置信息（已保存在 `.env` 文件中）

---

## 2. 启用 Authentication

### 步骤 2.1: 进入 Authentication
1. 在左侧菜单中点击 "Authentication"
2. 点击 "开始使用"

### 步骤 2.2: 配置登录方法
1. 点击 "Sign-in method" 标签
2. 您会看到各种登录提供商的列表

---

## 3. 配置 Google 登录

### 步骤 3.1: 启用 Google 登录
1. 在 "Sign-in method" 页面，找到 "Google"
2. 点击 "Google" 行
3. 切换 "启用" 开关为开启状态
4. 输入项目支持邮箱（您的邮箱）
5. 点击 "保存"

### 步骤 3.2: 配置 OAuth 同意屏幕（重要！）
1. 点击 "Web SDK 配置" 部分
2. 复制 "Web SDK 配置" 中的配置信息
3. 如果遇到 OAuth 同意屏幕错误，需要配置：

#### 配置 OAuth 同意屏幕：
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 选择您的 Firebase 项目
3. 在左侧菜单中找到 "APIs & Services" → "OAuth consent screen"
4. 选择 "External" 用户类型
5. 填写必要信息：
   - 应用名称：`图书管理系统`
   - 用户支持邮箱：您的邮箱
   - 开发者联系信息：您的邮箱
6. 点击 "保存并继续"
7. 在 "Scopes" 页面，点击 "添加或移除范围"
8. 添加以下范围：
   - `../auth/userinfo.email`
   - `../auth/userinfo.profile`
   - `openid`
9. 点击 "更新" → "保存并继续"
10. 在 "Test users" 页面，添加测试用户邮箱（可选）
11. 点击 "保存并继续" → "返回到信息中心"

### 步骤 3.3: 配置授权重定向 URI
1. 在 Google Cloud Console 中，转到 "APIs & Services" → "Credentials"
2. 找到您的 OAuth 2.0 客户端 ID
3. 点击编辑（铅笔图标）
4. 在 "已获授权的重定向 URI" 中添加：
   - `http://localhost:3000` (开发环境)
   - `https://your-domain.com` (生产环境)
5. 点击 "保存"

---

## 4. 启用 Firestore 数据库

### 步骤 4.1: 创建 Firestore 数据库
1. 在 Firebase Console 左侧菜单中点击 "Firestore Database"
2. 点击 "创建数据库"
3. 选择 "以测试模式开始"（稍后可以修改安全规则）
4. 选择数据库位置（建议选择离您最近的区域）
5. 点击 "完成"

### 步骤 4.2: 创建集合结构
数据库会自动创建，无需手动创建集合。应用会在需要时自动创建 `books` 集合。

---

## 5. 设置安全规则

### 步骤 5.1: 配置 Firestore 安全规则
1. 在 Firestore Database 页面，点击 "规则" 标签
2. 将以下规则粘贴到编辑器中：

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 图书集合规则
    match /books/{document} {
      // 所有人都可以读取图书
      allow read: if true;
      
      // 只有登录用户可以创建图书
      allow create: if request.auth != null;
      
      // 只有图书作者可以更新和删除
      allow update, delete: if request.auth != null 
        && request.auth.uid == resource.data.userId;
    }
  }
}
```

3. 点击 "发布"

### 步骤 5.2: 配置 Authentication 设置
1. 在 Authentication 页面，点击 "设置" 标签
2. 在 "授权域" 部分，确保包含：
   - `localhost` (开发环境)
   - 您的生产域名
3. 在 "用户操作" 部分，可以配置：
   - 密码重置模板
   - 邮箱验证模板

---

## 6. 测试配置

### 步骤 6.1: 启动应用
```bash
cd week5/lib_app
npm run dev
```

### 步骤 6.2: 测试 Google 登录
1. 打开 `http://localhost:3000`
2. 点击 "注册" 或 "登录"
3. 应该能看到 Google 登录选项
4. 点击 Google 登录按钮
5. 完成 Google 授权流程

### 步骤 6.3: 测试功能
1. 登录后尝试添加图书
2. 检查 Firestore 数据库中是否创建了 `books` 集合
3. 测试搜索功能
4. 测试编辑和删除功能

---

## 7. 常见问题解决

### 问题 1: Google 登录显示 "此应用未验证"
**解决方案：**
1. 在 Google Cloud Console 中配置 OAuth 同意屏幕
2. 添加测试用户到 OAuth 同意屏幕
3. 或者发布应用进行验证（需要 Google 审核）

### 问题 2: "redirect_uri_mismatch" 错误
**解决方案：**
1. 检查 Google Cloud Console 中的重定向 URI 配置
2. 确保包含 `http://localhost:3000`
3. 确保没有多余的斜杠或协议错误

### 问题 3: Firebase 配置错误
**解决方案：**
1. 检查 `.env` 文件中的配置是否正确
2. 确保所有环境变量都以 `VITE_` 开头
3. 重启开发服务器

### 问题 4: Firestore 权限错误
**解决方案：**
1. 检查 Firestore 安全规则
2. 确保用户已正确认证
3. 检查用户 ID 是否匹配

### 问题 5: CORS 错误
**解决方案：**
1. 确保在 Firebase Console 中添加了正确的授权域
2. 检查本地开发服务器是否在正确的端口运行

---

## 🔧 开发环境配置检查清单

- [ ] Firebase 项目已创建
- [ ] Web 应用已注册
- [ ] `.env` 文件配置正确
- [ ] Authentication 已启用
- [ ] Google 登录已配置
- [ ] OAuth 同意屏幕已设置
- [ ] 重定向 URI 已配置
- [ ] Firestore 数据库已创建
- [ ] 安全规则已设置
- [ ] 应用可以正常启动
- [ ] Google 登录功能正常
- [ ] 图书 CRUD 功能正常

---

## 📞 获取帮助

如果遇到问题，可以：
1. 查看 [Firebase 官方文档](https://firebase.google.com/docs)
2. 查看 [Google Cloud Console 文档](https://cloud.google.com/docs)
3. 检查浏览器控制台的错误信息
4. 查看 Firebase Console 中的日志

---

## 🚀 部署到生产环境

当准备部署到生产环境时：
1. 在 Firebase Console 中添加生产域名到授权域
2. 在 Google Cloud Console 中添加生产域名到重定向 URI
3. 更新 `.env` 文件中的配置（如果需要）
4. 使用 `npm run build` 构建生产版本
5. 部署到 Firebase Hosting 或其他托管服务
