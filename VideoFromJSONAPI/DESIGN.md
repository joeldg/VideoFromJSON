# Project Design Document: VideoFromJSON

Instructions: This file is the design for this project and should be considered as authorative for what to do with how this entire API is organized and run. You as an LLM have license to enforce the following design pattern on the project. When an item in the lists in this file above the horizontal rule mark are completed change the starting "-" to a "*" so I can know you worked on it. If it not entirely complete change the "-" to a "^" and if you need more information change it to a "&" if a topic/line doesn't start with a "-" do not work on it at this time.

## Overview
VideoFromJSONAPI is a Flask-based web API that allows users to create custom videos by providing JSON data that specifies various parameters and settings. The application processes the JSON input to generate videos with specified segments, effects, audio enhancements, and other customizable features. It integrates with external APIs, such as Pixabay, to fetch images and videos for video segments, and supports advanced features like audiograms, watermarks, and dynamic text overlays.
You will not access any files outside of the folder VideoFromJSONAPI and its subfolders.

### Core technologies
* Primary Flask app must use Python organized into classes
* Python code is tested via unittest
* The application will use classes for all code structure, where possible.
* The application is integrated with Make.com for posting images and audio that use 'Content-Type: multipart/form-data' POST requests.
* The application is deployed to AWS Elastic Beanstalk.

### Code style and quality
* Where possible we must separate structure and keep similar methods grouped in files.
* If a file gets to be over 400 lines we must split the file into separate components that are logically similar.
* We must avoid keeping too many files in the root directory; utility files should be moved into appropriately named folder structures.
- Unit tests must be organized into a base unit test directory named tests/ and split up by groupings of what they are testing. We must have a unit test for each endpoint that tests success and failure. In the case of the creation endpoint, the unit test will need to be exhaustive as there are many options and combinations.
- Unit tests may use Pixabay where applicable but must cache results in a temp directory where files will remain until their ctime or mtime are greater than seven days. Unit tests can also use files found in the testfiles directory. 
* Python code will be formatted as Flake8/Black

---
The following is general structure of the project for reference.
---
## Project Structure

### application.py
- The main entry point of the Flask application.
- Initializes the Flask app and registers blueprints.

### app/config.py
- Contains configuration variables and constants used throughout the project.
- Manages environment variables and API keys.

### app/routes
- Defines API endpoints and web routes.

### app/utils
- Contains utility functions for processing videos, validating inputs, and other helper functions.

### static/
- **videos/**: Stores generated videos and pre/post-roll content.
- **testfiles/**: Contains background music and sound effects for video creation.
- **uploads/**: Directory for uploaded images and videos.
- **temp_videos/**: Temporary storage for video files during processing.

### requirements.txt
- Lists all Python dependencies required for the project.

### README.md
- Provides an overview and instructions for setting up and running the project.

### ../.env
- Stores environment variables like API keys (not committed to version control).

---
The following are reference 
## Dependencies

### Python Libraries:
- Flask: Web framework for handling HTTP requests and serving content.
- requests: For making HTTP requests to external APIs.
- moviepy: For video editing and processing.
- python-dotenv: For loading environment variables from a .env file.
- unittest2: Enhanced testing framework for unit tests.
- Additional libraries listed in requirements.txt.

### External Services:
- **Pixabay API**: Used to fetch random images and videos for segments. Requires a valid PIXABAY_API_KEY.
- **Webhook URLs**: Used for sending notifications upon successful video processing or errors.

## Configuration

### API Keys:
- **API_KEY**: Used to authenticate API requests to the application.
- **PIXABAY_API_KEY**: Access key for the Pixabay API.

### Environment Variables:
- Stored in the .env file or set in the system environment.
- Includes configuration for API keys, logging levels, and webhook URLs.

### Constants (in config.py):
- **ALLOWED_FADE_EFFECTS**: A set of allowed transition effects between video segments.
- **SOCIAL_MEDIA_PRESETS**: Presets for various social media platforms (e.g., resolution and duration limits).
- **TEMP_VIDEO_DIR**: Directory path for storing temporary video files during processing.
- Paths for pre-roll and post-roll videos.

## API Endpoints

### Video Creation and Management:
- **POST /api/creation**: Creates a video based on provided JSON data.
- **GET /api/status/<video_id>**: Retrieves the processing status of a video.
- **GET /api/videos**: Lists all generated videos.
- **DELETE /api/videos/<video_id>**: Deletes a specified video.

### Media Uploads:
- **POST /api/upload_image/<directory>**: Uploads an image to a specified directory.
- **POST /api/pre_roll**: Uploads a pre-roll video.
- **POST /api/post_roll**: Uploads a post-roll video.

### Downloads and Utilities:
- **GET /download/<filename>**: Allows downloading of generated videos.
- **GET /api/generate_random_data**: Generates random data for testing purposes.
- **GET /health**: Health check endpoint.

## Web Routes

## Main Components

### Video Processing (in utils.py):
- Assembles video segments based on input parameters.
- Applies transitions, effects, overlays, and audio enhancements.
- Manages temporary files and ensures resources are cleaned up after processing.

### API Integrations:
- Interacts with Pixabay API to fetch random media content.
- Uses webhooks to send notifications upon completion or errors.

### Concurrency and Asynchronous Processing:
- Utilizes threading to process video creation requests without blocking the main application.
- Manages processing statuses with thread-safe mechanisms.

### Logging:
- Configured to output logs at various levels (DEBUG, INFO, WARNING, ERROR).
- Helps in tracing execution flow and diagnosing issues.

