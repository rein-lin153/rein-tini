/**
 * 音乐播放器 - 独立窗口版本
 * 支持持久播放、状态恢复、与主窗口通信
 */

class MusicPlayer {
    constructor() {
        this.audio = document.getElementById('audioElement');
        this.playlist = [];
        this.currentIndex = 0;
        this.isPlaying = false;
        this.isShuffled = false;
        this.repeatMode = 'none'; // 'none', 'one', 'all'
        this.volume = 0.7;
        this.currentTime = 0;
        this.duration = 0;
        this.likedSongs = new Set();
        this.isPlaylistOpen = false;
        
        // 从 localStorage 恢复状态
        this.restoreState();
        
        // 初始化
        this.init();
    }
    
    init() {
        // 设置音频属性
        this.audio.volume = this.volume;
        this.audio.preload = 'metadata';
        
        // 绑定音频事件
        this.audio.addEventListener('loadedmetadata', () => {
            this.duration = this.audio.duration;
            this.updateDurationDisplay();
        });
        
        this.audio.addEventListener('timeupdate', () => {
            this.currentTime = this.audio.currentTime;
            this.updateProgress();
            this.saveStateDebounced();
        });
        
        this.audio.addEventListener('ended', () => {
            this.handleTrackEnd();
        });
        
        this.audio.addEventListener('play', () => {
            this.isPlaying = true;
            this.updatePlayButton();
            this.updateCoverAnimation();
            this.saveState();
        });
        
        this.audio.addEventListener('pause', () => {
            this.isPlaying = false;
            this.updatePlayButton();
            this.updateCoverAnimation();
            this.saveState();
        });
        
        this.audio.addEventListener('error', (e) => {
            console.error('音频加载错误:', e);
            this.showError('无法加载音频文件');
        });
        
        // 绑定 UI 事件
        this.bindEvents();
        
        // 加载播放列表
        this.loadPlaylist();
        
        // 初始化樱花飘落
        this.initSakura();
        
        // 监听来自主窗口的消息
        window.addEventListener('message', (e) => {
            this.handleMessage(e.data);
        });
        
        // 监听 localStorage 变化（用于多窗口同步）
        window.addEventListener('storage', (e) => {
            if (e.key === 'musicPlayerState') {
                this.restoreState();
            }
            if (e.key === 'musicPlaylist') {
                this.loadPlaylist();
            }
        });
        
        // 页面卸载前保存状态
        window.addEventListener('beforeunload', () => {
            this.saveState();
        });
    }
    
    bindEvents() {
        // 播放/暂停
        document.getElementById('playPauseBtn').addEventListener('click', () => {
            this.togglePlay();
        });
        
        // 上一首/下一首
        document.getElementById('prevBtn').addEventListener('click', () => {
            this.prev();
        });
        
        document.getElementById('nextBtn').addEventListener('click', () => {
            this.next();
        });
        
        // 进度条
        const progressBar = document.getElementById('progressBar');
        progressBar.addEventListener('click', (e) => {
            this.seek(e);
        });
        
        // 音量控制
        document.getElementById('volumeBtn').addEventListener('click', () => {
            this.toggleMute();
        });
        
        const volumeSlider = document.getElementById('volumeSlider');
        volumeSlider.addEventListener('click', (e) => {
            this.setVolume(e);
        });
        
        // 随机/循环
        document.getElementById('shuffleBtn').addEventListener('click', () => {
            this.toggleShuffle();
        });
        
        document.getElementById('repeatBtn').addEventListener('click', () => {
            this.toggleRepeat();
        });
        
        // 喜欢
        document.getElementById('likeBtn').addEventListener('click', () => {
            this.toggleLike();
        });
        
        // 播放列表
        document.getElementById('playlistToggleBtn').addEventListener('click', () => {
            this.togglePlaylist();
        });
        
        document.getElementById('playlistCloseBtn').addEventListener('click', () => {
            this.togglePlaylist();
        });
    }
    
