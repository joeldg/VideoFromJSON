from flask import Blueprint, render_template, request, jsonify, current_app
import logging
import os

routes = Blueprint("routes", __name__)

logger = logging.getLogger(__name__)


@routes.route("/web")
def web_index():
    logger.debug("Rendering index.html")
    links = [
        {
            "url": "/test/web",
            "text": "Home",
            "description": "Main page of the VideoFromJSONWeb application",
        },
        {
            "url": "/test/web/upload_image",
            "text": "Upload Image",
            "description": "Upload images for video processing",
        },
        {
            "url": "/test/web/creation",
            "text": "Create Video",
            "description": "Create videos from uploaded images and settings",
        },
        {
            "url": "/test/web/status",
            "text": "Check Status",
            "description": "Check the status of your video processing tasks",
        },
        {
            "url": "/test/web/videos",
            "text": "View Videos",
            "description": "View all created and available videos",
        },
        {
            "url": "/test/web/pre_roll",
            "text": "Pre-Roll",
            "description": "Add pre-roll content to your videos",
        },
        {
            "url": "/test/web/post_roll",
            "text": "Post-Roll",
            "description": "Add post-roll content to your videos",
        },
    ]
    return render_template("index.html", links=links)


@routes.route("/web/upload_image")
def web_upload_image():
    logger.debug("Rendering upload_image.html")
    return render_template("upload_image.html")


