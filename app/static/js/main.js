// 心语时光 - 主 JavaScript 文件

// 全局错误处理（捕获未处理的 Promise 拒绝和错误）
window.addEventListener('error', function(event) {
    // 忽略来自浏览器扩展的错误（如 content.js）
    if (event.filename && (
        event.filename.includes('chrome-extension://') || 
        event.filename.includes('moz-extension://') ||
        event.filename.includes('safari-extension://')
    )) {
        console.debug('忽略浏览器扩展错误:', event.filename);
        return;
    }
    
    // 记录其他错误
    console.error('全局错误:', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
    });
}, true);

// 捕获未处理的 Promise 拒绝
window.addEventListener('unhandledrejection', function(event) {
    // 忽略来自浏览器扩展的 Promise 拒绝
    const error = event.reason;
    if (error && typeof error === 'object') {
        const errorString = JSON.stringify(error);
        if (errorString.includes('chrome-extension://') || 
            errorString.includes('moz-extension://') ||
            errorString.includes('content.js')) {
            console.debug('忽略浏览器扩展 Promise 拒绝');
            event.preventDefault(); // 阻止默认错误处理
            return;
        }
    }
    
    // 记录其他 Promise 拒绝
    console.error('未处理的 Promise 拒绝:', {
        reason: event.reason,
        promise: event.promise
    });
    
    // 对于已知的 message port 错误，静默处理
    if (event.reason && typeof event.reason === 'string' && 
        event.reason.includes('message port closed')) {
        console.debug('Message port 已关闭（可能是浏览器扩展），静默处理');
        event.preventDefault();
        return;
    }
});

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有功能
    initTooltips();
    initAlerts();
    initSmoothScroll();
    initImageModals();
    initCountdown();
    initAjaxNavigation();
});

/**
 * 初始化 Bootstrap Tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * 自动关闭 Alert 消息
 */
function initAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);  // 5秒后自动关闭
    });
}

/**
 * 平滑滚动
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '#!') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

/**
 * 图片点击放大（Modal）
 */
function initImageModals() {
    const images = document.querySelectorAll('.post-content img, .photo-card img');
    
    images.forEach(function(img) {
        img.style.cursor = 'pointer';
        img.addEventListener('click', function() {
            createImageModal(this.src, this.alt);
        });
    });
}

