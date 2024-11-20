### README.md

# VideoFromJson

This is a Flask application that allows you to create videos from a series of image and audio segments. The application supports various features such as zooming, panning, fade effects, audiograms, watermarks, background music, audio volume adjustments, video resolution, and thumbnail generation.

This was almost entirely written by ChatGPT's o1-preview using some well crafted prompts.

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
- Flask 3.1.0
- ffmpeg
- ffprobe

## Installation

### Prerequisites

- Python 3.12
- Flask 3.1.0
- `ffmpeg` and `ffprobe` installed and added to your system's PATH
- AWS Account with appropriate permissions
- AWS Elastic Beanstalk CLI (`eb` command)

### Local Installation

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

Ensure that you have `ffmpeg` and `ffprobe` installed on your system. You can install them via:

- **macOS (using Homebrew):**

  ```sh
  brew install ffmpeg
  ```

- **Ubuntu/Debian:**

  ```sh
  sudo apt-get install ffmpeg
  ```

- **Windows:**

  Download the binaries from the [FFmpeg official website](https://ffmpeg.org/download.html) and add them to your system's PATH.

### Deployment to AWS Elastic Beanstalk

Follow these steps to deploy the application to AWS Elastic Beanstalk:

1. **Install the AWS Elastic Beanstalk CLI:**

   - **macOS (using Homebrew):**

     ```sh
     brew install awsebcli
     ```

   - **Windows and Linux:**

     Install via `pip`:

     ```sh
     pip install awsebcli --upgrade
     ```

     Or follow the instructions on the [AWS Elastic Beanstalk CLI Installation Guide](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html).

2. **Configure AWS Credentials:**

   Ensure you have your AWS Access Key ID and Secret Access Key configured.

   ```sh
   aws configure
   ```

   You will be prompted to enter:

   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region name (e.g., `us-west-2`)
   - Default output format (leave blank or set to `json`)

   If you haven't generated access keys, create them in the AWS Management Console under IAM Users.

3. **Initialize the Elastic Beanstalk Application:**

   Navigate to your project directory:

   ```sh
   cd videoFlaskApp
   ```

   Initialize the application:

   ```sh
   eb init
   ```

   During initialization:

   - Select the region where you want to deploy your application.
   - Enter the application name (e.g., `video-flask-app`).
   - Select the platform (choose `3` for Python if prompted).
   - Choose the default Python version (e.g., `Python 3.8`).
   - When asked if you want to set up SSH for your instances, you can choose `yes` or `no` depending on your needs.

4. **Create an Environment:**

   ```sh
   eb create video-flask-app-env
   ```

   Replace `video-flask-app-env` with a unique name for your environment.

   This command creates an environment and deploys the application. It may take a few minutes to complete.

5. **Set Environment Variables:**

   Set necessary environment variables (e.g., `API_KEY`, `SUCCESS_WEBHOOK_URL`, `ERROR_WEBHOOK_URL`):

   ```sh
   eb setenv API_KEY=your_api_key_here SUCCESS_WEBHOOK_URL=your_success_webhook_url ERROR_WEBHOOK_URL=your_error_webhook_url
   ```

6. **Update Application Configurations (if needed):**

   Create a directory named `.ebextensions` in your project root if it doesn't exist:

   ```sh
   mkdir .ebextensions
   ```

   Inside `.ebextensions`, create configuration files (e.g., `python.config`) to install packages or run commands on the EC2 instances.

   **Example (`python.config`):**

   ```yaml
   // filepath: .ebextensions/python.config

   packages:
     yum:
       git: []
       libjpeg-devel: []
       zlib-devel: []
       freetype-devel: []

   commands:
     01_install_ffmpeg:
       command: "sudo amazon-linux-extras install epel -y && sudo yum install -y ffmpeg"

   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: application.py
   ```

7. **Create a Requirements File:**

   Ensure all dependencies are listed in `requirements.txt`:

   ```sh
   pip freeze > requirements.txt
   ```

8. **Deploy the Application:**

   ```sh
   eb deploy
   ```

   This command packages your application and deploys it to the Elastic Beanstalk environment.

9. **Verify the Deployment:**

   After deployment, Elastic Beanstalk provides a URL for your application:

   ```sh
   eb status
   ```

   Access the application using the provided URL.

10. **Managing the Application:**

    - **View Logs:**

      ```sh
      eb logs
      ```

    - **Monitor Health:**

      ```sh
      eb health
      ```

    - **Open the Application in Browser:**

      ```sh
      eb open
      ```

    - **Terminate the Environment:**

      If you want to terminate the environment:

      ```sh
      eb terminate video-flask-app-env
      ```

      Replace `video-flask-app-env` with your environment name.

**Notes:**

- **Database and Storage:** If your application requires a database or persistent storage (like S3), ensure you configure these services and update your application accordingly.

- **Security Groups and Permissions:** Configure security groups to allow necessary inbound and outbound traffic. Adjust IAM roles and permissions as needed.

- **Scaling and Load Balancing:** Elastic Beanstalk can handle scaling. Configure the auto-scaling group and load balancer settings if your application needs to scale based on demand.

- **Custom Domain:** To use a custom domain, configure Route 53 or your DNS provider to point to the Elastic Beanstalk environment URL.

## Configuration

Configure your Elastic Beanstalk environment by updating the `.elasticbeanstalk/config.yml` file.

Modify the `application.py` file to configure the API key and webhook URLs:

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