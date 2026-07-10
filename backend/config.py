from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    chroma_persist_dir: str = "./chroma_db"
    embedding_model: str = "text-embedding-3-small"
    rag_model: str = "gpt-4o-mini"      # <- agregar
    judge_model: str = "gpt-4o"   

    class Config:
        env_file = ".env"


settings = Settings()
