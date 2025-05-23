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
print(f"DEBUG: GOOGLE_API_KEY value: {os.getenv('GOOGLE_API_KEY')}") # Added debug print
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
    print(f"DEBUG: GOOGLE_API_KEY value before embed_content: {os.getenv('GOOGLE_API_KEY')}") # Added debug print
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

    # Construir el contexto con la información relevante
    context = ""
    for i, result in enumerate(search_results):
        title = result.payload.get("titulo", "Sin título")
        part = result.payload.get("parte", 0)
        file_name = result.payload.get("archivo", "Sin archivo")
        context += f"\n--- Información relevante #{i+1} (de {title}, archivo {file_name}, parte {part}) ---\n"
        chunk_text = result.payload.get("text", "No hay texto disponible")
        context += chunk_text + "\n"

    # Crear un prompt más amigable, conciso y sin mención de fuentes
    prompt = f"""Por favor, responde a la siguiente consulta de manera amigable, profesional y muy concisa, utilizando la información proporcionada.
                Sé directo y ve al punto, evitando cualquier rodeos innecesario.
                **NUNCA menciones los archivos o fuentes de donde obtuviste la información.**
                Si la información proporcionada no es suficiente para responder, indícalo de manera cordial y sugiere buscar más información externa.

                Contexto:
                {context}

                Consulta: {query}

                Instrucciones clave para la respuesta:
                1. Sé amigable y conversacional, pero siempre directo.
                2. Proporciona la respuesta solicitada de la manera más concisa posible.
                3. **NO menciones NUNCA las fuentes de información (archivos, documentos, etc.).**
                4. Usa lenguaje claro y accesible.
                5. Si la información es insuficiente, dilo claramente y de forma cordial.
                6. Cuando presentes listas, usa viñetas o números.

                Respuesta concisa:"""

    # Configurar el modelo con un prompt del sistema reforzado en concisión y sin fuentes
    system_prompt = """Eres un asistente experto y amigable especializado en FicZone 2025.
                      Tu objetivo es ayudar a los usuarios de manera cordial, profesional y directa.
                      Características de tus respuestas:
                      - Usa un tono conversacional y cercano, pero siempre ve al grano.
                      - Sé empático y comprensivo.
                      - Proporciona información clara y bien estructurada.
                      - Cuando te pregunten por los invitados, SIEMPRE responde con una lista numerada, donde cada invitado esté en una línea nueva.
                      - Si la información es sobre horarios, también preséntala en formato de lista numerada y con su hora correspondiente.
                      - Si te preguntan por las entradas proporciona el precio y este link http://entradasytickets.com/entradas/38 tal cual.
                      - Si no tienes suficiente información, indícalo de manera cordial y sin rodeos.
                      - Mantén un balance entre profesionalismo y claridad.
                      - **Bajo NINGUNA circunstancia menciones las fuentes de información (archivos, documentos, fragmentos, etc.). Actúa como si la información fuera de tu conocimiento general.**
                      - **NO inicies tus respuestas con saludos como 'Hola', '¡Hola!', etc. Ve directamente a responder la consulta.**"""

    # Added debug print
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