@routes.route("/web/creation", methods=["GET", "POST"])
def web_creation():
    logger.debug("Rendering creation.html")
    # Retrieve background music and sound effect files
    background_music_dir = os.path.join("static", "testfiles", "background_music")
    try:
        background_music_files = [
            f"/static/testfiles/background_music/{filename}"
            for filename in os.listdir(background_music_dir)
            if filename.lower().endswith((".mp3", ".wav"))
        ]
    except FileNotFoundError:
        logger.error(f"Directory not found: {background_music_dir}")
        background_music_files = []

    sound_effects_dir = os.path.join("static", "testfiles", "sound_effects")
    try:
        sound_effect_files = [
            f"/static/testfiles/sound_effects/{filename}"
            for filename in os.listdir(sound_effects_dir)
            if filename.lower().endswith((".mp3", ".wav"))
        ]
    except FileNotFoundError:
        logger.error(f"Directory not found: {sound_effects_dir}")
        sound_effect_files = []

    if request.method == "POST":
        # Process form data
        form_data = request.form.to_dict()
        # Convert checkbox values to boolean
        form_data["zoom_pan"] = "zoom_pan" in request.form
        form_data["thumbnail"] = "thumbnail" in request.form
        form_data["use_local_files"] = "use_local_files" in request.form
        # Parse JSON fields
        try:
            form_data["segments"] = json.loads(request.form.get("segments", "[]"))
            form_data["audiogram"] = json.loads(request.form.get("audiogram", "{}"))
            form_data["watermark"] = json.loads(request.form.get("watermark", "{}"))
            form_data["audio_enhancement"] = json.loads(
                request.form.get("audio_enhancement", "{}")
            )
            form_data["dynamic_text"] = json.loads(
                request.form.get("dynamic_text", "{}")
            )
            # Parse additional JSON fields
            form_data["audio_filters"] = json.loads(
                request.form.get("audio_filters", "{}")
            )
            form_data["segment_audio_effects"] = json.loads(
                request.form.get("segment_audio_effects", "[]")
            )
        except json.JSONDecodeError as e:

            # Retrieve background music and sound effect files
            background_music_dir = os.path.join(
                "static", "testfiles", "background_music"
            )
            try:
                background_music_files = [
                    f"/static/testfiles/background_music/{filename}"
                    for filename in os.listdir(background_music_dir)
                    if filename.lower().endswith((".mp3", ".wav"))
                ]
            except FileNotFoundError:
                logger.error(f"Directory not found: {background_music_dir}")
                background_music_files = []

            sound_effects_dir = os.path.join("static", "testfiles", "sound_effects")
            try:
                sound_effect_files = [
                    f"/static/testfiles/sound_effects/{filename}"
                    for filename in os.listdir(sound_effects_dir)
                    if filename.lower().endswith((".mp3", ".wav"))
                ]
            except FileNotFoundError:
                logger.error(f"Directory not found: {sound_effects_dir}")
                sound_effect_files = []

            # Render the template with all necessary variables
            return render_template(
                "creation.html",
                allowed_fade_effects=sorted(current_app.config["ALLOWED_FADE_EFFECTS"]),
                social_presets=list(
                    current_app.config["SOCIAL_MEDIA_PRESETS"].keys()
                ),  # Convert to list
                error="Invalid JSON format in one of the fields.",
                form_data=form_data,
                background_music_files=background_music_files,  # Include this line
                sound_effect_files=sound_effect_files,  # Include this line
            )

        logger.debug(f"Parsed form data: {form_data}")

        # Extract other form fields
        segments = form_data.get("segments", [])
        zoom_pan = form_data.get("zoom_pan", False)
        fade_effect = form_data.get("fade_effect", "fade")
        audiogram = form_data.get("audiogram", {})
        watermark = form_data.get("watermark", {})
        background_music = form_data.get("background_music", None)
        resolution = form_data.get("resolution", "1920x1080")
        thumbnail = form_data.get("thumbnail", False)
        audio_enhancement = form_data.get("audio_enhancement", {})
        dynamic_text = form_data.get("dynamic_text", {})
        template = form_data.get("template", None)
        social_preset = form_data.get("social_preset", None)
        use_local_files = form_data.get("use_local_files", False)

        # Extract new parameters for audio enhancements
        intro_music = form_data.get("intro_music", None)
        outro_music = form_data.get("outro_music", None)
        audio_filters = form_data.get("audio_filters", {})
        segment_audio_effects = form_data.get("segment_audio_effects", [])

        # Handle social preset
        if social_preset:
            preset = current_app.config["SOCIAL_MEDIA_PRESETS"].get(social_preset)
            if preset:
                resolution = preset.get("resolution", resolution)
            else:
                logger.error(f"Invalid social media preset: {social_preset}")
                return render_template(
                    "creation.html",
                    allowed_fade_effects=sorted(
                        current_app.config["ALLOWED_FADE_EFFECTS"]
                    ),
                    social_presets=list(
                        current_app.config["SOCIAL_MEDIA_PRESETS"].keys()
                    ),  # Convert to list
                    error="Invalid social media preset",
                    form_data=form_data,
                )

        # Generate a video ID
        video_id = str(uuid.uuid4())
        logger.info(f"Starting video processing with ID: {video_id}")
        with status_lock:
            video_status[video_id] = "Processing"

        # Start the video processing thread
        thread = threading.Thread(
            target=process_video,
            args=(
                video_id,
                segments,
                zoom_pan,
                fade_effect,
                audiogram,
                watermark,
                background_music,
                resolution,
                thumbnail,
                audio_enhancement,
                dynamic_text,
                template,
                use_local_files,
                video_status,  # Pass video_status
                status_lock,  # Pass status_lock
                intro_music,  # Pass new parameters
                outro_music,
                audio_filters,
                segment_audio_effects,
            ),
        )
        thread.start()

        # Add the following lines to retrieve background music files for POST requests
        background_music_dir = os.path.join("static", "testfiles", "background_music")
        try:
            background_music_files = [
                f"/static/testfiles/background_music/{filename}"
                for filename in os.listdir(background_music_dir)
                if filename.lower().endswith((".mp3", ".wav"))
            ]
        except FileNotFoundError:
            logger.error(f"Directory not found: {background_music_dir}")
            background_music_files = []

        # Add the following lines to retrieve sound effect files
        sound_effects_dir = os.path.join("static", "testfiles", "sound_effects")
        try:
            sound_effect_files = [
                f"/static/testfiles/sound_effects/{filename}"
                for filename in os.listdir(sound_effects_dir)
                if filename.lower().endswith((".mp3", ".wav"))
            ]
        except FileNotFoundError:
            logger.error(f"Directory not found: {sound_effects_dir}")
            sound_effect_files = []

        # Modify the render_template call to include sound_effect_files
        return render_template(
            "creation.html",
            allowed_fade_effects=sorted(current_app.config["ALLOWED_FADE_EFFECTS"]),
            social_presets=list(
                current_app.config["SOCIAL_MEDIA_PRESETS"].keys()
            ),  # Convert to list
            video_id=video_id,  # Pass video_id to the template
            form_data=form_data,
            background_music_files=background_music_files,  # Include background_music_files
            sound_effect_files=sound_effect_files,  # Include sound_effect_files
        )

    else:
        # Add the following lines to retrieve background music files
        background_music_dir = os.path.join("static", "testfiles", "background_music")
        try:
            background_music_files = [
                f"/static/testfiles/background_music/{filename}"
                for filename in os.listdir(background_music_dir)
                if filename.lower().endswith((".mp3", ".wav"))
            ]
        except FileNotFoundError:
            logger.error(f"Directory not found: {background_music_dir}")
            background_music_files = []

        # Add the following lines to retrieve sound effect files
        sound_effects_dir = os.path.join("static", "testfiles", "sound_effects")
        try:
            sound_effect_files = [
                f"/static/testfiles/sound_effects/{filename}"
                for filename in os.listdir(sound_effects_dir)
                if filename.lower().endswith((".mp3", ".wav"))
            ]
        except FileNotFoundError:
            logger.error(f"Directory not found: {sound_effects_dir}")
            sound_effect_files = []

        return render_template(
            "creation.html",
            allowed_fade_effects=sorted(current_app.config["ALLOWED_FADE_EFFECTS"]),
            social_presets=list(
                current_app.config["SOCIAL_MEDIA_PRESETS"].keys()
            ),  # Convert to list
            form_data={},
            background_music_files=background_music_files,  # Pass the list to the template
            sound_effect_files=sound_effect_files,  # Include sound_effect_files
        )


@routes.route("/web/status")
def web_status():
    logger.debug("Rendering status.html")
    return render_template("status.html")


@routes.route("/web/videos")
def web_videos():
    logger.debug("Rendering videos.html")
    return render_template("videos.html")


@routes.route("/web/pre_roll")
def web_pre_roll():
    logger.debug("Rendering pre_roll.html")
    return render_template("pre_roll.html")


@routes.route("/web/post_roll")
def web_post_roll():
    logger.debug("Rendering post_roll.html")
    return render_template("post_roll.html")


@routes.route("/web/uploads")
def web_uploads():
    logger.debug("Rendering uploads.html")
    return render_template("uploads.html")
