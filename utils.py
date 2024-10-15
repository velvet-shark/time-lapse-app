# utils.py

import os
import numpy as np
from PIL import Image
import face_recognition
import cv2
from skimage.exposure import match_histograms
import pyheif
from pillow_heif import register_heif_opener
import logging

register_heif_opener()

def load_image(path):
    image = Image.open(path)
    return image.convert('RGB')

def convert_heic_to_jpg(image_folder):
    for filename in os.listdir(image_folder):
        if filename.lower().endswith('.heic'):
            image_path = os.path.join(image_folder, filename)
            image = Image.open(image_path)
            new_filename = filename.rsplit('.', 1)[0] + '.jpg'
            new_image_path = os.path.join(image_folder, new_filename)
            image.save(new_image_path, 'JPEG')
            logging.info(f"Converted {filename} to {new_filename}")

def get_face_landmarks(image):
    image_np = np.array(image)
    face_landmarks_list = face_recognition.face_landmarks(image_np)
    if face_landmarks_list:
        return face_landmarks_list[0]
    else:
        return None

def align_face(image, landmarks, size):
    # Desired coordinates (centered face)
    desired_left_eye = (0.35 * size, 0.35 * size)
    desired_right_eye = (0.65 * size, 0.35 * size)

    # Extract the coordinates of the left and right eye
    left_eye_pts = landmarks['left_eye']
    right_eye_pts = landmarks['right_eye']

    left_eye_center = np.mean(left_eye_pts, axis=0)
    right_eye_center = np.mean(right_eye_pts, axis=0)

    # Compute the angle between the eye centroids
    dy = right_eye_center[1] - left_eye_center[1]
    dx = right_eye_center[0] - left_eye_center[0]
    angle = np.degrees(np.arctan2(dy, dx))

    # Calculate the scale of the new face
    dist = np.linalg.norm(right_eye_center - left_eye_center)
    desired_dist = (desired_right_eye[0] - desired_left_eye[0])
    scale = desired_dist / dist

    # Compute center between the eyes
    eyes_center = ((left_eye_center[0] + right_eye_center[0]) / 2,
                   (left_eye_center[1] + right_eye_center[1]) / 2)

    # Get the rotation matrix
    M = cv2.getRotationMatrix2D(eyes_center, angle, scale)

    # Adjust the translation component of the matrix
    tX = size * 0.5
    tY = size * 0.4
    M[0, 2] += (tX - eyes_center[0])
    M[1, 2] += (tY - eyes_center[1])

    # Apply the affine transformation
    aligned_image = cv2.warpAffine(
        np.array(image),
        M,
        (size, size),
        flags=cv2.INTER_CUBIC
    )

    return Image.fromarray(aligned_image)

def adjust_color(image, reference):
    matched = match_histograms(
        np.array(image),
        np.array(reference)
    )
    return Image.fromarray(np.uint8(matched))

def create_timelapse(image_folder, output_video, fps):
    from moviepy.editor import ImageSequenceClip
    image_files = sorted([
        os.path.join(image_folder, img)
        for img in os.listdir(image_folder)
        if img.endswith('.jpg')
    ])
    if not image_files:
        logging.error("No images found to create the video.")
        return
    clip = ImageSequenceClip(image_files, fps=fps)
    clip.write_videofile(output_video, codec='libx264')
    logging.info(f"Video saved to {output_video}")

def crop_and_resize(image, size):
    width, height = image.size
    new_width, new_height = size, size

    left = (width - new_width) / 2
    top = (height - new_height) / 2
    right = (width + new_width) / 2
    bottom = (height + new_height) / 2

    image = image.crop((left, top, right, bottom))
    return image.resize((size, size), Image.ANTIALIAS)
