from qdrant_client import QdrantClient
# from openai import OpenAI # No necesitamos el cliente de OpenAI si usamos Google AI
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import os
import tiktoken
import google.generativeai as genai # Importar la librería de Google AI

load_dotenv()
console = Console()

collection_name = os.getenv("QDRANT_COLLECTION_NAME")

# Configurar la API de Google AI
print(f"DEBUG: GOOGLE_API_KEY value: {os.getenv("GOOGLE_API_KEY")}") # Added debug print
genai.configure(
    api_key=os.getenv("GOOGLE_API_KEY") # Usamos GOOGLE_API_KEY para la clave de Google AI
)

# Obtener los modelos configurados desde .env
EMBEDDING_MODEL = os.getenv("GITHUB_MODELS_MODEL_FOR_EMBEDDINGS", "embedding-001") # Usar default si no está en .env
GENERATION_MODEL = os.getenv("GITHUB_MODELS_MODEL_FOR_GENERATION", "gemini-pro") # Usar default si no está en .env

# Inicializar el cliente de Qdrant
qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"))

def query_embeddings(query):
    console.print(":mag: [bold cyan]Generando embedding para la consulta...[/bold cyan]")
    
    # Usar el modelo de embeddings de Google AI
    print(f"DEBUG: GOOGLE_API_KEY value before embed_content: {os.getenv("GOOGLE_API_KEY")}") # Added debug print
    embedding_response = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=query,
        task_type="retrieval_query"
    )
    # La respuesta de embed_content es un diccionario, el embedding está en 'embedding'
    query_vector = embedding_response['embedding']

    console.print(":satellite: [bold cyan]Buscando documentos similares en Qdrant...[/bold cyan]")
    search_results = qdrant_client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=3,
        with_payload=True
    ).points

    console.print(f":page_facing_up: [bold green]{len(search_results)} resultados encontrados.[/bold green]")
    return search_results

def generate_response_with_embeddings(query, search_results):
    # Inicializar el tokenizador (puede variar si se usa Google AI, pero tiktoken es común)
    # Es posible que necesites ajustar el cálculo de tokens o usar una librería diferente para modelos Gemini
    encoding = tiktoken.get_encoding("cl100k_base") # Esto es para modelos de OpenAI, ten cuidado aquí.
    
    # Calcular tokens para el prompt del sistema y la consulta
    system_prompt = ("Eres un asistente experto en todo lo relacionado al evento FicZone."
                     "Tu tarea es responder a las preguntas de los usuarios utilizando la información proporcionada en el contexto."
                     "Si la información no es suficiente, indícalo y sugiere buscar más información."
                     "Siempre añade la referencia a la fuente de información utilizada para responder, en fragmento si es posible, y al final de la respuesta, utilizando el formato: "
                     "Referencia: [nombre del archivo] [parte del archivo]")
    
    # Estos cálculos de tokens pueden no ser precisos para modelos Gemini con tiktoken.
    system_tokens = len(encoding.encode(system_prompt))
    query_tokens = len(encoding.encode(query))
    
    # Reservar tokens para la respuesta (aproximadamente 1000 tokens)
    reserved_tokens = 1000
    
    # Calcular tokens máximos disponibles para el contexto
    max_context_tokens = 8000 - system_tokens - query_tokens - reserved_tokens # Ten cuidado con el contexto para Gemini
    
    context = ""
    current_tokens = 0
    
    for i, result in enumerate(search_results):
        title = result.payload.get("titulo", "Sin título")
        part = result.payload.get("parte", 0)
        file_name = result.payload.get("archivo", "Sin archivo")
        chunk_text = result.payload.get("text", "No hay texto disponible")
        
        # Calcular tokens para este fragmento (también puede ser inexacto con tiktoken para Gemini)
        chunk_header = f"\n--- Información relevante #{i+1} (de {title}, archivo {file_name}, parte {part}) ---\n"
        chunk_tokens = len(encoding.encode(chunk_header + chunk_text))
        
        # Si añadir este fragmento excedería el límite, detenerse aquí
        if current_tokens + chunk_tokens > max_context_tokens:
            break
            
        context += chunk_header + chunk_text + "\n"
        current_tokens += chunk_tokens

    prompt = f"""Responde a la siguiente consulta utilizando la información proporcionada.\n                Si la información proporcionada no es suficiente para responder, puedes indicarlo.\n\n                Contexto:\n                {context}\n\n                Consulta: {query}\n\n                Respuesta:"""

    console.print(":robot: [bold cyan]Generando respuesta con el modelo...[/bold cyan]")
    
    # Get the model name from environment variables
    generation_model_name = os.getenv("GITHUB_MODELS_MODEL_FOR_GENERATION")

    # Create a GenerativeModel instance
    # generation_model = genai.GenerativeModel(generation_model_name) # This instance is not used

    # Generate content using the model instance
    # response = generation_model.generate_content( # This call is not used
    #     prompt
    # )
    
    # Usar el modelo de generación de Google AI
    print(f"DEBUG: GOOGLE_API_KEY value before generate_content: {os.getenv("GOOGLE_API_KEY")}") # Added debug print
    model = genai.GenerativeModel(GENERATION_MODEL)
    response = model.generate_content(
        [{"role": "user", "parts": [prompt]}]
    )

    # Acceder al texto de la respuesta
    return response.text

# Código de interacción por terminal - INICIO
# 1. Generar un bucle para poder preguntar de forma continua
if __name__ == "__main__":
    while True:
        # Solicitar la consulta al usuario
        query = console.input(":question: [bold blue]¿Cuál es tu consulta? (Escribe 'salir' para terminar): [/bold blue]")
        if query.lower().strip() == "salir":
            console.print(":wave: [bold red]Saliendo...[/bold red]")
            break
        if not query.strip():
            console.print(":warning: [bold red]Consulta vacía. Por favor, introduce una consulta válida.[/red]")
            continue   

        console.print(Panel(f":thinking_face: [bold yellow]Consulta:[/bold yellow] {query}", title="Consulta del usuario"))

        # 2. Obtener los embeddings más similares a la consulta
        search_results = query_embeddings(query)

        # 3. Generar la respuesta utilizando los embeddings como contexto
        result = generate_response_with_embeddings(query, search_results)

        # 4. Imprimir la respuesta generada
        console.print(Panel(Markdown(result), title=":sparkles: Respuesta Generada", subtitle=":clapper: Asistente de FicZone")) 


# Código de interacción por terminal - FIN 