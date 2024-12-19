function manageTimeBar(elemId, time) {
    if (!window.visTimelineInstances) {
        console.error(`Timeline instances collection not found`);
        return;
    }

    const timeline = window.visTimelineInstances[elemId];
    if (!timeline) {
        console.error(`Timeline instance ${elemId} not found`);
        return;
    }
    
    if (!window.customTimeBarIds) {
        window.customTimeBarIds = {};
    }
    
    try {
        timeline.setCustomTime(time, elemId);
    } catch (e) {
        timeline.addCustomTime(time, elemId);
    }
}

function setTimeBarDirect(elemId, time) {
    manageTimeBar(elemId, time);
}

function setTimeBarNormalized(elemId, start, end, normalizedPos) {
    const time = start + (end - start) * normalizedPos;
    manageTimeBar(elemId, time);
}

class AudioTimelineSync {
    constructor(timelineId, audioId, trackLength) {
        this.timelineId = timelineId;
        this.trackLength = trackLength;
        const container = document.getElementById(audioId);
        
        // Find the progress element through shadow DOM
        const waveform = container.querySelector('#waveform');
        if (!waveform) {
            console.error('Waveform container not found');
            return;
        }

        // Access shadow root and find progress element
        const shadowRoot = waveform.querySelector('div').shadowRoot;
        this.progressElement = shadowRoot.querySelector('div[part="progress"]');
        
        if (!this.progressElement) {
            console.error('Progress element not found');
            return;
        }
        
        this.setupProgressObserver();
    }
    
    setupProgressObserver() {
        // Create mutation observer to watch for style changes to a specific progress element of the audio component
        // The style is defined by the completion of the audio source, even when the audio is not playing but the time bar is being dragged by the cursor.
        this.observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    this.onProgressUpdate();
                }
            });
        });
        
        // Observe the progress element for style changes
        this.observer.observe(this.progressElement, {
            attributes: true,
            attributeFilter: ['style']
        });
    }
    
    onProgressUpdate() {
        const style = this.progressElement.style;
        const widthStr = style.width;
        if (!widthStr) return;
        
        // Convert percentage string to number (e.g., "70.7421%" -> 0.707421)
        const percentage = parseFloat(widthStr) / 100;
        this.syncTimeBarToPlayback(percentage);
    }
    
    syncTimeBarToPlayback(normalizedPosition) {
        const timeline = window.visTimelineInstances[this.timelineId];
        if (timeline) {
            setTimeBarNormalized(this.timelineId, 0, this.trackLength, normalizedPosition);
        }
    }

    cleanup() {
        // Disconnect observer
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }
    }
}

function initAudioSync(timelineId, audioId, trackLength) {
    try {
        // Initialize syncs container if it doesn't exist
        if (!window.audioTimelineSyncs) {
            window.audioTimelineSyncs = {};
        }

        // Cleanup existing sync if any
        if (window.audioTimelineSyncs[timelineId]) {
            window.audioTimelineSyncs[timelineId].cleanup();
        }
        
        // Create new sync instance
        window.audioTimelineSyncs[timelineId] = new AudioTimelineSync(timelineId, audioId, trackLength);
    } catch (error) {
        console.error('Error initializing audio sync:', error);
    }

    return null;
}