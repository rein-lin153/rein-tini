/**
 * 内嵌播放器 - 嵌入在页面底部的播放器
 * 支持 AJAX 导航，页面切换时播放不中断
 */

class EmbeddedMusicPlayer {
    constructor() {
        this.audio = document.createElement('audio');
        this.audio.preload = 'metadata';
        document.body.appendChild(this.audio);
        
        this.playlist = [];
        this.currentIndex = 0;
        this.isPlaying = false;
        this.isShuffled = false;
        this.repeatMode = 'none';
        this.volume = 0.7;
        this.currentTime = 0;
        this.duration = 0;
        this.isPlaylistOpen = false;
        
        // 从 localStorage 恢复状态
        this.restoreState();
        
        // 初始化
        this.init();
    }
    
    init() {
        // 设置音频属性
        this.audio.volume = this.volume;
        
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
        });
        
        // 绑定 UI 事件
        this.bindEvents();
        
        // 加载播放列表
        this.loadPlaylist();
    }
    
    bindEvents() {
        // 播放/暂停
        const playPauseBtn = document.getElementById('embeddedPlayPauseBtn');
        if (playPauseBtn) {
            playPauseBtn.addEventListener('click', () => this.togglePlay());
        }
        
        // 上一首/下一首
        const prevBtn = document.getElementById('embeddedPrevBtn');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.prev());
        }
        
        const nextBtn = document.getElementById('embeddedNextBtn');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.next());
        }
        
        // 进度条
        const progressBar = document.getElementById('embeddedProgressBar');
        if (progressBar) {
            progressBar.addEventListener('click', (e) => this.seek(e));
        }
        
        // 音量控制
        const volumeBtn = document.getElementById('embeddedVolumeBtn');
        if (volumeBtn) {
            volumeBtn.addEventListener('click', () => this.toggleMute());
        }
        
        // 随机/循环
        const shuffleBtn = document.getElementById('embeddedShuffleBtn');
        if (shuffleBtn) {
            shuffleBtn.addEventListener('click', () => this.toggleShuffle());
        }
        
        const repeatBtn = document.getElementById('embeddedRepeatBtn');
        if (repeatBtn) {
            repeatBtn.addEventListener('click', () => this.toggleRepeat());
        }
        
        // 播放列表
        const playlistBtn = document.getElementById('embeddedPlaylistBtn');
        if (playlistBtn) {
            playlistBtn.addEventListener('click', () => this.togglePlaylist());
        }
        
        // 点击播放器区域外关闭播放列表
        document.addEventListener('click', (e) => {
            const player = document.querySelector('.music-player-embedded');
            const playlist = document.querySelector('.player-embedded-playlist');
            if (player && playlist && this.isPlaylistOpen) {
                if (!player.contains(e.target) && !playlist.contains(e.target)) {
                    this.togglePlaylist();
                }
            }
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
                this.hidePlayer();
                return;
            }
            
            // 显示播放器
            this.showPlayer();
            
            // 更新播放列表计数
            const playlistCount = document.getElementById('embeddedPlaylistCount');
            if (playlistCount) {
                playlistCount.textContent = this.playlist.length;
            }
            
            // 恢复播放状态
            this.restorePlayback();
            
            // 渲染播放列表
            this.renderPlaylist();
            
        } catch (error) {
            console.error('加载播放列表失败:', error);
            this.hidePlayer();
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
        }
        
        // 恢复播放模式
        if (savedState.isShuffled !== undefined) {
            this.isShuffled = savedState.isShuffled;
            this.updateShuffleButton();
        }
        if (savedState.repeatMode) {
            this.repeatMode = savedState.repeatMode;
            this.updateRepeatButton();
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
        this.updateShuffleButton();
        this.saveState();
    }
    
    toggleRepeat() {
        const modes = ['none', 'all', 'one'];
        const currentModeIndex = modes.indexOf(this.repeatMode);
        this.repeatMode = modes[(currentModeIndex + 1) % modes.length];
        this.updateRepeatButton();
        this.saveState();
    }
    
    togglePlaylist() {
        this.isPlaylistOpen = !this.isPlaylistOpen;
        const playlist = document.querySelector('.player-embedded-playlist');
        if (playlist) {
            playlist.classList.toggle('show', this.isPlaylistOpen);
        }
    }
    
    updateTrackInfo(track) {
        const titleEl = document.getElementById('embeddedTitle');
        const artistEl = document.getElementById('embeddedArtist');
        const coverImg = document.getElementById('embeddedCoverImg');
        const coverPlaceholder = document.getElementById('embeddedCoverPlaceholder');
        const cover = document.querySelector('.player-embedded-cover');
        
        if (titleEl) {
            titleEl.textContent = track.title || '未知歌曲';
        }
        
        if (artistEl) {
            artistEl.textContent = track.artist || '未知艺术家';
        }
        
        // 更新封面
        if (coverImg && coverPlaceholder && cover) {
            if (track.cover) {
                coverImg.src = track.cover;
                coverImg.style.display = 'block';
                coverPlaceholder.style.display = 'none';
            } else {
                coverImg.style.display = 'none';
                coverPlaceholder.style.display = 'flex';
            }
        }
    }
    
    updatePlayButton() {
        const btn = document.getElementById('embeddedPlayPauseBtn');
        if (btn) {
            const icon = btn.querySelector('i');
            if (icon) {
                icon.className = this.isPlaying ? 'fas fa-pause' : 'fas fa-play';
            }
        }
    }
    
    updateCoverAnimation() {
        const cover = document.querySelector('.player-embedded-cover');
        if (cover) {
            if (this.isPlaying) {
                cover.classList.add('playing');
            } else {
                cover.classList.remove('playing');
            }
        }
    }
    
    updateProgress() {
        const percent = this.duration > 0 ? (this.currentTime / this.duration) * 100 : 0;
        const progressFill = document.getElementById('embeddedProgressFill');
        if (progressFill) {
            progressFill.style.width = percent + '%';
        }
        
        const currentTimeEl = document.getElementById('embeddedCurrentTime');
        if (currentTimeEl) {
            currentTimeEl.textContent = this.formatTime(this.currentTime);
        }
    }
    
    updateDurationDisplay() {
        const durationEl = document.getElementById('embeddedDuration');
        if (durationEl) {
            durationEl.textContent = this.formatTime(this.duration);
        }
    }
    
    updateVolumeDisplay() {
        const volumeBtn = document.getElementById('embeddedVolumeBtn');
        if (volumeBtn) {
            const icon = volumeBtn.querySelector('i');
            if (icon) {
                if (this.audio.volume === 0) {
                    icon.className = 'fas fa-volume-mute';
                } else if (this.audio.volume < 0.5) {
                    icon.className = 'fas fa-volume-down';
                } else {
                    icon.className = 'fas fa-volume-up';
                }
            }
        }
    }
    
    updateShuffleButton() {
        const btn = document.getElementById('embeddedShuffleBtn');
        if (btn) {
            btn.classList.toggle('active', this.isShuffled);
        }
    }
    
    updateRepeatButton() {
        const btn = document.getElementById('embeddedRepeatBtn');
        if (btn) {
            btn.classList.toggle('active', this.repeatMode !== 'none');
            const icon = btn.querySelector('i');
            if (icon) {
                if (this.repeatMode === 'one') {
                    icon.className = 'fas fa-redo';
                    btn.title = '单曲循环';
                } else if (this.repeatMode === 'all') {
                    icon.className = 'fas fa-sync';
                    btn.title = '列表循环';
                } else {
                    icon.className = 'fas fa-redo';
                    btn.title = '循环播放';
                }
            }
        }
    }
    
    renderPlaylist() {
        const container = document.getElementById('embeddedPlaylistItems');
        if (!container) {
            return;
        }
        
        container.innerHTML = '';
        
        this.playlist.forEach((track, index) => {
            const item = document.createElement('div');
            item.className = 'playlist-item-embedded';
            if (index === this.currentIndex) {
                item.classList.add('active');
            }
            
            const coverHtml = track.cover
                ? `<img src="${track.cover}" alt="封面" class="playlist-item-embedded-cover">`
                : `<div class="playlist-item-embedded-cover" style="display: flex; align-items: center; justify-content: center; color: #999;"><i class="fas fa-music"></i></div>`;
            
            item.innerHTML = `
                ${coverHtml}
                <div class="playlist-item-embedded-info">
                    <div class="playlist-item-embedded-title">${track.title || '未知歌曲'}</div>
                    <div class="playlist-item-embedded-artist">${track.artist || '未知艺术家'}</div>
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
        const items = document.querySelectorAll('.playlist-item-embedded');
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
    
    showPlayer() {
        const player = document.querySelector('.music-player-embedded');
        if (player) {
            player.classList.remove('hidden');
        }
    }
    
    hidePlayer() {
        const player = document.querySelector('.music-player-embedded');
        if (player) {
            player.classList.add('hidden');
        }
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
            
            localStorage.setItem('embeddedMusicPlayerState', JSON.stringify(state));
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
            const saved = localStorage.getItem('embeddedMusicPlayerState');
            if (saved) {
                const state = JSON.parse(saved);
                if (Date.now() - state.timestamp > 24 * 3600 * 1000) {
                    localStorage.removeItem('embeddedMusicPlayerState');
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
        }
    }
    
    // 刷新播放列表（用于上传新音乐后）
    async refreshPlaylist() {
        await this.loadPlaylist();
        this.renderPlaylist();
    }
}

// 初始化播放器（仅在页面加载时初始化一次）
function initEmbeddedPlayer() {
    // 如果播放器已存在，不重复初始化
    if (window.embeddedMusicPlayer) {
        return;
    }
    
    // 只在有播放器元素时才初始化
    if (document.querySelector('.music-player-embedded')) {
        window.embeddedMusicPlayer = new EmbeddedMusicPlayer();
        
        // 监听播放列表刷新事件（只绑定一次）
        if (!window.embeddedPlayerListenersBound) {
            window.addEventListener('storage', (e) => {
                if (e.key === 'musicPlaylistRefresh' && window.embeddedMusicPlayer) {
                    window.embeddedMusicPlayer.refreshPlaylist();
                }
            });
            
            // 监听来自上传页面的消息
            window.addEventListener('message', (e) => {
                if (e.data && e.data.type === 'refreshPlaylist') {
                    if (window.embeddedMusicPlayer) {
                        window.embeddedMusicPlayer.refreshPlaylist();
                    }
                }
            });
            
            window.embeddedPlayerListenersBound = true;
        }
    }
}

// 页面加载时初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEmbeddedPlayer);
} else {
    // DOM 已经加载完成，直接初始化
    initEmbeddedPlayer();
}

// 导出初始化函数，供 AJAX 导航后调用（如果需要）
window.initEmbeddedPlayer = initEmbeddedPlayer;

