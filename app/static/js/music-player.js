/**
 * 音乐播放器功能
 */

class MusicPlayer {
    constructor() {
        this.audio = null;
        this.currentTrackIndex = 0;
        this.playlist = [];
        this.isPlaying = false;
        this.currentTime = 0;
        this.duration = 0;
        this.volume = 0.7;
        this.isPlaylistOpen = false;
        this.saveStateTimer = null;
        this.isRestoring = false;
        
        // 从localStorage恢复状态
        this.restoreState();
        
        this.init();
    }
    
    init() {
        // 创建音频元素
        this.audio = new Audio();
        this.audio.volume = this.volume;
        
        // 绑定事件
        this.audio.addEventListener('loadedmetadata', () => {
            this.duration = this.audio.duration;
            this.updateDurationDisplay();
        });
        
        this.audio.addEventListener('timeupdate', () => {
            this.currentTime = this.audio.currentTime;
            this.updateProgress();
            // 每5秒保存一次播放进度
            this.saveStateDebounced();
        });
        
        this.audio.addEventListener('ended', () => {
            this.next();
        });
        
        this.audio.addEventListener('play', () => {
            this.isPlaying = true;
            this.updatePlayButton();
            this.updateWaves();
            this.saveState();
        });
        
        this.audio.addEventListener('pause', () => {
            this.isPlaying = false;
            this.updatePlayButton();
            this.updateWaves();
            this.saveState();
        });
        
        // 绑定控制按钮
        this.bindControls();
        
        // 加载播放列表
        this.loadPlaylist();
    }
    