    async loadPlaylist() {
        try {
            const response = await fetch('/music/list');
            if (!response.ok) {
                throw new Error('获取播放列表失败');
            }
            
            this.playlist = await response.json();
            
            if (this.playlist.length === 0) {
                this.showError('播放列表为空');
                return;
            }
            
            // 更新播放列表计数
            document.getElementById('playlistCount').textContent = this.playlist.length;
            
            // 恢复播放状态
            this.restorePlayback();
            
            // 渲染播放列表
            this.renderPlaylist();
            
            // 保存播放列表到 localStorage（用于多窗口同步）
            localStorage.setItem('musicPlaylist', JSON.stringify(this.playlist));
            
        } catch (error) {
            console.error('加载播放列表失败:', error);
            this.showError('加载播放列表失败: ' + error.message);
        }
    }
    
    restorePlayback() {
        const savedState = this.getSavedState();
        if (!savedState || this.playlist.length === 0) {
            this.currentIndex = 0;
            this.loadTrack(this.currentIndex);
            return;
        }
        
        // 恢复当前歌曲索引
        const savedIndex = savedState.currentIndex;
        if (savedIndex >= 0 && savedIndex < this.playlist.length) {
            this.currentIndex = savedIndex;
        } else {
            // 尝试通过 ID 或文件名查找
            const savedTrack = savedState.currentTrack;
            if (savedTrack) {
                const foundIndex = this.playlist.findIndex(
                    track => track.id === savedTrack.id || track.filename === savedTrack.filename
                );
                if (foundIndex >= 0) {
                    this.currentIndex = foundIndex;
                }
            }
        }
        
        // 加载歌曲
        this.loadTrack(this.currentIndex, savedState.currentTime);
        
        // 恢复音量
        if (savedState.volume !== undefined) {
            this.volume = savedState.volume;
            this.audio.volume = this.volume;
            this.updateVolumeDisplay();
        }
        
        // 恢复播放状态（需要用户交互才能自动播放）
        if (savedState.isPlaying) {
            // 延迟一下，等待音频加载
            setTimeout(() => {
                this.audio.play().catch(() => {
                    // 自动播放被阻止，需要用户点击
                    console.log('自动播放被阻止，等待用户交互');
                });
            }, 500);
        }
    }
    
    loadTrack(index, seekTime = null) {
        if (index < 0 || index >= this.playlist.length) {
            return;
        }
        
        this.currentIndex = index;
        const track = this.playlist[index];
        
        // 设置音频源
        this.audio.src = track.url;
        this.audio.load();
        
        // 更新 UI
        this.updateTrackInfo(track);
        this.updatePlaylistActive();
        
        // 恢复播放进度
        if (seekTime !== null && seekTime > 0) {
            this.audio.addEventListener('loadedmetadata', () => {
                this.audio.currentTime = Math.min(seekTime, this.audio.duration - 1);
            }, { once: true });
        }
        
        // 保存状态
        this.saveState();
        
        // 通知主窗口
        this.notifyMainWindow('trackChanged', track);
    }
    
    togglePlay() {
        if (this.playlist.length === 0) {
            return;
        }
        
        if (this.isPlaying) {
            this.audio.pause();
        } else {
            this.audio.play().catch(error => {
                console.error('播放失败:', error);
                this.showError('播放失败，请检查音频文件');
            });
        }
    }
    
    prev() {
        if (this.playlist.length === 0) {
            return;
        }
        
        if (this.isShuffled) {
            this.currentIndex = Math.floor(Math.random() * this.playlist.length);
        } else {
            this.currentIndex = (this.currentIndex - 1 + this.playlist.length) % this.playlist.length;
        }
        
        this.loadTrack(this.currentIndex);
        if (this.isPlaying) {
            this.audio.play();
        }
    }
    
    next() {
        if (this.playlist.length === 0) {
            return;
        }
        
        if (this.isShuffled) {
            this.currentIndex = Math.floor(Math.random() * this.playlist.length);
        } else {
            this.currentIndex = (this.currentIndex + 1) % this.playlist.length;
        }
        
        this.loadTrack(this.currentIndex);
        if (this.isPlaying) {
            this.audio.play();
        }
    }
    
