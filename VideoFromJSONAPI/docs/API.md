# VideoFromJSON API Documentation

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Credit System](#credit-system)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [Video Creation](#video-creation)
  - [Video Status](#video-status)
  - [Video Management](#video-management)
  - [Media Upload](#media-upload)
  - [Web Interface](#web-interface)
- [Error Handling](#error-handling)
- [Examples](#examples)
  - [Python](#python-examples)
  - [TypeScript](#typescript-examples)
  - [JavaScript](#javascript-examples)
- [Changelog](#changelog)

## Overview

The VideoFromJSON API allows you to create custom videos by providing JSON data that specifies various parameters and settings. The API supports features like:
- Video creation from image and audio segments
- Platform-specific video processing (YouTube, TikTok, Instagram, Facebook)
- Subtitle support with various formats
- Video enhancements (watermarks, transitions, filters)
- Audio processing and adjustments

## Authentication

All API requests require an API key to be included in the `X-API-Key` header:

```http
X-API-Key: your_api_key_here
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:
- 1 request per minute per API key
- Rate limit headers included in responses:
  ```http
  X-RateLimit-Limit: 1
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1616630400
  ```
- When rate limit is exceeded, the API returns a 429 status code with:
  ```json
  {
    "error": "Rate limit exceeded",
    "message": "Rate limit exceeded. Please wait before making another request."
  }
  ```

## Credit System

The API uses a credit-based system with different subscription tiers:

### Free Tier
- 10 video credits per month
- Basic features only
- Rate limit: 1 request/minute

### Starter Plan ($19.99/month)
- 60 video credits per month
- All basic features
- Rate limit: 1 request/minute
- Priority support

### Creator Plan ($39.99/month)
- 150 video credits per month
- All starter features
- Advanced video effects
- Custom watermarks
- Rate limit: 1 request/minute
- Priority support

### Pro Plan ($79.99/month)
- 500 video credits per month
- All creator features
- Custom templates
- Advanced audio processing
- Rate limit: 1 request/minute
- 24/7 priority support

### Credit Information
Each API response includes credit information:
```json
{
  "status": "Processing started",
  "video_id": "abc123xyz",
  "credits": {
    "plan": "starter",
    "credits_total": 60,
    "credits_used": 45,
    "credits_remaining": 15,
    "credits_reset": "2024-04-24T00:00:00",
    "rate_limit": 1,
    "features": ["basic", "priority_support"]
  }
}
```

### Credit Errors
When credits are exhausted, the API returns a 403 status code:
```json
{
  "error": "Credit limit reached",
  "message": "Monthly credit limit reached"
}
```

## Base URL

- Development: `http://localhost:5000/api`
- Production: `https://your-domain.com/api`

## Endpoints

### Video Creation

#### Create Video

```http
POST /creation
Content-Type: application/json
X-API-Key: your_api_key_here
```

**Request Body:**
```json
{
  "body": {
    "segments": [
      {
        "imageUrl": "https://example.com/image1.png",
        "audioUrl": "https://example.com/audio1.mp3",
        "volume": 0.8,
        "duration": 5,
        "zoom_pan": {
          "enabled": true,
          "zoom_factor": 1.2,
          "pan_direction": "left"
        }
      }
    ],
    "zoom_pan": true,
    "fade_effect": "wipeleft",
    "audiogram": {
      "enabled": true,
      "size": "640x480",
      "gamma": 1.5,
      "color": "red",
      "position": "10:10",
      "opacity": 0.7,
      "sensitivity": 0.8,
      "smoothness": 0.5
    },
    "watermark": {
      "text": "Sample Watermark",
      "position": "10:10",
      "opacity": 0.5,
      "font_size": 24,
      "color": "white",
      "font": "Arial",
      "rotation": 0
    },
    "background_music": "https://example.com/background_music.mp3",
    "background_volume": 0.3,
    "resolution": "1280x720",
    "thumbnail": true,
    "text_overlay": {
      "text": "Sample Text",
      "position": "10:10",
      "font_size": 24,
      "color": "white",
      "font": "Arial",
      "animation": "fade_in",
      "duration": 2
    },
    "filter": {
      "filter_type": "grayscale",
      "intensity": 0.5,
      "color_balance": {
        "red": 1.0,
        "green": 1.0,
        "blue": 1.0
      }
    },
    "use_local_files": true,
    "intro_music": "path/to/intro.mp3",
    "outro_music": "path/to/outro.mp3",
    "audio_filters": {
      "normalize": true,
      "compression": {
        "threshold": -20,
        "ratio": 4,
        "attack": 5,
        "release": 50
      },
      "equalizer": {
        "bands": [
          {"frequency": 60, "gain": 2},
          {"frequency": 170, "gain": 1},
          {"frequency": 310, "gain": 0},
          {"frequency": 600, "gain": -1},
          {"frequency": 1000, "gain": -2},
          {"frequency": 3000, "gain": -1},
          {"frequency": 6000, "gain": 0},
          {"frequency": 12000, "gain": 1},
          {"frequency": 14000, "gain": 2},
          {"frequency": 16000, "gain": 3}
        ]
      }
    },
    "segment_audio_effects": [
      {
        "type": "fade_in",
        "duration": 0.5,
        "curve": "linear"
      },
      {
        "type": "fade_out",
        "duration": 0.5,
        "curve": "exponential"
      }
    ],
    "social_preset": "youtube",
    "template": "modern",
    "dynamic_text": {
      "enabled": true,
      "text": "Dynamic Text",
      "position": "center",
      "font_size": 32,
      "color": "white",
      "animation": "bounce",
      "duration": 2,
      "repeat": true
    }
  }
}
```

**Available Options and Parameters:**

1. **Segments** (Required)
   - `imageUrl`: URL or path to the image
   - `audioUrl`: URL or path to the audio file
   - `volume`: Audio volume (0.0-2.0)
   - `duration`: Segment duration in seconds
   - `zoom_pan`: Object containing zoom/pan settings
     - `enabled`: Enable zoom/pan effect
     - `zoom_factor`: Zoom level (1.0-2.0)
     - `pan_direction`: "left", "right", "up", "down"

2. **Fade Effects** (Optional)
   Available values:
   - Basic: "fade", "fadeblack", "fadewhite"
   - Wipe: "wipeleft", "wiperight", "wipeup", "wipedown"
   - Slide: "slideleft", "slideright", "slideup", "slidedown"
   - Crop: "circlecrop", "rectcrop", "distance"
   - Special: "radial", "dissolve", "pixelize"
   - Smooth: "smoothleft", "smoothright", "smoothup", "smoothdown"
   - Circle: "circleopen", "circleclose"
   - Vertical/Horizontal: "vertopen", "vertclose", "horzopen", "horzclose"
   - Diagonal: "diagtl", "diagtr", "diagbl", "diagbr"
   - Slice: "hlslice", "hrslice", "vuslice", "vdslice"
   - Other: "hblur", "fadegrays", "wipetl", "wipetr", "wipebl", "wipebr", "squeezeh", "squeezev"

3. **Audiogram Settings** (Optional)
   - `enabled`: Enable audiogram visualization
   - `size`: Dimensions (e.g., "640x480")
   - `gamma`: Brightness adjustment (0.1-3.0)
   - `color`: Color of the visualization
   - `position`: Position on screen (e.g., "10:10")
   - `opacity`: Transparency (0.0-1.0)
   - `sensitivity`: Audio sensitivity (0.0-1.0)
   - `smoothness`: Smoothing factor (0.0-1.0)

4. **Watermark Settings** (Optional)
   - `text`: Watermark text
   - `position`: Position on screen
   - `opacity`: Transparency (0.0-1.0)
   - `font_size`: Text size
   - `color`: Text color
   - `font`: Font family
   - `rotation`: Rotation angle in degrees

5. **Audio Filters** (Optional)
   - `normalize`: Enable audio normalization
   - `compression`: Audio compression settings
     - `threshold`: dB threshold
     - `ratio`: Compression ratio
     - `attack`: Attack time in ms
     - `release`: Release time in ms
   - `equalizer`: Multi-band equalizer settings
     - `bands`: Array of frequency bands with gain

6. **Segment Audio Effects** (Optional)
   - `type`: Effect type ("fade_in", "fade_out")
   - `duration`: Effect duration in seconds
   - `curve`: Fade curve ("linear", "exponential", "logarithmic")

7. **Dynamic Text** (Optional)
   - `enabled`: Enable dynamic text
   - `text`: Text content
   - `position`: Position on screen
   - `font_size`: Text size
   - `color`: Text color
   - `animation`: Animation type
   - `duration`: Animation duration
   - `repeat`: Enable animation repeat

8. **Social Media Presets** (Optional)
   Available values:
   - "youtube": 1920x1080, 30fps
   - "tiktok": 1080x1920, 30fps
   - "instagram": 1080x1080, 30fps
   - "facebook": 1280x720, 30fps

9. **Templates** (Optional)
   Available values:
   - "modern": Clean, contemporary style
   - "classic": Traditional video style
   - "minimal": Simple, minimal design
   - "dynamic": High-energy, dynamic style

10. **Other Options**
    - `use_local_files`: Use local file paths instead of URLs
    - `intro_music`: Path to intro music file
    - `outro_music`: Path to outro music file
    - `background_volume`: Background music volume (0.0-1.0)
    - `thumbnail`: Generate video thumbnail
    - `resolution`: Custom resolution (e.g., "1920x1080")

**Success Response (200 OK):**
```json
{
  "status": "Processing started",
  "video_id": "abc123xyz"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Invalid JSON format",
  "message": "Missing required field: segments"
}
```

### Video Status

#### Get Video Status

```http
GET /status/{video_id}
X-API-Key: your_api_key_here
```

**Success Response (200 OK):**
```json
{
  "video_id": "abc123xyz",
  "status": "Processing",
  "progress": 45
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "Video not found",
  "message": "Video ID abc123xyz does not exist"
}
```

### Video Management

#### List Videos

```http
GET /videos
X-API-Key: your_api_key_here
```

**Success Response (200 OK):**
```json
{
  "videos": [
    {
      "id": "abc123xyz",
      "filename": "video1.mp4",
      "created_at": "2024-03-24T22:49:00Z",
      "status": "Completed"
    }
  ]
}
```

#### Delete Video

```http
DELETE /videos/{video_id}
X-API-Key: your_api_key_here
```

**Success Response (200 OK):**
```json
{
  "status": "Video deleted"
}
```

### Media Upload

#### Upload Image

```http
POST /upload_image
Content-Type: multipart/form-data
X-API-Key: your_api_key_here
```

**Form Data:**
- `file`: Image file (PNG, JPG, JPEG)

**Success Response (200 OK):**
```json
{
  "status": "Image uploaded",
  "filename": "image1.png"
}
```

#### Upload Pre-roll Video

```http
POST /pre_roll
Content-Type: multipart/form-data
X-API-Key: your_api_key_here
```

**Form Data:**
- `file`: Video file (MP4)

**Success Response (200 OK):**
```json
{
  "status": "Pre-roll video uploaded"
}
```

## Error Handling

The API uses standard HTTP status codes and provides detailed error messages:

- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid API key
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

Error Response Format:
```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

## Examples

### Python Examples

```python
import requests
import json

class VideoFromJSONAPI:
    def __init__(self, api_key, base_url="http://localhost:5000/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def create_video(self, segments, options=None):
        """Create a video from segments."""
        url = f"{self.base_url}/creation"
        data = {
            "body": {
                "segments": segments,
                **(options or {})
            }
        }
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_video_status(self, video_id):
        """Get the status of a video processing job."""
        url = f"{self.base_url}/status/{video_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def upload_image(self, file_path):
        """Upload an image file."""
        url = f"{self.base_url}/upload_image"
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, headers={"X-API-Key": self.api_key}, files=files)
            response.raise_for_status()
            return response.json()

# Usage example
api = VideoFromJSONAPI("your_api_key")

# Create a video
segments = [
    {
        "imageUrl": "https://example.com/image1.png",
        "audioUrl": "https://example.com/audio1.mp3",
        "volume": 0.8
    }
]

options = {
    "zoom_pan": True,
    "fade_effect": "wipeleft",
    "resolution": "1280x720"
}

try:
    result = api.create_video(segments, options)
    video_id = result["video_id"]
    
    # Check status
    status = api.get_video_status(video_id)
    print(f"Video status: {status['status']}")
    
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
```

### TypeScript Examples

```typescript
interface VideoSegment {
  imageUrl: string;
  audioUrl: string;
  volume: number;
}

interface VideoOptions {
  zoom_pan?: boolean;
  fade_effect?: string;
  resolution?: string;
  watermark?: {
    text: string;
    position: string;
    opacity: number;
  };
}

class VideoFromJSONAPI {
  private apiKey: string;
  private baseUrl: string;
  private headers: HeadersInit;

  constructor(apiKey: string, baseUrl: string = "http://localhost:5000/api") {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
    this.headers = {
      "X-API-Key": apiKey,
      "Content-Type": "application/json"
    };
  }

  async createVideo(segments: VideoSegment[], options?: VideoOptions): Promise<any> {
    const url = `${this.baseUrl}/creation`;
    const data = {
      body: {
        segments,
        ...options
      }
    };

    const response = await fetch(url, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async getVideoStatus(videoId: string): Promise<any> {
    const url = `${this.baseUrl}/status/${videoId}`;
    const response = await fetch(url, {
      headers: this.headers
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async uploadImage(file: File): Promise<any> {
    const url = `${this.baseUrl}/upload_image`;
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "X-API-Key": this.apiKey
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }
}

// Usage example
async function main() {
  const api = new VideoFromJSONAPI("your_api_key");

  try {
    const segments: VideoSegment[] = [
      {
        imageUrl: "https://example.com/image1.png",
        audioUrl: "https://example.com/audio1.mp3",
        volume: 0.8
      }
    ];

    const options: VideoOptions = {
      zoom_pan: true,
      fade_effect: "wipeleft",
      resolution: "1280x720"
    };

    const result = await api.createVideo(segments, options);
    const videoId = result.video_id;

    const status = await api.getVideoStatus(videoId);
    console.log(`Video status: ${status.status}`);
  } catch (error) {
    console.error("Error:", error);
  }
}
```

### JavaScript Examples

```javascript
class VideoFromJSONAPI {
  constructor(apiKey, baseUrl = "http://localhost:5000/api") {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
    this.headers = {
      "X-API-Key": apiKey,
      "Content-Type": "application/json"
    };
  }

  async createVideo(segments, options = {}) {
    const url = `${this.baseUrl}/creation`;
    const data = {
      body: {
        segments,
        ...options
      }
    };

    const response = await fetch(url, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async getVideoStatus(videoId) {
    const url = `${this.baseUrl}/status/${videoId}`;
    const response = await fetch(url, {
      headers: this.headers
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async uploadImage(file) {
    const url = `${this.baseUrl}/upload_image`;
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "X-API-Key": this.apiKey
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }
}

// Usage example
async function main() {
  const api = new VideoFromJSONAPI("your_api_key");

  try {
    const segments = [
      {
        imageUrl: "https://example.com/image1.png",
        audioUrl: "https://example.com/audio1.mp3",
        volume: 0.8
      }
    ];

    const options = {
      zoom_pan: true,
      fade_effect: "wipeleft",
      resolution: "1280x720"
    };

    const result = await api.createVideo(segments, options);
    const videoId = result.video_id;

    const status = await api.getVideoStatus(videoId);
    console.log(`Video status: ${status.status}`);
  } catch (error) {
    console.error("Error:", error);
  }
}
```

## Changelog

### v1.0.0 (2024-03-24)
- Initial release
- Basic video creation functionality
- Platform-specific video processing
- Subtitle support
- Video enhancements (watermarks, transitions)
- Media upload capabilities
- Web interface for testing

### v1.1.0 (2024-03-25)
- Added comprehensive test suite
- Docker support
- Enhanced error handling
- Rate limiting implementation
- Improved documentation 