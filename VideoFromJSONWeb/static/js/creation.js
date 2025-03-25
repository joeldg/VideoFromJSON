document.addEventListener('DOMContentLoaded', function () {
    var config = window.serverData;
    console.log("DOM fully loaded and parsed");

    var videoId = config.videoId;
    if (videoId) {
        pollStatus(videoId);
    }

    console.log("Background Music Files:", config.backgroundMusicFiles);
    console.log("Sound Effect Files:", config.soundEffectFiles);
    console.log("Allowed Fade Effects:", config.allowedFadeEffects);
    console.log("Social Presets:", config.socialPresets);

    // Event Listener for "Generate Random Video" Button
    var generateButton = document.getElementById('generate-random-video');
    if (generateButton) {
        console.log("Generate Random Video button found");
        generateButton.addEventListener('click', function () {
            console.log("Generate Random Video button clicked");

            // Disable the button to prevent multiple clicks
            generateButton.disabled = true;
            console.log("Generate Random Video button disabled");

            fetch(config.apiBaseUrl + '/api/generate_random_data')
                .then(response => response.json())
                .then(data => {
                    console.log("Random Data Received:", data);
                    populateFormFields(data);
                })
                .catch(error => {
                    console.error("Error fetching random data:", error);
                    alert("Failed to generate random video data.");
                })
                .finally(() => {
                    // Re-enable the button after the operation completes
                    generateButton.disabled = false;
                    console.log("Generate Random Video button re-enabled");
                });
        });
    } else {
        console.warn("Generate Random Video button not found");
    }

    // Modify form submission to send as JSON
    var createForm = document.getElementById('create-video-form');
    if (createForm) {
        console.log('Attach submit event listener to create-video-form');

        createForm.addEventListener('submit', function (event) {
            event.preventDefault();
            console.log('Form submission initiated.');

            var formData = new FormData(createForm);
            console.log('FormData object:', formData);

            var jsonData = {};
            formData.forEach(function (value, key) {
                // Parse JSON fields
                if (['segments', 'audiogram', 'watermark', 'audio_enhancement', 'dynamic_text', 'audio_filters', 'segment_audio_effects'].includes(key)) {
                    try {
                        jsonData[key] = JSON.parse(value);
                        console.log(`Form field [${key}] parsed as JSON:`, jsonData[key]);
                    } catch (e) {
                        console.error(`Error parsing JSON for field [${key}]:`, e);
                        jsonData[key] = value;
                    }
                }
                // Convert checkbox values to boolean
                else if (['zoom_pan', 'thumbnail', 'use_local_files'].includes(key)) {
                    jsonData[key] = value === 'on' ? true : false;
                    console.log(`Form field [${key}] converted to boolean:`, jsonData[key]);
                }
                // Handle other fields
                else {
                    jsonData[key] = value;
                    console.log(`Form field [${key}]:`, value);
                }
            });
            console.log('Converted JSON Data:', jsonData);

            fetch(createForm.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jsonData)
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status}`);
                    }
                    console.log('Fetch response received:', response);
                    return response.json();
                })
                .then(data => {
                    console.log('Response JSON data:', data);
                    if (data.video_id) {
                        // Initialize video status section
                        const videoStatus = document.getElementById('video-status');
                        const statusText = document.getElementById('status-text');
                        const videoIdText = document.getElementById('video-id-text'); // Added

                        if (videoStatus && statusText && videoIdText) {
                            videoIdText.innerText = 'Video ID: ' + data.video_id; // Display video ID
                            videoStatus.style.display = 'block';
                            statusText.innerText = 'Processing...';
                            // Start polling for status
                            pollStatus(data.video_id);
                        } else {
                            console.error('Required elements not found.');
                        }
                    } else {
                        alert('Video creation started.');
                    }
                })
                .catch(error => {
                    if (error && typeof error === 'object') {
                        console.error('Fetch error:', error);
                        alert('An error occurred while creating the video.');
                    } else {
                        console.error('Unexpected error:', error);
                        alert('An unexpected error occurred.');
                    }
                });
        });
    } else {
        console.warn("create-video-form not found");
    }
});

// Function to Populate Form Fields with Random Data with Debugging
function populateFormFields(data) {
    console.log('populateFormFields called with data:', data);

    // Populate Segments
    var segmentsField = document.getElementById('segments');
    if (segmentsField) {
        segmentsField.value = JSON.stringify(data.segments, null, 2);
        console.log('Segments field populated with:', segmentsField.value);
    } else {
        console.warn("Segments field not found");
    }

    // Populate Zoom and Pan
    var zoomPanField = document.getElementById('zoom_pan');
    if (zoomPanField) {
        zoomPanField.checked = data.zoom_pan;
        console.log('Zoom and Pan field set to:', zoomPanField.checked);
    } else {
        console.warn("Zoom and Pan field not found");
    }

    // Populate Fade Effect
    var fadeEffectField = document.getElementById('fade_effect');
    if (fadeEffectField) {
        fadeEffectField.value = data.fade_effect;
        console.log('Fade Effect field set to:', fadeEffectField.value);
    } else {
        console.warn("Fade Effect field not found");
    }

    // Populate Intro Music
    var introMusicField = document.getElementById('intro_music');
    if (introMusicField) {
        introMusicField.value = data.intro_music || '';
        console.log('Intro Music field set to:', introMusicField.value);
    } else {
        console.warn("Intro Music field not found");
    }

    // Populate Audiogram
    var audiogramField = document.getElementById('audiogram');
    if (audiogramField) {
        audiogramField.value = JSON.stringify(data.audiogram, null, 2);
        console.log('Audiogram field populated with:', audiogramField.value);
    } else {
        console.warn("Audiogram field not found");
    }

    // Populate Watermark
    var watermarkField = document.getElementById('watermark');
    if (watermarkField) {
        watermarkField.value = JSON.stringify(data.watermark, null, 2);
        console.log('Watermark field populated with:', watermarkField.value);
    } else {
        console.warn("Watermark field not found");
    }

    // Populate Background Music
    var backgroundMusicField = document.getElementById('background_music');
    if (backgroundMusicField) {
        backgroundMusicField.value = data.background_music || '';
        console.log('Background Music field set to:', backgroundMusicField.value);
    } else {
        console.warn("Background Music field not found");
    }

    // Populate Resolution
    var resolutionField = document.getElementById('resolution');
    if (resolutionField) {
        resolutionField.value = data.resolution;
        console.log('Resolution field set to:', resolutionField.value);
    } else {
        console.warn("Resolution field not found");
    }

    // Populate Thumbnail
    var thumbnailField = document.getElementById('thumbnail');
    if (thumbnailField) {
        thumbnailField.checked = data.thumbnail;
        console.log('Thumbnail field set to:', thumbnailField.checked);
    } else {
        console.warn("Thumbnail field not found");
    }

    // Populate Audio Enhancement
    var audioEnhancementField = document.getElementById('audio_enhancement');
    if (audioEnhancementField) {
        audioEnhancementField.value = JSON.stringify(data.audio_enhancement, null, 2);
        console.log('Audio Enhancement field populated with:', audioEnhancementField.value);
    } else {
        console.warn("Audio Enhancement field not found");
    }

    // Populate Dynamic Text
    var dynamicTextField = document.getElementById('dynamic_text');
    if (dynamicTextField) {
        dynamicTextField.value = JSON.stringify(data.dynamic_text, null, 2);
        console.log('Dynamic Text field populated with:', dynamicTextField.value);
    } else {
        console.warn("Dynamic Text field not found");
    }

    // Populate Template
    var templateField = document.getElementById('template');
    if (templateField) {
        templateField.value = data.template || '';
        console.log('Template field set to:', templateField.value);
    } else {
        console.warn("Template field not found");
    }

    // Populate Social Preset
    var socialPresetField = document.getElementById('social_preset');
    if (socialPresetField) {
        socialPresetField.value = data.social_preset || '';
        console.log('Social Preset field set to:', socialPresetField.value);
    } else {
        console.warn("Social Preset field not found");
    }

    // Populate Use Local Files
    var useLocalFilesField = document.getElementById('use_local_files');
    if (useLocalFilesField) {
        useLocalFilesField.checked = data.use_local_files;
        console.log('Use Local Files field set to:', useLocalFilesField.checked);
    } else {
        console.warn("Use Local Files field not found");
    }

    // Populate Audio Filters
    var audioFiltersField = document.getElementById('audio_filters');
    if (audioFiltersField) {
        audioFiltersField.value = JSON.stringify(data.audio_filters, null, 2);
        console.log('Audio Filters field populated with:', audioFiltersField.value);
    } else {
        console.warn("Audio Filters field not found");
    }

    // Populate Segment Audio Effects
    var segmentAudioEffectsField = document.getElementById('segment_audio_effects');
    if (segmentAudioEffectsField) {
        segmentAudioEffectsField.value = JSON.stringify(data.segment_audio_effects, null, 2);
        console.log('Segment Audio Effects field populated with:', segmentAudioEffectsField.value);
    } else {
        console.warn("Segment Audio Effects field not found");
    }

    // Ensure the Generate Random Video button remains enabled
    var generateButton = document.getElementById('generate-random-video');
    if (generateButton) {
        generateButton.disabled = false;
        console.log("Generate Random Video button is enabled");
    }
}

// Add polling function to check video status
function pollStatus(videoId) {
    var checkStatus = setInterval(function () {
        fetch('/api/status/' + videoId)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Status fetch error: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                var statusText = document.getElementById('status-text');
                if (statusText) {
                    statusText.innerText = data.status;
                } else {
                    console.error("status-text element not found");
                }

                if (data.status === "Completed") {
                    clearInterval(checkStatus);
                    var videoSource = document.getElementById('video-source');
                    var videoPlayer = document.getElementById('video-player');

                    if (videoSource && videoPlayer) {
                        videoSource.src = '/api/download/' + videoId + '.mp4';
                        videoPlayer.style.display = 'block';
                        videoPlayer.load(); // Ensure the video element loads the new source
                        videoPlayer.play().catch(error => {
                            console.error('Error playing the video:', error);
                        }); // Attempt to play the video
                    } else {
                        console.error("video-source or video-player element not found");
                    }
                } else if (data.status === "Error") {
                    clearInterval(checkStatus);
                    if (statusText) {
                        statusText.innerText = 'An error occurred during processing.';
                    } else {
                        console.error("status-text element not found");
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching status:', error);
                clearInterval(checkStatus);
                var statusText = document.getElementById('status-text');
                if (statusText) {
                    statusText.innerText = 'Failed to fetch video status.';
                } else {
                    console.error("status-text element not found");
                }
            });
    }, 5000);
}