    bindControls() {
        // 播放/暂停按钮
        const playPauseBtn = document.getElementById('musicPlayPause');
        if (playPauseBtn) {
            playPauseBtn.addEventListener('click', () => this.togglePlay());
        }
        
        // 上一首
        const prevBtn = document.getElementById('musicPrev');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.prev());
        }
        
        // 下一首
        const nextBtn = document.getElementById('musicNext');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.next());
        }
        
        // 进度条
        const progress = document.getElementById('musicProgress');
        if (progress) {
            progress.addEventListener('click', (e) => this.seek(e));
        }
        
        // 音量控制
        const volumeBtn = document.getElementById('musicVolumeBtn');
        if (volumeBtn) {
            volumeBtn.addEventListener('click', () => this.toggleMute());
        }
        
        const volumeSlider = document.getElementById('musicVolumeSlider');
        if (volumeSlider) {
            volumeSlider.addEventListener('click', (e) => this.setVolume(e));
        }
        
        // 播放列表按钮
        const playlistBtn = document.getElementById('musicPlaylistBtn');
        if (playlistBtn) {
            playlistBtn.addEventListener('click', () => this.togglePlaylist());
        }
    }
    
    async loadPlaylist() {
        try {
            const response = await fetch('/api/music/list');
            const data = await response.json();
            console.log('音乐列表API响应:', data);
            if (data.success && data.music_list) {
                this.playlist = data.music_list;
                console.log('加载到 ' + this.playlist.length + ' 首歌曲');
                if (this.playlist.length > 0) {
                    // 尝试恢复之前的状态
                    const savedState = this.getSavedState();
                    if (savedState && savedState.currentTrackIndex !== undefined) {
                        const savedIndex = savedState.currentTrackIndex;
                        if (savedIndex >= 0 && savedIndex < this.playlist.length) {
                            this.isRestoring = true;
                            this.currentTrackIndex = savedIndex;
                            this.volume = savedState.volume !== undefined ? savedState.volume : this.volume;
                            this.audio.volume = this.volume;
                            this.updateVolumeDisplay();
                            
                            // 加载歌曲并恢复播放进度
                            this.loadTrackWithRestore(this.currentTrackIndex, savedState);
                        } else {
                            this.currentTrackIndex = 0;
                            this.loadTrack(this.currentTrackIndex);
                        }
                    } else {
                        this.currentTrackIndex = 0;
                        this.loadTrack(this.currentTrackIndex);
                    }
                    
                    this.renderPlaylist();
                    // 更新UI显示
                    this.updateTrackInfo(this.playlist[this.currentTrackIndex]);
                } else {
                    console.warn('播放列表为空，请检查音乐文件是否在 app/static/music/ 目录');
                    this.updateTrackInfo({ title: '暂无音乐', artist: '请将音乐文件放入 app/static/music/ 目录' });
                }
            } else {
                console.error('API返回失败:', data);
                this.updateTrackInfo({ title: '加载失败', artist: '请检查API配置' });
            }
        } catch (error) {
            console.error('加载播放列表失败:', error);
            this.updateTrackInfo({ title: '加载失败', artist: '网络错误: ' + error.message });
        }
    }
    
    loadTrack(index) {
        if (index < 0 || index >= this.playlist.length) return;
        
        this.currentTrackIndex = index;
        const track = this.playlist[index];
        
        if (this.audio) {
            this.audio.src = track.url;
            this.audio.load();
            
            // 更新UI
            this.updateTrackInfo(track);
            this.updatePlaylistActive();
            
            // 如果不是在恢复状态，保存状态
            if (!this.isRestoring) {
                this.saveState();
            }
        }
    }
    
    // 加载歌曲并恢复播放状态
    loadTrackWithRestore(index, savedState) {
        if (index < 0 || index >= this.playlist.length) return;
        
        this.currentTrackIndex = index;
        const track = this.playlist[index];
        
        if (this.audio) {
            // 创建一个一次性的事件监听器来恢复播放进度
            const restoreHandler = () => {
                if (savedState && savedState.currentTime) {
                    const restoreTime = Math.min(savedState.currentTime, this.audio.duration - 1);
                    this.audio.currentTime = restoreTime;
                    this.currentTime = restoreTime;
                    this.updateProgress();
                }
                
                // 如果之前正在播放，尝试继续播放（可能需要用户交互）
                if (savedState && savedState.isPlaying) {
                    setTimeout(() => {
                        this.audio.play().catch(() => {
                            // 自动播放被阻止，这是正常的
                            this.isPlaying = false;
                            this.updatePlayButton();
                        });
                    }, 100);
                }
                this.isRestoring = false;
            };
            
            // 监听canplay事件，确保音频可以播放
            this.audio.addEventListener('canplay', restoreHandler, { once: true });
            
            this.audio.src = track.url;
            this.audio.load();
            
            // 更新UI
            this.updateTrackInfo(track);
            this.updatePlaylistActive();
        }
    }
    
    togglePlay() {
        if (!this.audio || !this.playlist.length) return;
        
        if (this.isPlaying) {
            this.audio.pause();
        } else {
            this.audio.play().catch(error => {
                console.error('播放失败:', error);
            });
        }
    }
    
    prev() {
        if (this.playlist.length === 0) return;
        
        this.currentTrackIndex = (this.currentTrackIndex - 1 + this.playlist.length) % this.playlist.length;
        this.loadTrack(this.currentTrackIndex);
        if (this.isPlaying) {
            this.audio.play();
        }
    }
    
    next() {
        if (this.playlist.length === 0) return;
        
        this.currentTrackIndex = (this.currentTrackIndex + 1) % this.playlist.length;
        this.loadTrack(this.currentTrackIndex);
        if (this.isPlaying) {
            this.audio.play();
        }
    }
    
    seek(e) {
        if (!this.audio || !this.duration) return;
        
        const progress = document.getElementById('musicProgress');
        const rect = progress.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        const time = percent * this.duration;
        
        this.audio.currentTime = time;
    }
    
    setVolume(e) {
        const volumeSlider = document.getElementById('musicVolumeSlider');
        const rect = volumeSlider.getBoundingClientRect();
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
    
    togglePlaylist() {
        this.isPlaylistOpen = !this.isPlaylistOpen;
        const playlist = document.getElementById('musicPlaylist');
        if (playlist) {
            playlist.classList.toggle('show', this.isPlaylistOpen);
            
            // 如果是iframe环境，调整iframe高度以显示播放列表
            if (window.self !== window.top) {
                const iframe = window.frameElement;
                if (iframe) {
                    if (this.isPlaylistOpen) {
                        // 显示播放列表时，增加iframe高度
                        const playlistHeight = Math.min(400, this.playlist.length * 60 + 20);
                        iframe.style.height = (70 + playlistHeight) + 'px';
                        document.body.classList.add('playlist-open');
                    } else {
                        // 隐藏播放列表时，恢复iframe高度
                        iframe.style.height = '70px';
                        document.body.classList.remove('playlist-open');
                    }
                }
            }
        }
    }
    
    updatePlayButton() {
        const playPauseBtn = document.getElementById('musicPlayPause');
        if (playPauseBtn) {
            const icon = playPauseBtn.querySelector('i');
            if (icon) {
                icon.className = this.isPlaying ? 'fas fa-pause' : 'fas fa-play';
            }
            playPauseBtn.classList.toggle('playing', this.isPlaying);
        }
    }
    
    updateProgress() {
        const progressBar = document.getElementById('musicProgressBar');
        const currentTimeEl = document.getElementById('musicCurrentTime');
        
        if (progressBar && this.duration > 0) {
            const percent = (this.currentTime / this.duration) * 100;
            progressBar.style.width = percent + '%';
        }
        
        if (currentTimeEl) {
            currentTimeEl.textContent = this.formatTime(this.currentTime);
        }
    }
    
    updateDurationDisplay() {
        const durationEl = document.getElementById('musicDuration');
        if (durationEl) {
            durationEl.textContent = this.formatTime(this.duration);
        }
    }
    
    updateVolumeDisplay() {
        const volumeBar = document.getElementById('musicVolumeBar');
        const volumeBtn = document.getElementById('musicVolumeBtn');
        
        if (volumeBar) {
            volumeBar.style.width = (this.audio.volume * 100) + '%';
        }
        
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
    
    updateTrackInfo(track) {
        const titleEl = document.getElementById('musicTitle');
        const artistEl = document.getElementById('musicArtist');
        
        if (titleEl) {
            titleEl.textContent = track.title || '未知歌曲';
        }
        
        if (artistEl) {
            artistEl.textContent = track.artist || '未知艺术家';
        }
    }
    
    updateWaves() {
        const waves = document.getElementById('musicWaves');
        if (waves) {
            waves.classList.toggle('playing', this.isPlaying);
        }
    }
    
    renderPlaylist() {
        const playlist = document.getElementById('musicPlaylist');
        if (!playlist) return;
        
        playlist.innerHTML = '';
        
        this.playlist.forEach((track, index) => {
            const item = document.createElement('div');
            item.className = 'music-player-playlist-item';
            if (index === this.currentTrackIndex) {
                item.classList.add('active');
            }
            
            item.innerHTML = `
                <div class="music-player-playlist-item-icon">
                    <i class="fas fa-music"></i>
                </div>
                <div class="music-player-playlist-item-info">
                    <div class="music-player-playlist-item-title">${track.title || '未知歌曲'}</div>
                    <div class="music-player-playlist-item-artist">${track.artist || '未知艺术家'}</div>
                </div>
            `;
            
            item.addEventListener('click', () => {
                this.loadTrack(index);
                if (this.isPlaying) {
                    this.audio.play();
                }
                // 如果播放列表是打开的，关闭它
                if (this.isPlaylistOpen) {
                    this.togglePlaylist();
                }
            });
            
            playlist.appendChild(item);
        });
    }
    
    updatePlaylistActive() {
        const items = document.querySelectorAll('.music-player-playlist-item');
        items.forEach((item, index) => {
            item.classList.toggle('active', index === this.currentTrackIndex);
        });
    }
    
    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    // 保存状态到localStorage
    saveState() {
        try {
            const state = {
                currentTrackIndex: this.currentTrackIndex,
                currentTime: this.currentTime,
                isPlaying: this.isPlaying,
                volume: this.volume,
                timestamp: Date.now()
            };
            localStorage.setItem('musicPlayerState', JSON.stringify(state));
        } catch (error) {
            console.error('保存播放器状态失败:', error);
        }
    }
    
    // 防抖保存状态
    saveStateDebounced() {
        if (this.saveStateTimer) {
            clearTimeout(this.saveStateTimer);
        }
        this.saveStateTimer = setTimeout(() => {
            this.saveState();
        }, 5000);
    }
    
    // 从localStorage恢复状态
    restoreState() {
        try {
            const savedState = this.getSavedState();
            if (savedState) {
                if (savedState.volume !== undefined) {
                    this.volume = savedState.volume;
                }
            }
        } catch (error) {
            console.error('恢复播放器状态失败:', error);
        }
    }
    
    // 获取保存的状态
    getSavedState() {
        try {
            const saved = localStorage.getItem('musicPlayerState');
            if (saved) {
                const state = JSON.parse(saved);
                // 检查状态是否过期（超过1小时则重置）
                if (Date.now() - state.timestamp > 3600000) {
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
}

// 初始化音乐播放器
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('musicPlayer')) {
        window.musicPlayer = new MusicPlayer();
        
        // 在页面卸载前保存状态
        window.addEventListener('beforeunload', function() {
            if (window.musicPlayer) {
                window.musicPlayer.saveState();
            }
        });
        
        // 在页面隐藏时保存状态（移动设备）
        document.addEventListener('visibilitychange', function() {
            if (document.hidden && window.musicPlayer) {
                window.musicPlayer.saveState();
            }
        });
    }
});

