from sqlalchemy import Column, Integer, Text, JSON
from pgvector.sqlalchemy import Vector
from db.database import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    
    # BGE-M3 dense embeddings have a dimension of 1024
    dense_embedding = Column(Vector(1024))
    
    # JSON column for sparse lexical data or metadata
    meta_data = Column("metadata", JSON)
