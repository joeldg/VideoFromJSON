### README.md

# VideoFromJSON

This is copy of [VideoFlaskApp](https://github.com/joeldg/VideoFlaskApp) which I want to preserve how it was for a Medium post I am writing about it.
Now, this VideoFromJSON repo will be active devlopment for further enhancements and features of this API as I actively use it. Please provide pull requests here instead of the other.

This is a Flask application that allows you to create videos from a series of image and audio segments. The application supports various features such as zooming, panning, fade effects, audiograms, watermarks, background music, audio volume adjustments, video resolution, and thumbnail generation.

This was almost entirely written by ChatGPT's o1-preview using some well crafted prompts. I did this after work one day in about 4.5hrs and most of that time was fixing issues with nginx in elastic beanstalk.

This has several more features than a web service that costs $99+/month, ties in easily with Make(dot)com workflows and automates multiple issues I had.

All the following was written by the AI designer that generated this fully working app over a fairly epic prompting run.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
  - [Create Video](#1-create-video)
  - [Get Video Status](#2-get-video-status)
  - [List Videos](#3-list-videos)
  - [Delete Video](#4-delete-video)
  - [Upload Pre-roll Video](#5-upload-pre-roll-video)
  - [Upload Post-roll Video](#6-upload-post-roll-video)
  - [Upload Image](#7-upload-image)
  - [Download Video](#8-download-video)
- [Examples](#examples)
- [Notes](#notes)
- [License](#license)

## Features

- Create videos from a series of image and audio segments.
- Support for various transition effects (e.g., fade, wipe, slide).
- Apply zoom and pan effects to images.
- Add audiograms to visualize audio frequencies.
- Overlay watermarks and dynamic text on videos.
- Include pre-roll and post-roll videos.
- Adjust audio volumes and apply audio enhancements.
- Generate thumbnails for videos.
- Support custom resolutions and social media presets (Instagram, TikTok, YouTube).
- Template support for consistent video styles.

## Requirements

- Python 3.12
- Docker
- Docker Compose
- ffmpeg and ffprobe (for local development)

## Installation

### Using Docker (Recommended)

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd VideoFromJSON
    ```

2. Build and start the Docker container:
    ```sh
    docker-compose up --build
    ```

3. The application will be available at `http://localhost:5000`

### Local Development

1. Create and activate a virtual environment:
    ```sh
    # Create a new virtual environment
    python -m venv venv

    # Activate the virtual environment
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows:
    .\venv\Scripts\activate

    # Verify activation (should show path to venv)
    which python
    ```

2. Install dependencies:
    ```sh
    # Upgrade pip first
    python -m pip install --upgrade pip

    # Install project dependencies
    pip install -r requirements.txt
    ```

3. Install ffmpeg and ffprobe:
    - **macOS (using Homebrew):**
      ```sh
      brew install ffmpeg
      ```
    - **Ubuntu/Debian:**
      ```sh
      sudo apt-get install ffmpeg
      ```
    - **Windows:**
      Download from [FFmpeg official website](https://ffmpeg.org/download.html)

4. Run the application:
    ```sh
    # Development mode with auto-reload
    FLASK_APP=application.py FLASK_ENV=development python -m flask run

    # Or directly
    python application.py
    ```

5. Deactivate the virtual environment when done:
    ```sh
    deactivate
    ```

## Command Line Interface (CLI)

The project includes a CLI tool for various operations. To use it, ensure your virtual environment is activated.

### Basic Usage

```sh
# Show help
python -m app.cli --help

# Show specific command help
python -m app.cli process --help

# Show version
python -m app.cli --version
```

### Available Commands

1. **Process Video**
   ```sh
   # Basic usage
   python -m app.cli process <input_video> <platform> [options]

   # Examples with different platforms
   python -m app.cli process video.mp4 youtube
   python -m app.cli process video.mp4 tiktok
   python -m app.cli process video.mp4 instagram
   python -m app.cli process video.mp4 facebook

   # With subtitles
   python -m app.cli process video.mp4 youtube --subtitles subtitles.json

   # With watermark
   python -m app.cli process video.mp4 youtube --watermark "My Brand"

   # With custom resolution
   python -m app.cli process video.mp4 youtube --resolution 1920x1080

   # With output path
   python -m app.cli process video.mp4 youtube --output processed_video.mp4

   # With all options
   python -m app.cli process video.mp4 youtube \
     --subtitles subtitles.json \
     --watermark "My Brand" \
     --resolution 1920x1080 \
     --output processed_video.mp4
   ```

   Options:
   - `--subtitles`: Path to subtitle file (JSON format)
   - `--watermark`: Add watermark text
   - `--resolution`: Set output resolution (e.g., 1920x1080)
   - `--output`: Specify output file path
   - `--quality`: Set video quality (1-10, default: 8)
   - `--fps`: Set frames per second (default: 30)
   - `--audio-volume`: Adjust audio volume (0.0-2.0, default: 1.0)
   - `--background-music`: Add background music file
   - `--background-volume`: Set background music volume (0.0-1.0, default: 0.3)

2. **Create Test Videos**
   ```sh
   # Create a landscape test video
   python -m app.cli create-test-video landscape

   # Create a vertical test video
   python -m app.cli create-test-video vertical

   # Create with custom duration
   python -m app.cli create-test-video landscape --duration 15

   # Create with custom text
   python -m app.cli create-test-video landscape --text "Custom Test Video"

   # Create with background color
   python -m app.cli create-test-video landscape --background-color "#FF0000"
   ```

   Options:
   - `--duration`: Video duration in seconds (default: 10)
   - `--text`: Custom text to display
   - `--background-color`: Hex color code for background
   - `--output`: Custom output path

3. **Clean Temporary Files**
   ```sh
   # Clean files older than 7 days (default)
   python -m app.cli clean-temp

   # Clean files older than specified days
   python -m app.cli clean-temp --days 14

   # Clean specific directories
   python -m app.cli clean-temp --dirs temp_videos temp_images

   # Dry run (show what would be cleaned)
   python -m app.cli clean-temp --dry-run
   ```

   Options:
   - `--days`: Number of days to keep files (default: 7)
   - `--dirs`: Specific directories to clean
   - `--dry-run`: Show what would be cleaned without actually cleaning

4. **Generate Random Data**
   ```sh
   # Generate basic test data
   python -m app.cli generate-random-data

   # Generate with specific number of segments
   python -m app.cli generate-random-data --segments 5

   # Generate with specific duration
   python -m app.cli generate-random-data --duration 30

   # Generate with specific platform
   python -m app.cli generate-random-data --platform tiktok

   # Generate with all options
   python -m app.cli generate-random-data \
     --segments 5 \
     --duration 30 \
     --platform tiktok \
     --output test_data.json
   ```

   Options:
   - `--segments`: Number of segments to generate (default: 3)
   - `--duration`: Total video duration in seconds (default: 15)
   - `--platform`: Target platform (youtube, tiktok, instagram, facebook)
   - `--output`: Output JSON file path

### CLI Configuration

The CLI can be configured using environment variables or a config file:

1. **Environment Variables**:
   ```sh
   # Set default platform
   export VFJ_DEFAULT_PLATFORM=youtube

   # Set default output directory
   export VFJ_OUTPUT_DIR=processed_videos

   # Set log level
   export VFJ_LOG_LEVEL=DEBUG

   # Set API key
   export VFJ_API_KEY=your_api_key
   ```

2. **Config File**:
   Create a `config.json` in your home directory:
   ```json
   {
     "default_platform": "youtube",
     "output_dir": "processed_videos",
     "log_level": "DEBUG",
     "api_key": "your_api_key",
     "temp_dir": "temp",
     "cleanup_days": 7
   }
   ```

### Logging and Debugging

1. **Log Levels**:
   ```sh
   # Set log level via environment variable
   export VFJ_LOG_LEVEL=DEBUG

   # Or via command line
   python -m app.cli process video.mp4 youtube --log-level DEBUG
   ```

   Available levels:
   - `DEBUG`: Detailed information for debugging
   - `INFO`: General information about operations
   - `WARNING`: Warning messages for potential issues
   - `ERROR`: Error messages for failed operations
   - `CRITICAL`: Critical errors that prevent operation

2. **Log File**:
   ```sh
   # Enable log file
   python -m app.cli process video.mp4 youtube --log-file app.log

   # Rotate logs
   python -m app.cli process video.mp4 youtube --log-file app.log --log-rotate
   ```

3. **Debug Mode**:
   ```sh
   # Enable debug mode
   python -m app.cli process video.mp4 youtube --debug

   # Show verbose output
   python -m app.cli process video.mp4 youtube --verbose
   ```

### Common CLI Issues and Solutions

1. **Command Not Found**
   - Ensure virtual environment is activated
   - Verify Python path is correct
   - Check if package is installed
   - Try reinstalling the package:
     ```sh
     pip uninstall videofromjson
     pip install -e .
     ```

2. **Import Errors**
   - Activate virtual environment
   - Reinstall dependencies
   - Check PYTHONPATH
   - Verify package structure:
     ```sh
     python -c "import app.cli; print(app.cli.__file__)"
     ```

3. **Permission Issues**
   - Use appropriate file permissions
   - Run with correct user privileges
   - Check file ownership
   - Fix permissions:
     ```sh
     chmod +x app/cli.py
     chmod -R 755 app/
     ```

4. **Video Processing Issues**
   - Check ffmpeg installation:
     ```sh
     ffmpeg -version
     ```
   - Verify input file format:
     ```sh
     ffprobe input_video.mp4
     ```
   - Check available disk space:
     ```sh
     df -h
     ```

5. **Memory Issues**
   - Monitor memory usage:
     ```sh
     top -p $(pgrep -f "python -m app.cli")
     ```
   - Adjust video quality:
     ```sh
     python -m app.cli process video.mp4 youtube --quality 6
     ```
   - Process smaller segments:
     ```sh
     python -m app.cli process video.mp4 youtube --segment-size 30
     ```

6. **Network Issues**
   - Check internet connection
   - Verify API key validity
   - Test with local files:
     ```sh
     python -m app.cli process video.mp4 youtube --use-local-files
     ```

### Performance Optimization

1. **Video Processing**
   ```sh
   # Use hardware acceleration
   python -m app.cli process video.mp4 youtube --hwaccel

   # Optimize for speed
   python -m app.cli process video.mp4 youtube --fast

   # Use multiple threads
   python -m app.cli process video.mp4 youtube --threads 4
   ```

2. **Resource Management**
   ```sh
   # Set memory limit
   python -m app.cli process video.mp4 youtube --memory-limit 4G

   # Set CPU limit
   python -m app.cli process video.mp4 youtube --cpu-limit 2

   # Set temporary directory
   python -m app.cli process video.mp4 youtube --temp-dir /tmp/video
   ```

## API Endpoints

### 1. Create Video

**Endpoint:** `/api/creation`  
**Method:** `POST`  
**Description:** Creates a video from the provided segments with optional features.

**Request Headers:**
- `X-API-Key`: Your API key.

**Request Body:**
```json
{
  "body": {
    "segments": [
      {
        "imageUrl": "https://example.com/image1.png",
        "audioUrl": "https://example.com/audio1.mp3",
        "volume": 0.8
      },
      {
        "imageUrl": "https://example.com/image2.png",
        "audioUrl": "https://example.com/audio2.mp3",
        "volume": 1.2
      }
    ],
    "zoom_pan": true,
    "fade_effect": "wipeleft",
    "audiogram": {
      "size": "640x480",
      "gamma": 1.5,
      "color": "red",
      "position": "10:10"
    },
    "watermark": {
      "text": "Sample Watermark",
      "position": "10:10",
      "opacity": 0.5
    },
    "background_music": "https://example.com/background_music.mp3",
    "resolution": "1280x720",
    "thumbnail": true,
    "text_overlay": {
      "text": "Sample Text",
      "position": "10:10",
      "font_size": 24,
      "color": "white"
    },
    "filter": {
      "filter_type": "grayscale",
      "intensity": 0.5
    },
    "use_local_files": true
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

### 7. Upload Image

**Endpoint:** `/api/upload_image`  
**Method:** `POST`  
**Description:** Uploads an image.

**Request Body:**
- `file`: The image file.

**Response:**
- `200 OK`: Image uploaded.
  ```json
  {
    "status": "Image uploaded"
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

### 8. Download Video

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

## Web Interface Endpoints

The `/web` endpoints provide a user-friendly web interface to interact with the API functionalities.

- **Home Page**
  - **URL:** `/web`
  - **Description:** Displays links to all available API test pages.

- **Upload Image**
  - **URL:** `/web/upload_image`
  - **Description:** Provides a form to upload an image to a specified directory.

- **Create Video**
  - **URL:** `/web/creation`
  - **Description:** Allows users to create a video from provided segments using a JSON configuration.

- **Check Video Status**
  - **URL:** `/web/status`
  - **Description:** Enables users to check the processing status of a video by entering its Video ID.

- **List Videos**
  - **URL:** `/web/videos`
  - **Description:** Lists all videos available in the `static/videos` directory.

- **Upload Pre-roll Video**
  - **URL:** `/web/pre_roll`
  - **Description:** Provides a form to upload a pre-roll video segment.

- **Upload Post-roll Video**
  - **URL:** `/web/post_roll`
  - **Description:** Provides a form to upload a post-roll video segment.

## Notes

- Ensure that the API key is included in the request headers for endpoints that require it.
- The `fade_effect` must be one of the allowed values: `fade`, `wipeleft`, `wiperight`, `wipeup`, `wipedown`, `slideleft`, `slideright`, `slideup`, `slidedown`, `circlecrop`, `rectcrop`, `distance`, `fadeblack`, `fadewhite`, `radial`, `smoothleft`, `smoothright`, `smoothup`, `smoothdown`, `circleopen`, `circleclose`, `vertopen`, `vertclose`, `horzopen`, `horzclose`, `dissolve`, `pixelize`, `diagtl`, `diagtr`, `diagbl`, `diagbr`, `hlslice`, `hrslice`, `vuslice`, `vdslice`, `hblur`, `fadegrays`, `wipetl`, `wipetr`, `wipebl`, `wipebr`, `squeezeh`, `squeezev`.
- The `audiogram` option allows customization of the audiogram's size, gamma, color, and position.

## Docker Configuration

The project includes a `Dockerfile` and `docker-compose.yml` for containerized deployment:

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./static:/app/static
    environment:
      - FLASK_APP=application.py
      - FLASK_ENV=development
```

## Development Guidelines

1. **Code Style and Structure**
   - Follow PEP 8 guidelines strictly
   - Use type hints for function parameters and return values
   - Add comprehensive docstrings for all functions and classes
   - Keep files under 400 lines; split into logical components if needed
   - Use meaningful variable and function names
   - Group related functionality in appropriate modules
   - Keep the root directory clean; move utility files to appropriate folders

2. **Testing**
   - Write unit tests for all new features
   - Run the full test suite before committing changes
   - Ensure all tests pass in both Docker and local environments
   - Include edge cases and error scenarios in tests
   - Mock external services (Pixabay, etc.) in tests
   - Cache test results in temp directory (7-day retention)
   - Document test requirements and setup in test files

3. **Dependencies**
   - Keep `requirements.txt` up to date with specific versions
   - Document any new dependencies in the README
   - Use virtual environments for local development
   - Pin all dependency versions to ensure reproducibility
   - Regularly update dependencies for security patches
   - Document any system-level dependencies (ffmpeg, etc.)

4. **API Development**
   - Follow RESTful API design principles
   - Include proper error handling and status codes
   - Document all API endpoints with examples
   - Validate all input data
   - Implement rate limiting where appropriate
   - Use consistent response formats
   - Include request/response examples in documentation

5. **Security**
   - Never commit sensitive data or API keys
   - Use environment variables for configuration
   - Implement proper authentication and authorization
   - Validate all user inputs
   - Sanitize file uploads
   - Follow security best practices for file handling
   - Regular security audits of dependencies

6. **Performance**
   - Optimize video processing operations
   - Implement proper resource cleanup
   - Use efficient data structures and algorithms
   - Monitor memory usage in video processing
   - Implement caching where appropriate
   - Profile code for bottlenecks
   - Document performance considerations

7. **Documentation**
   - Keep README.md up to date
   - Document all configuration options
   - Include setup instructions for different environments
   - Provide examples for common use cases
   - Document API endpoints comprehensively
   - Include troubleshooting guides
   - Keep changelog up to date

8. **Version Control**
   - Use meaningful commit messages
   - Create feature branches for new development
   - Review code before merging
   - Keep commits focused and atomic
   - Tag releases appropriately
   - Document breaking changes
   - Follow semantic versioning

9. **Error Handling**
   - Implement comprehensive error handling
   - Log errors appropriately
   - Provide meaningful error messages
   - Handle edge cases gracefully
   - Implement proper cleanup on errors
   - Document error scenarios
   - Include error recovery procedures

10. **Monitoring and Logging**
    - Implement proper logging throughout the application
    - Use appropriate log levels
    - Include request IDs for tracking
    - Monitor application health
    - Track performance metrics
    - Implement proper error reporting
    - Document logging configuration

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.