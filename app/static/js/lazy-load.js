// 图片懒加载

(function() {
    'use strict';
    
    // 检查浏览器是否支持 IntersectionObserver
    if ('IntersectionObserver' in window) {
        // 创建观察器
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // 加载图片
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    
                    // 添加淡入效果
                    img.classList.add('fade-in');
                    
                    // 停止观察
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px',  // 提前 50px 开始加载
            threshold: 0.01
        });
        
        // 观察所有带 lazy-load 类的图片
        document.querySelectorAll('img.lazy-load').forEach(function(img) {
            imageObserver.observe(img);
        });
        
        // 观察所有带 loading="lazy" 属性的图片
        document.querySelectorAll('img[loading="lazy"]').forEach(function(img) {
            imageObserver.observe(img);
        });
    } else {
        // 不支持 IntersectionObserver，直接加载所有图片
        document.querySelectorAll('img[data-src]').forEach(function(img) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
})();