function createImageModal(src, alt) {
    // 创建 Modal HTML
    const modalHTML = `
        <div class="modal fade" id="imageModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered modal-xl">
                <div class="modal-content bg-transparent border-0">
                    <div class="modal-body p-0 text-center">
                        <img src="${src}" alt="${alt}" class="img-fluid rounded">
                        <button type="button" class="btn btn-light btn-sm mt-3" data-bs-dismiss="modal">
                            <i class="fas fa-times"></i> 关闭
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除旧的 Modal（如果存在）
    const oldModal = document.getElementById('imageModal');
    if (oldModal) {
        oldModal.remove();
    }
    
    // 添加到页面并显示
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('imageModal'));
    modal.show();
    
    // Modal 关闭后移除
    document.getElementById('imageModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

/**
 * 倒计时动画（首页）
 */
function initCountdown() {
    const countdownElement = document.querySelector('.countdown-days');
    if (countdownElement) {
        animateNumber(countdownElement, 0, parseInt(countdownElement.textContent), 2000);
    }
}

/**
 * 数字动画
 */
function animateNumber(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);  // 60fps
    let current = start;
    
    const timer = setInterval(function() {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

/**
 * 表单验证增强
 */
document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
        if (!form.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        form.classList.add('was-validated');
    });
});

/**
 * 图片上传预览
 */
const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
imageInputs.forEach(function(input) {
    input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(event) {
                let preview = document.getElementById('imagePreview');
                if (!preview) {
                    preview = document.createElement('img');
                    preview.id = 'imagePreview';
                    preview.className = 'img-fluid rounded mt-3';
                    preview.style.maxHeight = '400px';
                    input.parentNode.appendChild(preview);
                }
                preview.src = event.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
});

/**
 * 返回顶部按钮
 */
const backToTopBtn = document.getElementById('backToTopBtn');

if (backToTopBtn) {
    // 监听滚动事件，显示/隐藏按钮
    window.addEventListener('scroll', function() {
        const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        
        if (scrollTop > 300) {
            backToTopBtn.style.display = 'block';
            backToTopBtn.style.opacity = '1';
        } else {
            backToTopBtn.style.opacity = '0';
            setTimeout(() => {
                if (scrollTop <= 300) {
                    backToTopBtn.style.display = 'none';
                }
            }, 300);
        }
    });
    
    // 点击按钮返回顶部
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// 内嵌播放器已通过 player-embedded.js 处理
// 不再需要独立窗口逻辑

/**
 * 确认删除
 */
document.querySelectorAll('[data-confirm]').forEach(function(element) {
    element.addEventListener('click', function(e) {
        const message = this.getAttribute('data-confirm') || '确定要执行此操作吗？';
        if (!confirm(message)) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    });
});

/**
 * Markdown 编辑器辅助
 */
const markdownTextareas = document.querySelectorAll('textarea[name="body"]');
markdownTextareas.forEach(function(textarea) {
    // 添加快捷键支持
    textarea.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + B - 粗体
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
            e.preventDefault();
            wrapText(textarea, '**', '**');
        }
        // Ctrl/Cmd + I - 斜体
        if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
            e.preventDefault();
            wrapText(textarea, '*', '*');
        }
        // Tab - 插入缩进
        if (e.key === 'Tab') {
            e.preventDefault();
            insertText(textarea, '    ');
        }
    });
});

function wrapText(textarea, before, after) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    const replacement = before + selectedText + after;
    
    textarea.setRangeText(replacement, start, end, 'select');
    textarea.focus();
}

function insertText(textarea, text) {
    const start = textarea.selectionStart;
    textarea.setRangeText(text, start, start, 'end');
    textarea.focus();
}

/**
 * 工具函数：格式化日期
 */
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * 工具函数：时间差
 */
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return '刚刚';
    if (seconds < 3600) return Math.floor(seconds / 60) + ' 分钟前';
    if (seconds < 86400) return Math.floor(seconds / 3600) + ' 小时前';
    if (seconds < 604800) return Math.floor(seconds / 86400) + ' 天前';
    
    return formatDate(date);
}

/**
 * 初始化AJAX导航（保持音乐播放器不中断）
 */
function initAjaxNavigation() {
    // 设置初始历史状态
    if (window.history && window.history.pushState) {
        window.history.replaceState({ path: window.location.pathname }, '', window.location.pathname);
    }
    
    // 只拦截内部链接，不拦截外部链接、下载链接、邮件链接等
    document.addEventListener('click', function(e) {
        const link = e.target.closest('a');
        if (!link) return;
        
        const href = link.getAttribute('href');
        if (!href) return;
        
        // 跳过的情况：
        // 1. 外部链接
        // 2. 锚点链接（#开头）
        // 3. JavaScript链接
        // 4. 邮件链接
        // 5. 下载链接
        // 6. 新窗口打开的链接
        // 7. 表单提交链接
        // 8. 上传/编辑页面（这些页面需要完整刷新以保持表单状态）
        if (href.startsWith('http://') || 
            href.startsWith('https://') || 
            href.startsWith('//') ||
            href.startsWith('#') ||
            href.startsWith('javascript:') ||
            href.startsWith('mailto:') ||
            href.startsWith('tel:') ||
            link.hasAttribute('download') ||
            link.target === '_blank' ||
            link.closest('form') ||
            href.includes('/auth/') ||
            href.includes('/music/admin/upload') ||  // 音乐上传页面需要完整刷新
            href.includes('/album/upload') ||
            href.includes('/album/batch_upload') ||
            href.includes('/posts/new') ||
            href.includes('/posts/edit') ||
            e.ctrlKey || e.metaKey || e.shiftKey) {
            return;
        }
        
        // 拦截内部导航链接
        e.preventDefault();
        
        // 使用AJAX加载页面内容
        loadPage(href);
        
        // 更新浏览器历史记录
        if (window.history && window.history.pushState) {
            window.history.pushState({ path: href }, '', href);
        }
    });
    
    // 处理浏览器前进/后退
    window.addEventListener('popstate', function(e) {
        if (e.state && e.state.path) {
            loadPage(e.state.path);
        } else {
            window.location.reload();
        }
    });
}

/**
 * 使用AJAX加载页面内容
 */
function loadPage(url) {
    // 显示加载指示器
    const mainContent = document.querySelector('main.container');
    if (mainContent) {
        mainContent.style.opacity = '0.5';
        mainContent.style.transition = 'opacity 0.3s';
    }
    
    // 获取页面内容
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        // 解析HTML
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // 更新页面标题
        if (doc.title) {
            document.title = doc.title;
        }
        
        // 更新主内容区域（保持播放器不被刷新）
        const newMainContent = doc.querySelector('main.container');
        const currentMainContent = document.querySelector('main.container#mainContent');
        if (newMainContent && currentMainContent) {
            currentMainContent.innerHTML = newMainContent.innerHTML;
            currentMainContent.style.opacity = '1';
        }
        
        // 更新Flash消息
        const newFlashMessages = doc.querySelector('.container.mt-3');
        const currentFlashMessages = document.querySelector('.container.mt-3');
        if (newFlashMessages && currentFlashMessages) {
            currentFlashMessages.innerHTML = newFlashMessages.innerHTML;
        }
        
        // 重新初始化页面功能
        initTooltips();
        initAlerts();
        initSmoothScroll();
        initImageModals();
        initCountdown();
        
        // 检查是否需要加载额外的脚本
        const extraScripts = doc.querySelectorAll('script[src]');
        extraScripts.forEach(script => {
            const src = script.getAttribute('src');
            // 如果脚本还未加载，动态加载
            if (src && !document.querySelector(`script[src="${src}"]`)) {
                const newScript = document.createElement('script');
                newScript.src = src;
                newScript.async = true;
                document.body.appendChild(newScript);
            }
        });
        
        // 触发自定义事件，让其他脚本知道页面已更新
        // 先触发 pageLoaded（向后兼容）
        window.dispatchEvent(new CustomEvent('pageLoaded', { 
            detail: { url, timestamp: Date.now() },
            bubbles: true,
            cancelable: true
        }));
        
        // 再触发 content:loaded（统一的事件名称）
        // 延迟一点确保 DOM 完全更新
        setTimeout(() => {
            window.dispatchEvent(new CustomEvent('content:loaded', { 
                detail: { 
                    url: url || window.location.href,
                    timestamp: Date.now(),
                    target: currentMainContent
                },
                bubbles: true,
                cancelable: true
            }));
        }, 50);
        
        // 滚动到顶部（但不影响播放器）
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        // 注意：播放器不会被刷新，因为它不在 mainContent 内
        // 播放器状态会保持不变，继续播放
    })
    .catch(error => {
        console.error('加载页面失败:', error);
        // 如果AJAX加载失败，回退到传统页面跳转
        window.location.href = url;
    });
}

// 导出到全局
window.HeartMoments = {
    formatDate,
    timeAgo,
    animateNumber,
    createImageModal,
    loadPage
};

console.log('💖 心语时光已加载完成');

