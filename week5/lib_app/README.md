# 图书管理系统

一个基于 Firebase 的图书管理网站，支持用户登录、图书添加和浏览功能。

## 功能特性

- 🔐 **Firebase Google 登录**：安全的用户认证系统
- 📚 **图书管理**：登录用户可以添加图书信息
- 👀 **公开浏览**：所有用户（包括未登录用户）都可以浏览图书列表
- 💾 **Firestore 数据库**：实时数据存储和同步
- 📱 **响应式设计**：适配各种设备屏幕
- 🎨 **现代化UI**：使用 Bootstrap 5 和 Font Awesome

## 技术栈

- **前端**：HTML5, CSS3, JavaScript (ES6+)
- **UI框架**：Bootstrap 5
- **图标**：Font Awesome 6
- **后端服务**：Firebase
- **数据库**：Firestore
- **认证**：Firebase Auth (Google Provider)

## 快速开始

### 1. 创建 Firebase 项目

1. 访问 [Firebase Console](https://console.firebase.google.com/)
2. 创建新项目或选择现有项目
3. 启用 **Authentication** 服务
4. 在 Authentication > Sign-in method 中启用 **Google** 登录
5. 启用 **Firestore Database** 服务
6. 在 Firestore 中设置安全规则（见下文）

### 2. 配置 Firebase

1. 在 Firebase Console 中获取项目配置信息
2. 打开 `firebase-config.js` 文件
3. 替换配置对象中的占位符：

```javascript
const firebaseConfig = {
    apiKey: "your-api-key-here",
    authDomain: "your-project-id.firebaseapp.com", 
    projectId: "your-project-id",
    storageBucket: "your-project-id.appspot.com",
    messagingSenderId: "your-sender-id",
    appId: "your-app-id"
};
```

### 3. 设置 Firestore 安全规则

在 Firebase Console > Firestore Database > Rules 中设置以下规则：

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 图书集合规则
    match /books/{bookId} {
      // 所有人都可以读取图书信息
      allow read: if true;
      // 只有登录用户可以创建图书
      allow create: if request.auth != null 
        && request.auth.uid == resource.data.userId;
      // 只有图书的创建者可以更新和删除
      allow update, delete: if request.auth != null 
        && request.auth.uid == resource.data.userId;
    }
  }
}
```

### 4. 部署应用

#### 方法一：本地服务器
```bash
# 使用 Python 启动本地服务器
python -m http.server 8000

# 或使用 Node.js
npx serve .

# 然后访问 http://localhost:8000
```

#### 方法二：Firebase Hosting
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

## 数据结构

### Books 集合

每个图书文档包含以下字段：

```javascript
{
  title: "图书名称",           // string, 必填
  author: "作者姓名",          // string, 可选
  description: "图书简介",     // string, 必填
  userId: "用户ID",           // string, 自动填充
  userName: "用户显示名称",    // string, 自动填充
  userEmail: "用户邮箱",      // string, 自动填充
  createdAt: timestamp        // timestamp, 自动填充
}
```

## 使用说明

### 对于访客用户
- 可以浏览所有已添加的图书信息
- 查看图书名称、作者、简介和添加时间
- 查看图书添加者的用户名

### 对于登录用户
- 使用 Google 账号登录
- 添加新的图书信息（名称和简介为必填项）
- 浏览所有图书信息
- 只能管理自己添加的图书

## 文件结构

```
lib_app/
├── index.html          # 主页面
├── styles.css          # 样式文件
├── firebase-config.js  # Firebase 配置
├── app.js             # 主应用逻辑
└── README.md          # 说明文档
```

## 自定义和扩展

### 添加新字段
1. 在 `index.html` 中添加表单字段
2. 在 `app.js` 的 `handleBookSubmit` 函数中处理新字段
3. 在 `createBookCard` 函数中显示新字段

### 修改样式
- 编辑 `styles.css` 文件
- 使用 Bootstrap 类名进行快速样式调整
- 添加自定义 CSS 类

### 添加功能
- 图书编辑和删除
- 图书分类和标签
- 搜索和筛选
- 用户个人图书管理页面
- 图书评分和评论

## 故障排除

### 常见问题

1. **登录失败**
   - 检查 Firebase 配置是否正确
   - 确认 Google 登录已在 Firebase Console 中启用
   - 检查域名是否已添加到授权域名列表

2. **无法添加图书**
   - 确认用户已登录
   - 检查 Firestore 安全规则
   - 查看浏览器控制台错误信息

3. **图书列表不显示**
   - 检查 Firestore 数据库是否已启用
   - 确认安全规则允许读取操作
   - 检查网络连接

### 调试模式
在浏览器控制台中可以查看详细的错误信息和日志。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
