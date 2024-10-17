# Time-Lapse Selfie App

This app processes your collection of selfies to create a time-lapse video where your face remains consistently positioned and colored.

## Features

- Handles images in various formats: **PNG**, **JPG**, **HEIC**
- Detects and aligns faces
- Adjusts color and exposure to maintain consistency
- Assembles images into a time-lapse video

## Requirements

- Python 3.6 or higher
- Install required libraries:

```bash
brew install libheif
brew install ffmpeg
ffmpeg -version # check if ffmpeg is installed
```

- Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

- Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

- Place all your images in the images/input/ folder.
- Ensure you have a reference image (ideally with good lighting and exposure) for color correction.
- Run the script:

```bash
python main.py --input_folder images/input/ --reference_image path/to/reference.jpg
```

**Optional Arguments:**

--output_folder: Folder to save processed images (default: images/processed/)
--output_video: Path to output video file (default: output/timelapse.mp4)
--size: Size (width and height) of output images in pixels (default: 256)
--fps: Frames per second for the output video (default: 24)

**Example:**

```bash
python main.py \
  --input_folder images/input/ \
  --output_folder images/processed/ \
  --output_video output/my_timelapse.mp4 \
  --reference_image images/input/ref_image.jpg \
  --size 512 \
  --fps 30
```

- The final video will be saved to output/timelapse.mp4.

### Notes

- HEIC Images: The app automatically converts HEIC images to JPG.
- Face Detection Failures: Images where a face is not detected will be skipped.
- Logging: Progress and errors are logged to the console.

### Directory Structure

```graphql
time_lapse_app/
├── main.py
├── utils.py
├── requirements.txt
├── README.md
├── images/
│   ├── input/            # Place your original images here
│   └── processed/        # Processed images will be saved here
└── output/
    └── timelapse.mp4     # The final video will be saved here
```
