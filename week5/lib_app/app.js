// 主应用逻辑
import { auth, db } from './firebase-config.js';
import { 
    signInWithPopup, 
    GoogleAuthProvider, 
    signOut, 
    onAuthStateChanged 
} from 'https://www.gstatic.com/firebasejs/9.22.0/firebase-auth.js';
import { 
    collection, 
    addDoc, 
    getDocs, 
    query, 
    orderBy, 
    serverTimestamp 
} from 'https://www.gstatic.com/firebasejs/9.22.0/firebase-firestore.js';

// DOM 元素
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const userInfo = document.getElementById('user-info');
const userName = document.getElementById('user-name');
const addBookSection = document.getElementById('add-book-section');
const bookForm = document.getElementById('book-form');
const booksContainer = document.getElementById('books-container');
const loading = document.getElementById('loading');
const noBooksDiv = document.getElementById('no-books');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toast-message');

// Google 登录提供者
const provider = new GoogleAuthProvider();

// 当前用户
let currentUser = null;

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    // 监听认证状态变化
    onAuthStateChanged(auth, (user) => {
        currentUser = user;
        updateUI(user);
        if (user) {
            console.log('用户已登录:', user.displayName);
        } else {
            console.log('用户未登录');
        }
    });

    // 加载图书列表
    loadBooks();

    // 绑定事件监听器
    bindEventListeners();
});

// 绑定事件监听器
function bindEventListeners() {
    // 登录按钮
    loginBtn.addEventListener('click', signInWithGoogle);

    // 退出按钮
    logoutBtn.addEventListener('click', signOutUser);

    // 图书表单提交
    bookForm.addEventListener('submit', handleBookSubmit);
}

// Google 登录
async function signInWithGoogle() {
    try {
        const result = await signInWithPopup(auth, provider);
        const user = result.user;
        showToast(`欢迎，${user.displayName}！`, 'success');
    } catch (error) {
        console.error('登录失败:', error);
        showToast('登录失败，请重试', 'error');
    }
}

// 用户退出
async function signOutUser() {
    try {
        await signOut(auth);
        showToast('已成功退出', 'success');
    } catch (error) {
        console.error('退出失败:', error);
        showToast('退出失败，请重试', 'error');
    }
}

// 更新UI
function updateUI(user) {
    if (user) {
        // 用户已登录
        loginBtn.classList.add('d-none');
        userInfo.classList.remove('d-none');
        userName.textContent = user.displayName;
        addBookSection.classList.remove('d-none');
    } else {
        // 用户未登录
        loginBtn.classList.remove('d-none');
        userInfo.classList.add('d-none');
        addBookSection.classList.add('d-none');
    }
}

// 处理图书表单提交
async function handleBookSubmit(e) {
    e.preventDefault();

    if (!currentUser) {
        showToast('请先登录', 'error');
        return;
    }

    const title = document.getElementById('book-title').value.trim();
    const author = document.getElementById('book-author').value.trim();
    const description = document.getElementById('book-description').value.trim();

    if (!title || !description) {
        showToast('请填写图书名称和简介', 'error');
        return;
    }

    try {
        // 添加图书到 Firestore
        await addDoc(collection(db, 'books'), {
            title: title,
            author: author || '未知作者',
            description: description,
            userId: currentUser.uid,
            userName: currentUser.displayName,
            userEmail: currentUser.email,
            createdAt: serverTimestamp()
        });

        // 清空表单
        bookForm.reset();
        
        // 重新加载图书列表
        loadBooks();
        
        showToast('图书添加成功！', 'success');
    } catch (error) {
        console.error('添加图书失败:', error);
        showToast('添加图书失败，请重试', 'error');
    }
}

// 加载图书列表
async function loadBooks() {
    try {
        loading.classList.remove('d-none');
        booksContainer.classList.add('d-none');
        noBooksDiv.classList.add('d-none');

        // 查询所有图书，按创建时间降序排列
        const q = query(collection(db, 'books'), orderBy('createdAt', 'desc'));
        const querySnapshot = await getDocs(q);

        if (querySnapshot.empty) {
            // 没有图书
            loading.classList.add('d-none');
            noBooksDiv.classList.remove('d-none');
            return;
        }

        // 清空容器
        booksContainer.innerHTML = '';

        // 渲染图书卡片
        querySnapshot.forEach((doc) => {
            const book = doc.data();
            const bookCard = createBookCard(book);
            booksContainer.appendChild(bookCard);
        });

        loading.classList.add('d-none');
        booksContainer.classList.remove('d-none');

    } catch (error) {
        console.error('加载图书失败:', error);
        loading.classList.add('d-none');
        showToast('加载图书失败，请刷新页面重试', 'error');
    }
}

// 创建图书卡片
function createBookCard(book) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4 book-card fade-in';

    const createdAt = book.createdAt ? 
        new Date(book.createdAt.toDate()).toLocaleDateString('zh-CN') : 
        '未知时间';

    col.innerHTML = `
        <div class="card h-100">
            <div class="card-body">
                <div class="user-badge">
                    <i class="fas fa-user me-1"></i>${book.userName || '匿名用户'}
                </div>
                <h5 class="book-title">${escapeHtml(book.title)}</h5>
                <p class="book-author">
                    <i class="fas fa-pen-nib me-1"></i>${escapeHtml(book.author)}
                </p>
                <p class="book-description">${escapeHtml(book.description)}</p>
                <div class="book-meta">
                    <i class="fas fa-calendar-alt me-1"></i>
                    添加时间：${createdAt}
                </div>
            </div>
        </div>
    `;

    return col;
}

// HTML 转义函数
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// 显示 Toast 通知
function showToast(message, type = 'info') {
    toastMessage.textContent = message;
    
    // 移除之前的样式类
    toast.classList.remove('toast-success', 'toast-error');
    
    // 添加对应的样式类
    if (type === 'success') {
        toast.classList.add('toast-success');
    } else if (type === 'error') {
        toast.classList.add('toast-error');
    }

    // 显示 Toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// 导出函数供其他模块使用
window.app = {
    loadBooks,
    showToast
};
