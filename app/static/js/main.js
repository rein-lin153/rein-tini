// 心语时光 - 主 JavaScript 文件

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有功能
    initTooltips();
    initAlerts();
    initSmoothScroll();
    initImageModals();
    initCountdown();
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

// 导出到全局
window.HeartMoments = {
    formatDate,
    timeAgo,
    animateNumber,
    createImageModal
};

console.log('💖 心语时光已加载完成');

