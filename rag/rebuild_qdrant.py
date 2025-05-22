from qdrant_client import QdrantClient, models
from dotenv import load_dotenv
import os
from rich.console import Console

load_dotenv()
console = Console()

QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "info-ficzone")
VECTOR_DIMENSION = 768 # Dimensión para el modelo embedding-001 de Google AI

if not QDRANT_URL:
    console.print("[bold red]Error: QDRANT_URL no está configurado en el archivo .env[/bold red]")
    exit(1)

console.print(f"[bold blue]Conectando a Qdrant en: {QDRANT_URL}[/bold blue]")
client = QdrantClient(url=QDRANT_URL)

console.print(f"[bold yellow]Intentando eliminar la colección '{COLLECTION_NAME}'...[/bold yellow]")
try:
    client.delete_collection(collection_name=COLLECTION_NAME)
    console.print(f"[bold green]Colección '{COLLECTION_NAME}' eliminada exitosamente.[/bold green]")
except Exception as e:
    console.print(f"[bold yellow]La colección '{COLLECTION_NAME}' no existe o hubo un error al eliminarla: {e}[/bold yellow]")

console.print(f"[bold blue]Creando nueva colección '{COLLECTION_NAME}' con dimensión {VECTOR_DIMENSION}...[/bold blue]")
try:
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=VECTOR_DIMENSION, distance=models.Distance.COSINE)
    )
    console.print(f"[bold green]Colección '{COLLECTION_NAME}' creada exitosamente con dimensión {VECTOR_DIMENSION}.[/bold green]")
except Exception as e:
    console.print(f"[bold red]Error al crear la colección '{COLLECTION_NAME}': {e}[/bold red]")
    exit(1)

console.print("[bold green]Proceso completado. Ahora necesitarás re-indexar tus datos.[/bold green]") 