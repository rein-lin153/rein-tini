// 倒计时功能

/**
 * 初始化倒计时
 */
function initCountdown(targetDate, elementId) {
    const countdownElement = document.getElementById(elementId);
    if (!countdownElement) return;
    
    const target = new Date(targetDate).getTime();
    
    function updateCountdown() {
        const now = new Date().getTime();
        const distance = target - now;
        
        if (distance < 0) {
            countdownElement.innerHTML = '<span class="text-success">🎉 今天就是纪念日！</span>';
            return;
        }
        
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        let html = '';
        
        if (days > 0) {
            html += `<div class="countdown-item">
                <div class="countdown-number">${days}</div>
                <div class="countdown-label">天</div>
            </div>`;
        }
        
        html += `
            <div class="countdown-item">
                <div class="countdown-number">${hours}</div>
                <div class="countdown-label">时</div>
            </div>
            <div class="countdown-item">
                <div class="countdown-number">${minutes}</div>
                <div class="countdown-label">分</div>
            </div>
            <div class="countdown-item">
                <div class="countdown-number">${seconds}</div>
                <div class="countdown-label">秒</div>
            </div>
        `;
        
        countdownElement.innerHTML = html;
    }
    
    // 立即执行一次
    updateCountdown();
    
    // 每秒更新一次
    setInterval(updateCountdown, 1000);
}

// 导出到全局
window.initCountdown = initCountdown;

