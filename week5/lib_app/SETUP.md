# Firebase 配置快速指南

## 步骤 1: 创建 Firebase 项目

1. 访问 [Firebase Console](https://console.firebase.google.com/)
2. 点击"添加项目"
3. 输入项目名称（例如：library-management）
4. 选择是否启用 Google Analytics（可选）
5. 创建项目

## 步骤 2: 启用身份验证

1. 在 Firebase Console 中选择您的项目
2. 点击左侧菜单的"Authentication"
3. 点击"开始使用"
4. 切换到"Sign-in method"标签
5. 启用"Google"登录提供商
6. 输入项目的公开名称和支持邮箱
7. 保存

## 步骤 3: 创建 Firestore 数据库

1. 点击左侧菜单的"Firestore Database"
2. 点击"创建数据库"
3. 选择"以测试模式启动"（稍后会设置安全规则）
4. 选择数据库位置（建议选择亚洲地区）
5. 完成创建

## 步骤 4: 设置安全规则

1. 在 Firestore Database 页面，点击"规则"标签
2. 替换默认规则为以下内容：

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /books/{bookId} {
      allow read: if true;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && request.auth.uid == resource.data.userId;
    }
  }
}
```

3. 点击"发布"

## 步骤 5: 获取配置信息

1. 点击左侧菜单的"项目设置"（齿轮图标）
2. 滚动到"您的应用"部分
3. 点击"</>"图标添加 Web 应用
4. 输入应用昵称（例如：library-web）
5. 不需要设置 Firebase Hosting
6. 复制配置对象

## 步骤 6: 更新配置文件

将复制的配置信息替换到 `firebase-config.js` 文件中：

```javascript
const firebaseConfig = {
    apiKey: "AIzaSy...",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project",
    storageBucket: "your-project.appspot.com", 
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abcdef"
};
```

## 步骤 7: 测试应用

1. 在本地启动 Web 服务器：
   ```bash
   python -m http.server 8000
   ```

2. 访问 `http://localhost:8000`

3. 测试登录功能

4. 测试添加图书功能

## 常见问题

**Q: 登录时出现"unauthorized_client"错误**
A: 需要在 Firebase Console > Authentication > Settings > Authorized domains 中添加您的域名

**Q: 无法读取或写入数据**  
A: 检查 Firestore 安全规则是否正确设置

**Q: 本地测试时登录失败**
A: 确保使用 `http://localhost` 而不是 `file://` 协议

## 生产环境部署

### 使用 Firebase Hosting

1. 安装 Firebase CLI：
   ```bash
   npm install -g firebase-tools
   ```

2. 登录并初始化：
   ```bash
   firebase login
   firebase init hosting
   ```

3. 部署：
   ```bash
   firebase deploy
   ```

### 使用其他托管服务

确保在 Firebase Console > Authentication > Settings > Authorized domains 中添加您的生产域名。
