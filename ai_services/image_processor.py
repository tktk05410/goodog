import cv2
import numpy as np
import hashlib
import os
from datetime import datetime

class ImageProcessor:
    @staticmethod
    def read_image(image_path_or_bytes):
        if isinstance(image_path_or_bytes, bytes):
            nparr = np.frombuffer(image_path_or_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            img = cv2.imread(image_path_or_bytes)
        return img

    @staticmethod
    def to_grayscale(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def denoise(img, h=10, hColor=10, templateWindowSize=7, searchWindowSize=21):
        if len(img.shape) == 2:
            return cv2.fastNlMeansDenoising(img, None, h, templateWindowSize, searchWindowSize)
        else:
            return cv2.fastNlMeansDenoisingColored(img, None, h, hColor, templateWindowSize, searchWindowSize)

    @staticmethod
    def detect_edges(img, threshold1=50, threshold2=150):
        gray = ImageProcessor.to_grayscale(img)
        return cv2.Canny(gray, threshold1, threshold2)

    @staticmethod
    def resize_image(img, max_dimension=800):
        height, width = img.shape[:2]
        max_dim = max(height, width)
        scale = max_dimension / max_dim
        if scale < 1:
            return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        return img

    @staticmethod
    def extract_histogram(img, bins=256):
        gray = ImageProcessor.to_grayscale(img)
        hist = cv2.calcHist([gray], [0], None, [bins], [0, bins])
        hist = hist.flatten()
        hist = hist / hist.sum()
        return hist

    @staticmethod
    def extract_features(img):
        gray = ImageProcessor.to_grayscale(img)

        hist = ImageProcessor.extract_histogram(gray)

        features = {
            'mean_intensity': float(np.mean(gray)),
            'std_intensity': float(np.std(gray)),
            'contrast': float(np.max(gray) - np.min(gray)),
            'entropy': float(-np.sum(hist * np.log2(hist + 1e-10)))
        }

        return features

    @staticmethod
    def compare_histograms(hist1, hist2):
        return cv2.compareHist(hist1.astype(np.float32), hist2.astype(np.float32), cv2.HISTCMP_CORREL)

    @staticmethod
    def save_processed_image(img, output_dir, original_filename):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_name = hashlib.md5((original_filename + timestamp).encode()).hexdigest()
        filename = f'{hash_name}.jpg'
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, img)
        return filename

def preprocess_pipeline(image_input, output_dir=None):
    img = ImageProcessor.read_image(image_input)
    if img is None:
        raise ValueError('Invalid image input')

    gray = ImageProcessor.to_grayscale(img)

    denoised = ImageProcessor.denoise(gray)

    edges = ImageProcessor.detect_edges(denoised)

    resized = ImageProcessor.resize_image(img)

    return {
        'original': img,
        'grayscale': gray,
        'denoised': denoised,
        'edges': edges,
        'resized': resized
    }

def extract_image_features(image_input):
    img = ImageProcessor.read_image(image_input)
    if img is None:
        raise ValueError('Invalid image input')

    features = ImageProcessor.extract_features(img)

    return features