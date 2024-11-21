import os
from pathlib import Path
import fitz  # PyMuPDF
import io
from PIL import Image, ImageOps

def invert_image(image):
    """
    Invierte los colores de la imagen
    """
    if image.mode == 'RGBA':
        # Separar el canal alpha
        r, g, b, a = image.split()
        rgb_image = Image.merge('RGB', (r, g, b))
        inverted_rgb = ImageOps.invert(rgb_image)
        # Volver a agregar el canal alpha
        r, g, b = inverted_rgb.split()
        return Image.merge('RGBA', (r, g, b, a))
    else:
        return ImageOps.invert(image)

def extract_images_from_pdf(pdf_path):
    """
    Extrae todas las imágenes de un archivo PDF y las guarda en una carpeta con el nombre del PDF
    """
    # Crear nombre de carpeta basado en el nombre del PDF
    pdf_name = Path(pdf_path).stem
    output_dir = Path(pdf_name)
    output_dir.mkdir(exist_ok=True)
    
    # Abrir el PDF
    pdf_document = fitz.open(pdf_path)
    
    # Contador para nombrar las imágenes
    image_count = 0
    
    # Iterar sobre cada página
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        
        # Obtener las imágenes de la página
        image_list = page.get_images()
        
        # Procesar cada imagen
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            
            if base_image:
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                try:
                    # Convertir los bytes a imagen
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Invertir los colores de la imagen
                    inverted_image = invert_image(image)
                    
                    # Crear nombre único para la imagen
                    image_filename = f"imagen_pagina{page_num + 1}_{img_index + 1}.{image_ext}"
                    image_path = output_dir / image_filename
                    
                    # Guardar la imagen
                    inverted_image.save(str(image_path), quality=95, optimize=True)
                    print(f"Imagen guardada: {image_path}")
                    
                    image_count += 1
                    
                except Exception as e:
                    print(f"Error al procesar imagen {image_count}: {str(e)}")
    
    pdf_document.close()
    return image_count

def main():
    # Obtener todos los archivos PDF en el directorio actual
    current_dir = Path('.')
    pdf_files = list(current_dir.glob('*.pdf'))
    
    if not pdf_files:
        print("No se encontraron archivos PDF en el directorio actual")
        return
    
    # Procesar cada PDF
    for pdf_path in pdf_files:
        print(f"\nProcesando: {pdf_path}")
        try:
            num_images = extract_images_from_pdf(pdf_path)
            print(f"Se extrajeron {num_images} imágenes de {pdf_path}")
        except Exception as e:
            print(f"Error al procesar {pdf_path}: {str(e)}")

if __name__ == "__main__":
    main()