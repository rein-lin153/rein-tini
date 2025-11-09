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
        });
        
        this.audio.addEventListener('ended', () => {
            this.next();
        });
        
        this.audio.addEventListener('play', () => {
            this.isPlaying = true;
            this.updatePlayButton();
            this.updateWaves();
        });
        
        this.audio.addEventListener('pause', () => {
            this.isPlaying = false;
            this.updatePlayButton();
            this.updateWaves();
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
            if (data.success && data.music_list) {
                this.playlist = data.music_list;
                if (this.playlist.length > 0) {
                    this.currentTrackIndex = 0;
                    this.loadTrack(this.currentTrackIndex);
                    this.renderPlaylist();
                }
            }
        } catch (error) {
            console.error('加载播放列表失败:', error);
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
                this.togglePlaylist();
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
}

// 初始化音乐播放器
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('musicPlayer')) {
        window.musicPlayer = new MusicPlayer();
    }
});

