function playVideo(buttonNumber) {
    const videoPlayer = document.getElementById('videoPlayer');
    const statusLabel = document.getElementById('status');
    const videoPath = `/static/videos/video${buttonNumber}.mp4`;

    // Update video source and play
    videoPlayer.src = videoPath;
    videoPlayer.load();

    // Log play event before playing the video
    fetch('/log_play', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrf_token')  // If using CSRF protection
        },
        body: `button_number=${buttonNumber}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            videoPlayer.play();
            const buttonNames = {
                1: '55 inch UHD',
                2: '55 Inch Mini LED',
                3: '65 Inch Gaming QLED',
                4: '65 Inch Mini LED'
            };
            statusLabel.textContent = `Playing ${buttonNames[buttonNumber]}`;
        } else {
            statusLabel.textContent = 'Error logging play';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        statusLabel.textContent = 'Error logging play';
    });
}

// Helper function to get CSRF token if you're using it
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}