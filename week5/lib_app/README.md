# 图书管理系统 - Book Management System

一个使用 Vite + React + Firebase 构建的现代化图书管理网站。

## 功能特性

- 🔐 Firebase 身份验证（登录/注册）
- 📚 图书管理（添加、编辑、删除）
- 👥 用户权限控制
- 🌐 公开图书浏览（未登录用户可查看）
- 🔍 图书搜索功能
- 📱 响应式设计
- ⚡ 实时数据同步

## 技术栈

- **前端框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **后端服务**: Firebase
- **数据库**: Firestore
- **身份验证**: Firebase Auth
- **图标**: Lucide React

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置 Firebase

1. 在 [Firebase Console](https://console.firebase.google.com/) 创建新项目
2. 启用 Authentication 和 Firestore Database
3. 复制项目配置信息
4. 复制 `env.example` 为 `.env` 并填入您的 Firebase 配置：

```env
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=your-app-id
```

### 3. 配置 Firestore 安全规则

在 Firebase Console 的 Firestore 部分，设置以下安全规则：

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /books/{document} {
      allow read: if true; // 所有人都可以读取
      allow write: if request.auth != null && request.auth.uid == resource.data.userId; // 只有作者可以写入
      allow create: if request.auth != null; // 登录用户可以创建
    }
  }
}
```

### 4. 启动开发服务器

```bash
npm run dev
```

访问 [http://localhost:3000](http://localhost:3000) 查看应用。

## 项目结构

```
src/
├── components/          # React 组件
│   ├── Auth.tsx        # 登录/注册组件
│   ├── BookCard.tsx    # 图书卡片组件
│   ├── BookForm.tsx    # 图书表单组件
│   └── Navbar.tsx      # 导航栏组件
├── contexts/           # React Context
│   └── AuthContext.tsx # 身份验证上下文
├── hooks/              # 自定义 Hooks
│   └── useBooks.ts     # 图书管理 Hook
├── pages/              # 页面组件
│   └── HomePage.tsx    # 主页
├── types/              # TypeScript 类型定义
│   └── Book.ts         # 图书类型
├── firebase.ts         # Firebase 配置
├── App.tsx             # 主应用组件
├── main.tsx            # 应用入口
└── index.css           # 全局样式
```

## 使用说明

### 未登录用户
- 可以浏览所有用户添加的图书
- 可以搜索图书
- 无法添加、编辑或删除图书

### 已登录用户
- 可以添加新图书
- 可以编辑和删除自己的图书
- 可以浏览所有用户的图书
- 可以搜索图书

## 部署

### 构建生产版本

```bash
npm run build
```

### 部署到 Firebase Hosting

1. 安装 Firebase CLI：
```bash
npm install -g firebase-tools
```

2. 登录 Firebase：
```bash
firebase login
```

3. 初始化项目：
```bash
firebase init hosting
```

4. 部署：
```bash
firebase deploy
```

## 开发

### 代码检查

```bash
npm run lint
```

### 预览构建

```bash
npm run preview
```

## 许可证

MIT License