    handleTrackEnd() {
        if (this.repeatMode === 'one') {
            this.audio.currentTime = 0;
            this.audio.play();
        } else if (this.repeatMode === 'all' || this.currentIndex < this.playlist.length - 1) {
            this.next();
        } else {
            this.isPlaying = false;
            this.updatePlayButton();
        }
    }
    
    seek(e) {
        if (this.duration === 0) {
            return;
        }
        
        const rect = e.currentTarget.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        const time = percent * this.duration;
        
        this.audio.currentTime = time;
        this.currentTime = time;
        this.updateProgress();
    }
    
    setVolume(e) {
        const rect = e.currentTarget.getBoundingClientRect();
        const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        
        this.volume = percent;
        this.audio.volume = this.volume;
        this.updateVolumeDisplay();
        this.saveState();
    }
    
    toggleMute() {
        if (this.audio.volume > 0) {
            this.audio.volume = 0;
        } else {
            this.audio.volume = this.volume || 0.7;
        }
        this.updateVolumeDisplay();
    }
    
    toggleShuffle() {
        this.isShuffled = !this.isShuffled;
        document.getElementById('shuffleBtn').classList.toggle('active', this.isShuffled);
        this.saveState();
    }
    
    toggleRepeat() {
        const modes = ['none', 'all', 'one'];
        const currentModeIndex = modes.indexOf(this.repeatMode);
        this.repeatMode = modes[(currentModeIndex + 1) % modes.length];
        
        const repeatBtn = document.getElementById('repeatBtn');
        repeatBtn.classList.toggle('active', this.repeatMode !== 'none');
        
        // 更新图标
        const icon = repeatBtn.querySelector('i');
        if (this.repeatMode === 'one') {
            icon.className = 'fas fa-redo';
            repeatBtn.title = '单曲循环';
        } else if (this.repeatMode === 'all') {
            icon.className = 'fas fa-sync';
            repeatBtn.title = '列表循环';
        } else {
            icon.className = 'fas fa-redo';
            repeatBtn.title = '循环播放';
        }
        
        this.saveState();
    }
    
    toggleLike() {
        const currentTrack = this.playlist[this.currentIndex];
        if (!currentTrack) {
            return;
        }
        
        const trackId = currentTrack.id || currentTrack.filename;
        if (this.likedSongs.has(trackId)) {
            this.likedSongs.delete(trackId);
        } else {
            this.likedSongs.add(trackId);
        }
        
        document.getElementById('likeBtn').classList.toggle('liked', this.likedSongs.has(trackId));
        this.saveLikedSongs();
    }
    
    togglePlaylist() {
        this.isPlaylistOpen = !this.isPlaylistOpen;
        document.getElementById('playlist').classList.toggle('show', this.isPlaylistOpen);
    }
    
    updateTrackInfo(track) {
        document.getElementById('playerTitle').textContent = track.title || '未知歌曲';
        document.getElementById('playerArtist').textContent = track.artist || '未知艺术家';
        
        // 更新封面
        const coverImage = document.getElementById('coverImage');
        const coverPlaceholder = document.querySelector('.player-cover-placeholder');
        
        if (track.cover) {
            coverImage.src = track.cover;
            coverImage.style.display = 'block';
            coverPlaceholder.style.display = 'none';
        } else {
            coverImage.style.display = 'none';
            coverPlaceholder.style.display = 'flex';
        }
        
        // 更新喜欢状态
        const trackId = track.id || track.filename;
        document.getElementById('likeBtn').classList.toggle('liked', this.likedSongs.has(trackId));
    }
    
    updatePlayButton() {
        const btn = document.getElementById('playPauseBtn');
        const icon = btn.querySelector('i');
        icon.className = this.isPlaying ? 'fas fa-pause' : 'fas fa-play';
    }
    
    updateCoverAnimation() {
        const cover = document.querySelector('.player-cover');
        if (this.isPlaying) {
            cover.classList.add('playing');
        } else {
            cover.classList.remove('playing');
        }
    }
    
