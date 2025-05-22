import os
from dotenv import load_dotenv
import google.generativeai as genai
from rich.console import Console

load_dotenv()
console = Console()

API_KEY = os.getenv("GITHUB_TOKEN")

def list_available_models():
#    genai.configure(api_key=API_KEY) # Commenting out this line
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(m.name)

if not API_KEY:
    console.print("[bold red]Error: GITHUB_TOKEN no está configurado en el archivo .env[/bold red]")
    exit(1)

# genai.configure(api_key=API_KEY) # The configure call should ideally happen in the main app startup

console.print("[bold blue]Listando modelos de generación de contenido disponibles...[/bold blue]")

try:
    # This part seems like the actual execution, might not need the list_available_models function
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            console.print(f"[bold green]- {model.name}[/bold green]")
except Exception as e:
    console.print(f"[bold red]Error al listar modelos: {e}[/bold red]")

console.print("[bold blue]Lista de modelos completada.[/bold blue]") 