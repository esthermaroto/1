# Usa una imagen base adecuada para tu proyecto de IA.
# Si tu proyecto es principalmente Python, una imagen de Python es un buen inicio.
FROM python:3.9-slim

# Establece el directorio de trabajo DENTRO del contenedor.
# Esto coincidirá con el 'workspaceFolder' de tu devcontainer.json.
WORKDIR /app

# Copia requirements.txt desde la raíz del contexto de construcción
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto desde la raíz del contexto de construcción
COPY . .

# Comando de inicio de tu aplicación (opcional aquí, ya que 'command' en docker-compose lo define)
CMD ["python", "rag/4.query_embeddings_and_generate_response.py"]