    updateProgress() {
        const percent = this.duration > 0 ? (this.currentTime / this.duration) * 100 : 0;
        document.getElementById('progressFill').style.width = percent + '%';
        document.getElementById('progressHandle').style.left = percent + '%';
        document.getElementById('currentTime').textContent = this.formatTime(this.currentTime);
    }
    
    updateDurationDisplay() {
        document.getElementById('duration').textContent = this.formatTime(this.duration);
    }
    
    updateVolumeDisplay() {
        const percent = this.audio.volume * 100;
        document.getElementById('volumeFill').style.width = percent + '%';
        document.getElementById('volumeHandle').style.left = percent + '%';
        
        const volumeBtn = document.getElementById('volumeBtn');
        const icon = volumeBtn.querySelector('i');
        if (this.audio.volume === 0) {
            icon.className = 'fas fa-volume-mute';
        } else if (this.audio.volume < 0.5) {
            icon.className = 'fas fa-volume-down';
        } else {
            icon.className = 'fas fa-volume-up';
        }
    }
    
    renderPlaylist() {
        const container = document.getElementById('playlistItems');
        container.innerHTML = '';
        
        this.playlist.forEach((track, index) => {
            const item = document.createElement('div');
            item.className = 'playlist-item';
            if (index === this.currentIndex) {
                item.classList.add('active');
            }
            
            const coverHtml = track.cover
                ? `<img src="${track.cover}" alt="封面" class="playlist-item-cover">`
                : `<div class="playlist-item-cover" style="display: flex; align-items: center; justify-content: center; color: #999;"><i class="fas fa-music"></i></div>`;
            
            item.innerHTML = `
                ${coverHtml}
                <div class="playlist-item-info">
                    <div class="playlist-item-title">${track.title || '未知歌曲'}</div>
                    <div class="playlist-item-artist">${track.artist || '未知艺术家'}</div>
                </div>
            `;
            
            item.addEventListener('click', () => {
                this.loadTrack(index);
                if (this.isPlaying) {
                    this.audio.play();
                }
                if (this.isPlaylistOpen) {
                    this.togglePlaylist();
                }
            });
            
            container.appendChild(item);
        });
    }
    
    updatePlaylistActive() {
        const items = document.querySelectorAll('.playlist-item');
        items.forEach((item, index) => {
            item.classList.toggle('active', index === this.currentIndex);
        });
    }
    
