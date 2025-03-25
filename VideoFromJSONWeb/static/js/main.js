// This file has been moved to /Users/jgan/Projects/VideoFromJSON/VideoFromJSONWeb/static/js/main.js

new Vue({
    el: '#app',
    data: {
        title: 'API Test Pages',
        description: 'Use the following forms to test and use each of the API endpoints:',
        links: [
            { url: '/web/upload_image', text: 'Upload Image', description: 'Upload an image to a specified directory.' },
            { url: '/web/creation', text: 'Create Video', description: 'Create a video from provided segments.' },
            { url: '/web/status', text: 'Check Video Status', description: 'Check the status of a video by its ID.' },
            { url: '/web/videos', text: 'List Videos', description: 'List all videos in the static/videos directory.' },
            { url: '/web/pre_roll', text: 'Upload Pre-roll Video', description: 'Upload a pre-roll video.' },
            { url: '/web/post_roll', text: 'Upload Post-roll Video', description: 'Upload a post-roll video.' }
        ]
    }
});