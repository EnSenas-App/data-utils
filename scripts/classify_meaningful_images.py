"""
Image Semantic Content Classifier

This script processes a folder of images and identifies those that contain meaningful semantic
content (like objects, people, or landscapes) as opposed to simple geometric shapes or patterns.
It uses multimodal LLaMa at SambaNova API for image analysis and saves meaningful images to a separate folder.

Usage:
    python classify_meaningful_images.py input_folder [--output_folder output_folder]

Author: Jhon Felipe Delgado
Date: 21/11/2024
"""

import os
import base64
import shutil
import argparse
from pathlib import Path
import openai
from PIL import Image
import io
from typing import Optional, Set

# Constantes globales
VALID_IMAGE_EXTENSIONS: Set[str] = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}

def encode_image_to_base64(image_path: Path) -> str:
    """
    Convert an image file to base64 encoding.

    Args:
        image_path (Path): Path to the image file.

    Returns:
        str: Base64 encoded string of the image.

    Raises:
        IOError: If there's an error reading the image file.
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except IOError as e:
        raise IOError(f"Error reading image file {image_path}: {str(e)}")

def is_meaningful_image(client: openai.OpenAI, image_base64: str) -> bool:
    """
    Analyze an image using SambaNova API to determine if it contains meaningful content.

    This function sends the image to SambaNova's vision model and determines if the image
    contains semantic content (objects, people, landscapes) vs. simple geometric shapes.

    Args:
        client (openai.OpenAI): Configured SambaNova API client.
        image_base64 (str): Base64 encoded image string.

    Returns:
        bool: True if the image contains meaningful content, False otherwise.

    Raises:
        Exception: If there's an error in API communication or response processing.
    """
    try:
        response = client.chat.completions.create(
            model='Llama-3.2-90B-Vision-Instruct',
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analiza esta imagen y responde 'SI' si la imagen contiene "
                            "objetos, personas, paisajes u otro contenido con significado "
                            "semántico. Responde 'NO' si la imagen solo contiene figuras "
                            "geométricas básicas sin significado (como círculos, cuadrados, "
                            "líneas) o patrones abstractos sin contenido reconocible. "
                            "Responde ÚNICAMENTE con SI o NO."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    }
                ]
            }],
            temperature=0.1,
            top_p=0.1
        )
        result = response.choices[0].message.content.strip().upper()
        return result == "SI"
    except Exception as e:
        print(f"Error en el análisis de la imagen: {str(e)}")
        return False

def process_images(input_folder: str, output_folder: str) -> None:
    """
    Process all images in the input folder and copy meaningful ones to the output folder.

    This function:
    1. Configures the SambaNova client
    2. Creates the output folder if it doesn't exist
    3. Processes each image in the input folder
    4. Copies images with meaningful content to the output folder

    Args:
        input_folder (str): Path to the folder containing input images.
        output_folder (str): Path where meaningful images will be saved.

    Raises:
        ValueError: If the input folder doesn't exist or isn't accessible.
    """
    # Validar que la carpeta de entrada existe
    if not os.path.isdir(input_folder):
        raise ValueError(f"La carpeta de entrada no existe: {input_folder}")

    # Configurar el cliente de SambaNova
    client = openai.OpenAI(
        api_key=os.environ.get("SAMBANOVA_API_KEY"),
        base_url="https://api.sambanova.ai/v1",
    )

    # Crear carpeta de salida
    os.makedirs(output_folder, exist_ok=True)

    # Procesar imágenes
    input_path = Path(input_folder)
    processed_count = 0
    meaningful_count = 0

    for file_path in input_path.iterdir():
        if file_path.suffix.lower() in VALID_IMAGE_EXTENSIONS:
            try:
                print(f"Procesando: {file_path.name}")
                processed_count += 1
                
                # Analizar la imagen
                image_base64 = encode_image_to_base64(file_path)
                if is_meaningful_image(client, image_base64):
                    # Copiar imagen significativa
                    output_path = Path(output_folder) / file_path.name
                    shutil.copy2(file_path, output_path)
                    meaningful_count += 1
                    print(f"✓ Imagen con contenido significativo: {file_path.name}")
                else:
                    print(f"✗ Imagen descartada (sin contenido significativo): {file_path.name}")
                    
            except Exception as e:
                print(f"❌ Error procesando {file_path.name}: {str(e)}")

    # Mostrar resumen
    print("\nResumen del procesamiento:")
    print(f"Total de imágenes procesadas: {processed_count}")
    print(f"Imágenes con contenido significativo: {meaningful_count}")
    print(f"Imágenes descartadas: {processed_count - meaningful_count}")

def main() -> None:
    """
    Main entry point of the script.
    
    Configures argument parsing and initiates the image processing workflow.
    """
    parser = argparse.ArgumentParser(
        description='Clasificador de imágenes según contenido semántico',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'input_folder',
        help='Carpeta con las imágenes a procesar'
    )
    parser.add_argument(
        '--output_folder',
        default='imagenes_significativas',
        help='Carpeta donde se guardarán las imágenes con contenido significativo'
    )
    
    args = parser.parse_args()
    
    try:
        process_images(args.input_folder, args.output_folder)
    except Exception as e:
        print(f"Error en la ejecución del script: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()