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

def process_images(input_folder, output_folder, reference_image_path, size, adjust_color_flag):
    logging.info("Starting image processing...")
    reference_image = load_image(reference_image_path) if adjust_color_flag else None

    # Convert HEIC images to JPG
    convert_heic_to_jpg(input_folder)

    image_files = sorted([
        f for f in os.listdir(input_folder)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ])

    for idx, filename in enumerate(image_files):
        image_path = os.path.join(input_folder, filename)
        logging.info(f"Processing {image_path}...")
        try:
            image = load_image(image_path)
            landmarks = get_face_landmarks(image)
            if landmarks is None:
                logging.warning(f"No face detected in {filename}. Skipping.")
                continue
            aligned_image = align_face(image, landmarks, size)
            if adjust_color_flag:
                aligned_image = adjust_color(aligned_image, reference_image)
            resized_image = crop_and_resize(aligned_image, size)  # Resize based on width
            output_path = os.path.join(output_folder, f"img{idx:04d}.jpg")
            resized_image.save(output_path)
        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")

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
