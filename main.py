# main.py

import os
import argparse
from utils import (
    load_image,
    get_face_landmarks,
    align_face,
    adjust_color,
    create_timelapse,
    convert_heic_to_jpg,
    crop_and_resize
)
from PIL import Image
import logging
from PIL import ImageDraw, ImageFont
from PIL.ExifTags import TAGS
import datetime
import calendar

def get_image_date(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                decoded_tag = TAGS.get(tag, tag)
                if decoded_tag == "DateTimeOriginal":
                    return value.split()[0]  # Return only the date part
    except AttributeError:
        logging.warning("No EXIF data found in image.")
    except Exception as e:
        logging.warning(f"Could not extract date from image: {e}")

    # Fallback to file's last modified date
    timestamp = os.path.getmtime(image_path)
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y:%m:%d')

def overlay_date(image, date_text):
    draw = ImageDraw.Draw(image)
    
    # Load a TrueType font
    try:
        # Provide the full path to the font file if necessary
        font_path = "/Users/radek/Library/Fonts/Montserrat-Bold.otf"  # Update this path
        font = ImageFont.truetype(font_path, 48)  # Adjust the font size as needed
    except IOError:
        logging.warning("TrueType font not found, using default font.")
        font = ImageFont.load_default()  # Fallback to default font if TrueType font is unavailable

    text_position = (20, image.height - 70)  # Adjust position for larger text

    # Draw black border
    draw.text((text_position[0] - 1, text_position[1] - 1), date_text, font=font, fill="black")
    draw.text((text_position[0] + 1, text_position[1] - 1), date_text, font=font, fill="black")
    draw.text((text_position[0] - 1, text_position[1] + 1), date_text, font=font, fill="black")
    draw.text((text_position[0] + 1, text_position[1] + 1), date_text, font=font, fill="black")

    # Draw white text
    draw.text(text_position, date_text, (255, 255, 255), font=font)

    return image

def process_images(input_folder, output_folder, reference_image_path, size, adjust_color_flag):
    logging.info("Starting image processing...")
    reference_image = load_image(reference_image_path) if adjust_color_flag else None

    # Convert HEIC images to JPG
    convert_heic_to_jpg(input_folder)

    # Collect image files with their dates
    image_files_with_dates = []
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder, filename)
            date = get_image_date(image_path)
            if date:
                image_files_with_dates.append((image_path, date))

    # Sort image files by extracted date
    image_files_with_dates.sort(key=lambda x: x[1])

    for idx, (image_path, date) in enumerate(image_files_with_dates):
        logging.info(f"Processing {image_path}...")
        try:
            image = load_image(image_path)
            landmarks = get_face_landmarks(image)
            if landmarks is None:
                logging.warning(f"No face detected in {os.path.basename(image_path)}. Skipping.")
                continue
            aligned_image = align_face(image, landmarks, size)
            if adjust_color_flag:
                aligned_image = adjust_color(aligned_image, reference_image)
            resized_image = crop_and_resize(aligned_image, size)  # Resize based on width

            # Overlay date
            year, month, _ = date.split(':')
            month_name = calendar.month_name[int(month)]
            date_text = f"{year} {month_name}"
            resized_image = overlay_date(resized_image, date_text)

            output_path = os.path.join(output_folder, f"img{idx:04d}.jpg")
            resized_image.save(output_path)
        except Exception as e:
            logging.error(f"Error processing {os.path.basename(image_path)}: {e}")

    logging.info("Image processing completed.")

def main():
    parser = argparse.ArgumentParser(description="Create a time-lapse video from selfies.")
    parser.add_argument('--input_folder', type=str, required=True, help='Path to input images folder')
    parser.add_argument('--output_folder', type=str, default='images/processed/', help='Folder to save processed images')
    parser.add_argument('--output_video', type=str, default='output/timelapse.mp4', help='Path to output video file')
    parser.add_argument('--size', type=int, default=256, help='Size (width and height) of output images')
    parser.add_argument('--fps', type=int, default=24, help='Frames per second for the output video')
    parser.add_argument('--adjust_color', action='store_true', help='Enable color adjustment using reference image')
    parser.add_argument('--reference_image', type=str, help='Path to reference image for color correction')
    args = parser.parse_args()

    if args.adjust_color and not args.reference_image:
        parser.error("--reference_image is required when --adjust_color is set")

    os.makedirs(args.output_folder, exist_ok=True)
    os.makedirs(os.path.dirname(args.output_video), exist_ok=True)

    process_images(args.input_folder, args.output_folder, args.reference_image, args.size, args.adjust_color)
    create_timelapse(args.output_folder, args.output_video, args.fps)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
