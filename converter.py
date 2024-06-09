import os
import logging
from pdf2docx import Converter
from docx2pdf import convert
from PIL import Image
import moviepy.editor as mp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_image(input_path, output_format):
    try:
        if output_format.lower() not in ['jpeg', 'png', 'bmp', 'ico', 'jfif']:
            raise ValueError("Unsupported image format")
        output_path = os.path.splitext(input_path)[0] + '.' + output_format
        with Image.open(input_path) as img:
            img.save(output_path)
        logging.info(f"Image converted successfully: {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"Error converting image: {e}")
        return None

def convert_video(input_path, output_format):
    try:
        if output_format.lower() not in ['mp4', 'avi', 'mov', 'webp', 'mkv']:
            raise ValueError("Unsupported video format")
        output_path = os.path.splitext(input_path)[0] + '.' + output_format
        clip = mp.VideoFileClip(input_path)
        clip.write_videofile(output_path, codec='libx264')
        logging.info(f"Video converted successfully: {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"Error converting video: {e}")
        return None


def convert_pdf_to_docx(input_path):
    try:
        if not input_path.lower().endswith('.pdf'):
            raise ValueError("Input file is not a PDF")
        
        output_path = os.path.splitext(input_path)[0] + '.docx'
        cv = Converter(input_path)
        cv.convert(output_path)
        cv.close()
        
        logging.info(f"PDF converted to DOCX successfully: {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"Error converting PDF to DOCX: {e}")
        return None

def convert_docx_to_pdf(input_path):
    try:
        if not input_path.lower().endswith('.docx'):
            raise ValueError("Input file is not a DOCX")
        
        output_path = os.path.splitext(input_path)[0] + '.pdf'
        convert(input_path, output_path)
        
        logging.info(f"DOCX converted to PDF successfully: {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"Error converting DOCX to PDF: {e}")
        return None

def convert_file(input_path, output_format):
    try:
        if not os.path.isfile(input_path):
            raise ValueError("Input path is not a valid file")
        
        ext = input_path.split('.')[-1].lower()
        if ext == 'pdf' and output_format == 'docx':
            return convert_pdf_to_docx(input_path)
        elif ext == 'docx' and output_format == 'pdf':
            return convert_docx_to_pdf(input_path)
        else:
            raise ValueError(f"Unsupported conversion from {ext} to {output_format}")

    except Exception as e:
        logging.error(f"Error converting file: {e}")
        return None