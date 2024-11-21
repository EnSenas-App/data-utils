# Data ML Utils

Repositorio de utilidades de procesamiento de datos y experimentos de IA/ML. Incluye scripts ETL, exploración de modelos de visión y funciones de procesamiento de texto

## Estructura del Proyecto
```
.
├── README.md
├── requirements.txt
└── scripts
    ├── extractimages.py
    └── classify_meaningful_images.py
```

## Scripts Disponibles

### extractimages.py
Script para extraer todas las imágenes de archivos PDF.

**Uso:**
1. Coloca el archivo PDF en la misma carpeta que el script
2. Ejecuta el script:
```bash
python scripts/extractimages.py
```
3. Las imágenes extraídas se guardarán en una carpeta con el nombre del PDF

### classify_meaningful_images.py
Script que utiliza la API de SambaNova para clasificar imágenes, separando aquellas que contienen contenido semántico significativo (objetos, personas, paisajes) de las que solo contienen figuras geométricas simples o patrones abstractos.

**Requisitos previos:**
```bash
export SAMBANOVA_API_KEY="tu-api-key"
```

**Uso:**
```bash
python scripts/classify_meaningful_images.py carpeta_entrada --output_folder carpeta_salida
```

**Argumentos:**
- `carpeta_entrada`: Ruta a la carpeta que contiene las imágenes a procesar
- `--output_folder`: (Opcional) Carpeta donde se guardarán las imágenes con contenido significativo. Por defecto: "imagenes_significativas"

