### README.md

# Video Flask App

This is a Flask application that allows you to create videos from a series of image and audio segments. The application supports various features such as zooming, panning, fade effects, audiograms, watermarks, and background music.

## Requirements

- Python 3.12
- Flask 3.1.0
- ffmpeg
- ffprobe

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd videoFlaskApp
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Ensure `ffmpeg` and `ffprobe` are installed on your system.

## Configuration

Configure your Elastic Beanstalk environment by updating the `.elasticbeanstalk/config.yml` file.

## Running the Application

1. Run the Flask application:
    ```sh
    python application.py
    ```

2. The application will be available at `http://localhost:5000`.

## API Endpoints

### 1. Create Video

**Endpoint:** `/api/creation`  
**Method:** `POST`  
**Description:** Creates a video from the provided segments with optional zoom/pan, fade effect, audiogram, watermark, and background music.

**Request Headers:**
- `X-API-Key`: Your API key.

**Request Body:**
```json
{
  "body": {
    "segments": [
      {
        "imageUrl": "https://example.com/image1.png",
        "audioUrl": "https://example.com/audio1.mp3"
      },
      {
        "imageUrl": "https://example.com/image2.png",
        "audioUrl": "https://example.com/audio2.mp3"
      }
    ],
    "zoom_pan": true,  // Optional, default is false
    "fade_effect": "wipeleft",  // Optional, default is 'fade'
    "audiogram": {  // Optional
      "size": "640x480",
      "gamma": 1.5,
      "color": "red",
      "position": "10:10"
    },
    "watermark": {  // Optional
      "text": "Sample Watermark",
      "position": "10:10",
      "opacity": 0.5
    },
    "background_music": "https://example.com/background_music.mp3"  // Optional
  }
}
```

**Response:**
- `200 OK`: Video processing started.
  ```json
  {
    "status": "Processing started",
    "video_id": "<video_id>"
  }
  ```
- `400 Bad Request`: Invalid JSON format or number of segments out of range.
  ```json
  {
    "error": "Invalid JSON format"
  }
  ```
  ```json
  {
    "error": "Number of segments must be between 1 and 20"
  }
  ```
- `401 Unauthorized`: Invalid API key.
  ```json
  {
    "error": "Unauthorized"
  }
  ```

### 2. Get Video Status

**Endpoint:** `/api/status/<video_id>`  
**Method:** `GET`  
**Description:** Retrieves the status of the video processing.

**Response:**
- `200 OK`: Video status retrieved.
  ```json
  {
    "video_id": "<video_id>",
    "status": "Processing"  // or "Completed" or "Failed"
  }
  ```

### 3. List Videos

**Endpoint:** `/api/videos`  
**Method:** `GET`  
**Description:** Lists all processed videos.

**Response:**
- `200 OK`: List of videos.
  ```json
  {
    "videos": ["video1.mp4", "video2.mp4"]
  }
  ```

### 4. Delete Video

**Endpoint:** `/api/videos/<video_id>`  
**Method:** `DELETE`  
**Description:** Deletes a processed video.

**Response:**
- `200 OK`: Video deleted.
  ```json
  {
    "status": "Video deleted"
  }
  ```
- `404 Not Found`: Video not found.
  ```json
  {
    "error": "Video not found"
  }
  ```

### 5. Upload Pre-roll Video

**Endpoint:** `/api/pre_roll`  
**Method:** `POST`  
**Description:** Uploads a pre-roll video.

**Request Body:**
- `file`: The pre-roll video file.

**Response:**
- `200 OK`: Pre-roll video uploaded.
  ```json
  {
    "status": "Pre-roll video uploaded"
  }
  ```
- `400 Bad Request`: No file part or no selected file.
  ```json
  {
    "error": "No file part"
  }
  ```
  ```json
  {
    "error": "No selected file"
  }
  ```

### 6. Upload Post-roll Video

**Endpoint:** `/api/post_roll`  
**Method:** `POST`  
**Description:** Uploads a post-roll video.

**Request Body:**
- `file`: The post-roll video file.

**Response:**
- `200 OK`: Post-roll video uploaded.
  ```json
  {
    "status": "Post-roll video uploaded"
  }
  ```
- `400 Bad Request`: No file part or no selected file.
  ```json
  {
    "error": "No file part"
  }
  ```
  ```json
  {
    "error": "No selected file"
  }
  ```

### 7. Download Video

**Endpoint:** `/download/<filename>`  
**Method:** `GET`  
**Description:** Downloads a processed video.

**Response:**
- `200 OK`: Video file.
- `404 Not Found`: File not found.
  ```json
  {
    "error": "File not found"
  }
  ```

## Notes

- Ensure that the API key is included in the request headers for endpoints that require it.
- The `fade_effect` must be one of the allowed values: `fade`, `wipeleft`, `wiperight`, `wipeup`, `wipedown`, `slideleft`, `slideright`, `slideup`, `slidedown`, `circlecrop`, `rectcrop`, `distance`, `fadeblack`, `fadewhite`, `radial`, `smoothleft`, `smoothright`, `smoothup`, `smoothdown`, `circleopen`, `circleclose`, `vertopen`, `vertclose`, `horzopen`, `horzclose`, `dissolve`, `pixelize`, `diagtl`, `diagtr`, `diagbl`, `diagbr`, `hlslice`, `hrslice`, `vuslice`, `vdslice`, `hblur`, `fadegrays`, `wipetl`, `wipetr`, `wipebl`, `wipebr`, `squeezeh`, `squeezev`.
- The `audiogram` option allows customization of the audiogram's size, gamma, color, and position.