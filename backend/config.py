from pydantic_settings import BaseSettings


class Settings(BaseSettings):
     
    chroma_persist_dir: str = "./chroma_db"
    rag_model: str = "llama3.1:8b"
    embedding_model: str = "nomic-embed-text"
    ollama_url: str = "http://localhost:11434"

    class Config:
        env_file = ".env"


settings = Settings()
