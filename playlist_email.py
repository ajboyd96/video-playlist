import os

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Video Playlist</title>
  <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css" />
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; background: #111; color: #fff; }
    h1 { margin-bottom: 10px; }
    .video-title { margin: 10px 0; }
    a { color: #1E90FF; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h1>Video Playlist</h1>
  <!-- Initial Player Loading the First Video (Update VIDEO_ID_1 with your actual video ID or URL) -->
  <video id="player" playsinline controls>
    <source src="https://drive.google.com/uc?export=download&id=VIDEO_ID_1" type="video/mp4" />
  </video>
  <div id="playlist">
    <p class="video-title">
      <a href="#" onclick="loadVideo('https://drive.google.com/uc?export=download&id=VIDEO_ID_1'); return false;">
        Introduction to Python
      </a>
    </p>
    <p class="video-title">
      <a href="#" onclick="loadVideo('https://drive.google.com/uc?export=download&id=VIDEO_ID_2'); return false;">
        Loops and Logic
      </a>
    </p>
    <p class="video-title">
      <a href="#" onclick="loadVideo('https://drive.google.com/uc?export=download&id=VIDEO_ID_3'); return false;">
        Functions and Modules
      </a>
    </p>
  </div>
  <script src="https://cdn.plyr.io/3.7.8/plyr.polyfilled.js"></script>
  <script>
    const player = new Plyr('#player');
    function loadVideo(url) {
      player.source = {
        type: 'video',
        sources: [{ src: url, type: 'video/mp4' }]
      };
      player.play();
    }
  </script>
</body>
</html>
"""

# Define an output directory (using the home directory ensures writability)
output_dir = os.path.expanduser("~/temp_playlist")
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, "playlist.html")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Playlist HTML has been created and saved to:\n{output_file}")
