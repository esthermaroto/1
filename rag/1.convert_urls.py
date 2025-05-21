from markitdown import MarkItDown
import os
import re
from rich.console import Console

# Esta es la herramienta que nos ayudará a convertir en formato markdown lo que le pasemos
md = MarkItDown()

# Crear una consola de rich
console = Console()

# Para este ejemplo usamos documentación de YouTube relacionadas con los canales y sus vídeos
URLs = [
    {"url": "https://www.ficzone.com/programacion-ficzone-granada-gaming-meeple-factory/", "name": "Programación FicZone"},
    {"url": "https://www.ficzone.com/wp-content/uploads/2025/05/ficzone-sabado-2025.pdf", "name": "Horario FicZone Sábado"},
    {"url": "https://www.ficzone.com/wp-content/uploads/2025/05/ficzone-domingo-2025.pdf", "name": "Horario FicZone Domingo"},
    {"url": "https://www.granadagaming.com/", "name": "Granada Gaming"},
    {"url": "https://www.meeplefactory.es/", "name": "Meeple Factory"},
    {"url": "https://www.ficzone.com/", "name": "FicZone"},
    {"url": "https://www.ficzone.com/invitados-2025/", "name": "Invitados"},
]

# Se crea un directorio para guardar los archivos si no existe
output_dir = "./youtube_guides"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    console.print(f":file_folder: [bold green]Directorio creado:[/bold green] {output_dir}")

# Función para crear un nombre de archivo válido, que no tenga 
def create_valid_filename(name):
    # Reemplazar caracteres no válidos y espacios
    valid_name = re.sub(r'[^\w\s-]', '', name.lower())
    valid_name = re.sub(r'[-\s]+', '_', valid_name)
    return valid_name

# Convertir URLs a Markdown y guardar en archivos
for item in URLs:
    url = item["url"]
    name = item["name"]
    
    # Convertir la URL a contenido markdown
    try:
        result = md.convert(url, headers={
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        })
    except Exception as e:
        console.print(f":x: [bold red]Error al convertir:[/bold red] {url}\n{e}")
        continue
    
    # Crear nombre de archivo válido
    filename = create_valid_filename(name) + ".md"
    filepath = os.path.join(output_dir, filename)
    
    # Guardar contenido en el archivo
    if result:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {name}\n\n")
            # Convertir el resultado a string si no lo es ya
            f.write(result.markdown) 
        console.print(f":white_check_mark: [bold cyan]Archivo guardado:[/bold cyan] {filepath}")
    else:
        console.print(f":x: [bold red]No se pudo convertir la URL:[/bold red] {url}")
