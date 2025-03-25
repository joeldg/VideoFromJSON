# Project Design Document: VideoFromJSON

Instructions: This file is the design for this folder which contains a Flask web server that works with an API that is another project. This file should be considered as authorative for what to do with how this entire project is organized and run. You as an LLM have license to enforce the following design pattern on the project. When an item in the lists in this file above the horizontal rule mark are completed change the starting "-" to a "*" so I can know you worked on it. If it not entirely complete change the "-" to a "^" and if you need more information change it to a "&" 
You will not access any files outside of the folder VideoFromJSONWeb and its subfolders.

## Overview
VideoFromJSONWeb is a Flask-based web application that allows users to access an API to create custom videos through a web interface that imputs JSON data that specifies various parameters and settings. The API returns the JSON and generates videos with specified segments, effects, audio enhancements, and other customizable features. This interface should be easy to use and always try make every attempt to let users know the status.

### Core technologies
- Vue.js will be used for the web templates
- Primary Flask app must use Python organized into classes
- The application will use classes for all code structure, where possible.
- The application is deployed to AWS Elastic Beanstalk.

### Code style and quality
- Python code will be formatted as Flake8/Black for parts that require Python
- Where possible we must separate structure, so bare JavaScript should be in separate files from HTML and CSS should be in separate files. Each component file should be in a separate directory and organized by type.
- If a file gets to be over 400 lines we must split the file into separate components that are logically similar.
- We must avoid keeping too many files in the root directory; utility files should be moved into appropriately named folder structures.

---
The following is general structure of the project for reference.
---
## Project Structure

### application.py
- The main entry point of the Flask application.
- Initializes the Flask app and set this up on port 5001

### config.py
- Contains configuration variables and constants used throughout the project.
- Manages environment variables and API keys.

### routes.py
- Defines API endpoints and web routes.
- Handles requests and responses for video creation, uploading media, and serving content.

### utils.py
- Contains utility functions for supporting routes.

### templates/
- **base.html**: The base template that other templates extend.
- **creation.html**: Template for the video creation page. Includes forms and scripts for inputting video parameters.
- Additional templates for various web pages.

### static/
- **css/**: Stylesheets for the web application.
- **js/**: Javascript files
- **testfiles/**: Contains background music and sound effects for video creation.
- **uploads/**: Directory for uploaded images and videos.

### ../.env
- Stores environment variables like API keys (not committed to version control).

## Dependencies

### Python Libraries:
- Flask: Web framework for handling HTTP requests and serving content.
- Vue.js: Framework for displaying the UI
- requests: For making HTTP requests to external APIs.
- python-dotenv: For loading environment variables from a .env file.
- Additional libraries listed in ../requirements.txt.

### External Services:
- **Pixabay API**: Used to fetch random images and videos for segments. Requires a valid PIXABAY_API_KEY.

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

## Web Routes

### Web Interface Pages:
- **GET /creation**: Web page for creating videos via a form interface.
- **GET /upload_image**: Page for uploading images.
- **GET /status**: Displays the status of video processing.
- **GET /videos**: Lists available videos for viewing or download.
- **GET /pre_roll**: Page for uploading pre-roll content.
- **GET /post_roll**: Page for uploading post-roll content.
- **GET /**: Default landing page.

## Templates

### base.html
- The foundational HTML structure for the /web frontend.
- Includes blocks for dynamic content insertion.

### creation.html
- Extends base.html.
- Contains a comprehensive form for inputting all video creation parameters.
- Fields include segments JSON, zoom/pan options, fade effects, audiogram settings, watermark configurations, background music selection, resolution choices, and more.
- Includes JavaScript for handling form events and data population.

### Additional Templates
- For other web pages like status, video listings, and media uploads.

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

