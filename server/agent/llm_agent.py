from __future__ import annotations
import os
from pathlib import Path
from typing import List


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
import time
from typing import List
from langchain.schema import Document

# ---- Config ----
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b-instruct-q2_K")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
CHROMA_DIR = os.getenv(
    "CHROMA_DIR",
    str(Path(__file__).resolve().parents[1] / "database" / "chroma_events")
)

# ---- Globals ----
_llm = Ollama(
    model=LLM_MODEL,
    base_url=OLLAMA_BASE_URL,
    num_ctx=2048,      # הגדל מ-1024
    num_predict=512,   # הגדל מ-256
    temperature=0.3,   # הגדל מ-0.2
    timeout=60,        # הוסף timeout
)
_embeddings = OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_BASE_URL)
_text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)


def _get_vectorstore() -> Chroma:
    """
    Open (or create) the persistent Chroma vector store.
    """
    db_path = Path(CHROMA_DIR)
    db_path.mkdir(parents=True, exist_ok=True)
    # If a DB exists, reopen it; otherwise Chroma will initialize a new one.
    return Chroma(persist_directory=str(db_path), embedding_function=_embeddings)


def ingest_texts(texts: List[str], source: str = "local_texts", batch_size: int = 64, show_progress: bool = True) -> int:
    """
    Ingest plain texts into the vector store (RAG KB) with simple progress prints.
    Splits texts to chunks, embeds via Ollama, and stores in Chroma.
    """
    t0 = time.time()
    if show_progress:
        print("[ingest] splitting texts...")

    # split -> docs
    docs: List[Document] = []
    for idx, t in enumerate(texts, 1):
        chunks = _splitter.split_text(t)
        docs.extend(Document(page_content=c, metadata={"source": source}) for c in chunks)
        if show_progress:
            print(f"[ingest] split {idx}/{len(texts)} files -> total chunks: {len(docs)}")

    if not docs:
        if show_progress:
            print("[ingest] no content to index.")
        return 0

    vs = _get_vectorstore()

    # add in batches so you see progress (each add triggers embeddings)
    total = len(docs)
    if show_progress:
        print(f"[ingest] embedding & writing {total} chunks in batches of {batch_size}...")

    for i in range(0, total, batch_size):
        j = min(i + batch_size, total)
        vs.add_documents(docs[i:j])
        if show_progress:
            print(f"[ingest] {j}/{total} chunks indexed ({(j/total)*100:.1f}%)")

    # Chroma 0.4.x persists automatically, but keeping the message is useful
    if show_progress:
        print(f"[ingest] done in {time.time() - t0:.1f}s")
    return total


def ask_ai(question: str, show_progress: bool = True) -> str:
    """
    Retrieve-then-answer with Mistral via Ollama. Prints simple progress steps.
    """
    # if show_progress:
    #     print("[ask] opening vector store...")
    # vectordb = _get_vectorstore()
    #
    # if show_progress:
    #     print("[ask] retrieving context...")
    # retriever = vectordb.as_retriever(search_kwargs={"k": 4})
    #
    # prompt = ChatPromptTemplate.from_template(
    #     "You are an events-planning assistant.\n"
    #     "Answer ONLY using the provided context. If unsure, say you don't know.\n\n"
    #     "Context:\n{context}\n\nQuestion: {input}"
    # )
    #
    # if show_progress:
    #     print("[ask] generating answer...")
    # combine_docs_chain = create_stuff_documents_chain(_llm, prompt)
    # chain = create_retrieval_chain(retriever, combine_docs_chain)
    #
    # out = chain.invoke({"input": question})
    # answer = (out.get("answer") or "").strip()
    # if show_progress:
    #     print("[ask] done.")
    #return answer
    # בדוק שהמודל עובד בכלל
    simple_prompt = "What is 2+2?"
    print(_llm.invoke(simple_prompt))
    return "done"
