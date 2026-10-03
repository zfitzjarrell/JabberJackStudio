JabberJack Studio
Create custom talking faces and convert your own videos for the Jabberin' Jack projection pumpkin.

JabberJack Studio has two workflows:

Talking Pumpkin — choose a factory face, add your own audio, and create a talking AMV.
Custom Video — import MP4/MOV/AVI/MKV/etc., fit it to the projector, trim it, keep or mute audio, and convert it to AMV.
Warning

Hardware access is still required
The app creates compatible media files. It does not provide a software-only way to access the pumpkin's storage.

You will need to open the pumpkin and access its internal circuit board. Some versions may require soldering a USB cable or USB connection to the board before the storage can be accessed from a computer. See the following Reddit link for details: https://www.reddit.com/r/halloween/comments/148twxb/tutorial_jabberin_jack_magic_jack_custom_video/

Opening or soldering the unit can damage it and may void any remaining warranty. Make a complete backup of the original storage first. Do not modify or delete the .LIB files.

Talking Pumpkin
Traditional, Funny, Scary, and Angry styles; audio-envelope lip animation; upright preview; 0–30 second end pause; Black, Idle Face, or Idle + Expressions; optional 180° device rotation.

Manufacturer face artwork is not redistributed. In order to get the pumpkin faces, copy the original AMV files from your pumpkin and place them into a folder on your system. Run IMPORT_FACTORY_FACES.bat and select a folder containing your own original AMVs.

Custom Video
MP4, MOV, AVI, MKV, WMV, M4V, WebM
Crop to Fill / Fit with Black Bars / Stretch
Start/end trim
Keep or mute original audio
0–30 second end pause
Black or Hold Final Frame
Upright PC preview
Optional 180° pumpkin rotation
Tested output
208×176, 15 fps, AMV video, ADPCM IMA AMV audio, 22,050 Hz mono, 1,470-sample audio block size.

The factory files observed during development use 16 fps. Modern FFmpeg rejects 16 fps with 22,050-Hz AMV audio; 15 fps divides to exactly 1,470 samples/frame and has worked on tested hardware.

Filename behavior
On tested hardware, the first ten files needed the original factory filenames. Files after slot 10 could use arbitrary names. The app provides slots 1–10 plus Custom (11+).

Install from source
Install Python 3.10+.
Install FFmpeg or place ffmpeg.exe in tools.
pip install -r requirements.txt
Run IMPORT_FACTORY_FACES.bat for Talking Pumpkin mode.
Run RUN_JABBERIN_JACK.bat.
Custom Video mode does not require factory-face import.

Storage notes
Back up the complete drive. Leave AUDIBLE.LIB, EBOOK.LIB, M3U.LIB, MUSIC.LIB, PICTURE.LIB, and VIDEO.LIB alone. Copy generated .amv files to the root alongside the factory AMVs.

Affiliation
JabberJack Studio is an independent community project and is not affiliated with, endorsed by, or sponsored by the manufacturer or trademark owner of Jabberin' Jack.

License
Application source is MIT licensed. Manufacturer media assets are not included.
