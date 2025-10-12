// Firebase 配置文件
import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.22.0/firebase-app.js';
import { getAuth } from 'https://www.gstatic.com/firebasejs/9.22.0/firebase-auth.js';
import { getFirestore } from 'https://www.gstatic.com/firebasejs/9.22.0/firebase-firestore.js';

// Firebase 配置
// 请替换为您的 Firebase 项目配置
const firebaseConfig = {
    apiKey: "AIzaSyCTFtsivkwSWBdU57C4yHJpge1BS7qfgOI",
    authDomain: "lib-management-28d6a.firebaseapp.com",
    projectId: "lib-management-28d6a",
    storageBucket: "lib-management-28d6a.firebasestorage.app",
    messagingSenderId: "665904311811",
    appId: "1:665904311811:web:0f17f9668ba4fa5eb5e836",
    measurementId: "G-VQXBS22BS9"
};

// 初始化 Firebase
const app = initializeApp(firebaseConfig);

// 初始化 Firebase Auth
export const auth = getAuth(app);

// 初始化 Firestore
export const db = getFirestore(app);

// 导出 app 实例
export default app;