    formatTime(seconds) {
        if (isNaN(seconds)) {
            return '0:00';
        }
        
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    showError(message) {
        console.error(message);
        // 可以添加更友好的错误提示 UI
        document.getElementById('playerTitle').textContent = '错误';
        document.getElementById('playerArtist').textContent = message;
    }
    
    // 樱花飘落效果
    initSakura() {
        const container = document.getElementById('sakura-container');
        const petalCount = 20;
        
        for (let i = 0; i < petalCount; i++) {
            setTimeout(() => {
                this.createPetal(container);
            }, i * 500);
        }
        
        // 定期创建新花瓣
        setInterval(() => {
            this.createPetal(container);
        }, 3000);
    }
    
    createPetal(container) {
        const petal = document.createElement('div');
        petal.className = 'sakura-petal';
        
        const size = Math.random() * 8 + 6;
        petal.style.width = size + 'px';
        petal.style.height = size + 'px';
        petal.style.left = Math.random() * 100 + '%';
        petal.style.animationDuration = (Math.random() * 10 + 10) + 's';
        petal.style.animationDelay = Math.random() * 2 + 's';
        
        container.appendChild(petal);
        
        // 动画结束后移除
        setTimeout(() => {
            petal.remove();
        }, 12000);
    }
    
    // 状态管理
    saveState() {
        try {
            const currentTrack = this.playlist[this.currentIndex];
            const state = {
                currentIndex: this.currentIndex,
                currentTrack: currentTrack ? {
                    id: currentTrack.id,
                    filename: currentTrack.filename
                } : null,
                currentTime: this.currentTime,
                isPlaying: this.isPlaying,
                volume: this.volume,
                isShuffled: this.isShuffled,
                repeatMode: this.repeatMode,
                timestamp: Date.now()
            };
            
            localStorage.setItem('musicPlayerState', JSON.stringify(state));
            
            // 通知主窗口
            this.notifyMainWindow('stateChanged', state);
        } catch (error) {
            console.error('保存状态失败:', error);
        }
    }
    
    saveStateDebounced() {
        if (this.saveStateTimer) {
            clearTimeout(this.saveStateTimer);
        }
        this.saveStateTimer = setTimeout(() => {
            this.saveState();
        }, 2000);
    }
    
    getSavedState() {
        try {
            const saved = localStorage.getItem('musicPlayerState');
            if (saved) {
                const state = JSON.parse(saved);
                // 检查状态是否过期（超过24小时则重置）
                if (Date.now() - state.timestamp > 24 * 3600 * 1000) {
                    localStorage.removeItem('musicPlayerState');
                    return null;
                }
                return state;
            }
        } catch (error) {
            console.error('读取保存的状态失败:', error);
        }
        return null;
    }
    
    restoreState() {
        const savedState = this.getSavedState();
        if (savedState) {
            this.volume = savedState.volume !== undefined ? savedState.volume : 0.7;
            this.isShuffled = savedState.isShuffled || false;
            this.repeatMode = savedState.repeatMode || 'none';
            
            // 更新 UI
            document.getElementById('shuffleBtn').classList.toggle('active', this.isShuffled);
            document.getElementById('repeatBtn').classList.toggle('active', this.repeatMode !== 'none');
            this.updateVolumeDisplay();
        }
        
        // 恢复喜欢的歌曲
        this.restoreLikedSongs();
    }
    
    saveLikedSongs() {
        try {
            localStorage.setItem('musicLikedSongs', JSON.stringify(Array.from(this.likedSongs)));
        } catch (error) {
            console.error('保存喜欢的歌曲失败:', error);
        }
    }
    
    restoreLikedSongs() {
        try {
            const saved = localStorage.getItem('musicLikedSongs');
            if (saved) {
                this.likedSongs = new Set(JSON.parse(saved));
            }
        } catch (error) {
            console.error('读取喜欢的歌曲失败:', error);
        }
    }
    
    // 与主窗口通信
    notifyMainWindow(type, data) {
        try {
            if (window.opener && !window.opener.closed && window.opener.postMessage) {
                window.opener.postMessage({
                    type: type,
                    data: data,
                    source: 'musicPlayer',
                    timestamp: Date.now()
                }, '*');
            } else {
                // 回退到 localStorage 事件
                console.debug('window.opener 不可用，使用 localStorage 事件回退');
                try {
                    localStorage.setItem('musicPlayerEvent', JSON.stringify({ type, data, timestamp: Date.now() }));
                    localStorage.removeItem('musicPlayerEvent');
                } catch (e) {
                    console.warn('localStorage 回退也失败:', e);
                }
            }
        } catch (e) {
            console.warn('notifyMainWindow 失败:', e);
            // 静默失败，不影响主流程
        }
    }
    
    handleMessage(message) {
        if (!message || message.source === 'musicPlayer') {
            return;
        }
        
        switch (message.type) {
            case 'refreshPlaylist':
                this.loadPlaylist();
                break;
            case 'playTrack':
                if (message.data && message.data.id) {
                    const index = this.playlist.findIndex(track => track.id === message.data.id);
                    if (index >= 0) {
                        this.loadTrack(index);
                        this.audio.play();
                    }
                }
                break;
            case 'togglePlay':
                this.togglePlay();
                break;
            case 'next':
                this.next();
                break;
            case 'prev':
                this.prev();
                break;
        }
    }
    
    // 刷新播放列表（用于上传新音乐后）
    async refreshPlaylist() {
        await this.loadPlaylist();
        this.renderPlaylist();
    }
}

// 初始化播放器
document.addEventListener('DOMContentLoaded', () => {
    window.musicPlayer = new MusicPlayer();
});

