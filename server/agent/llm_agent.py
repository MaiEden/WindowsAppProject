# -*- coding: utf-8 -*-
import os
import re
import json
import hashlib
import requests
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Embeddings + LLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM

# Loaders
from langchain_community.document_loaders import PDFPlumberLoader, TextLoader

# Text splitter
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

# Vector DB + Retriever
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

HEB = re.compile(r'[\u0590-\u05FF]')  # Unicode for Hebrew


def hebrew_visual_to_logical(text: str) -> str:
    """Trying to reverse Hebrew letters extracted from a PDF."""
    if not text or not HEB.search(text):
        return text
    tokens = re.split(r'(\s+)', text)
    fixed = []
    for tok in tokens:
        fixed.append(tok[::-1] if HEB.search(tok) else tok)
    return "".join(fixed)


def normalize_text(t: str) -> str:
    if not t:  # fixes RTL or LTR issues
        return t
    t = t.replace('\u200f', '').replace('\u200e', '')
    t = re.sub(r'[ \t]+\n', '\n', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return hebrew_visual_to_logical(t).strip()


def load_any(path: str):
    # Load any text or PDF file.
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return PDFPlumberLoader(path, extract_images=False).load()
    return TextLoader(path, encoding="utf-8").load()


class MultiPDFRAGAssistant:
    def __init__(
            self,
            source_paths: List[str],
            ollama_host: str = "http://localhost:11434",
            model: str = "gemma:2b-instruct",
            cache_dir: str = "multi_source_cache",
            force_rebuild: bool = False,
    ):
        self.source_paths = source_paths or []
        self.ollama_host = ollama_host
        self.model = model
        self.embeddings_model_name = "intfloat/multilingual-e5-small"
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embeddings_model_name,
            encode_kwargs={"normalize_embeddings": True},
        )

        self.chunk_size = 1600
        self.chunk_overlap = 120

        # cacheing
        self.cache_dir = Path(cache_dir)
        self.index_dir = self.cache_dir / "faiss_index"
        self.manifest_path = self.cache_dir / "manifest.json"
        self.force_rebuild = force_rebuild

        self.vector_store = None
        self.retriever = None
        self.rag_chain = None

    # ---------- caching ----------
    def _compute_manifest(self) -> Dict[str, Any]:
        files = []
        h = hashlib.sha1()
        for p in self.source_paths:
            ap = str(Path(p).resolve())
            st = os.stat(p)
            item = {
                "path": ap,
                "size": st.st_size,
                "mtime": int(st.st_mtime),
            }
            files.append(item)
            h.update(ap.encode("utf-8"))
            h.update(str(st.st_size).encode("utf-8"))
            h.update(str(int(st.st_mtime)).encode("utf-8"))
        manifest = {
            "files": files,
            "hash": h.hexdigest(),
            "embedding_model": self.embeddings_model_name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "model": self.model,
        }
        return manifest

    def _manifest_matches(self, new_manifest: Dict[str, Any]) -> bool:
        if not self.manifest_path.exists():
            return False
        try:
            old = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except Exception:
            return False
        keys = ["hash", "embedding_model", "chunk_size", "chunk_overlap"]
        return all(old.get(k) == new_manifest.get(k) for k in keys)

    # ----------loading and cleaning files----------
    def _load_and_clean_docs(self) -> List[Any]:
        if not self.source_paths:
            raise ValueError("No files were selected.")
        all_docs = []
        for p in self.source_paths:
            try:
                docs = load_any(p)
                for d in docs:
                    d.page_content = normalize_text(d.page_content or "")
                    d.metadata["source_file"] = os.path.basename(p)
                    if "page" not in d.metadata:
                        d.metadata["page"] = None
                all_docs.extend(docs)
                print(f"Loaded: {p}  ({len(docs)} entries/pages)")
            except Exception as e:
                print(f"Error loading {p}: {e}")
        return all_docs

    def _split_docs(self, docs: List[Any]) -> List[Any]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        chunks = splitter.split_documents(docs)
        print(f"number of chunks after splittings: {len(chunks)}")
        return chunks

    # ----------building/ loading vector setor ----------
    def _build_vector(self, documents: List[Any]) -> None:
        self.vector_store = FAISS.from_documents(documents, self.embeddings)

    def _save_vector_store(self) -> None:
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(str(self.index_dir))

    def _load_vector_store(self) -> None:
        self.vector_store = FAISS.load_local(
            str(self.index_dir),
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

    # ---------- Retrieval + Answering chain ----------
    def _build_retriever(self) -> None:
        """
        Build a fast vector-based retriever over the FAISS index.

        - Uses MMR (Maximal Marginal Relevance) to balance relevance + diversity.
        - k=4: return 4 chunks to the LLM (keeps context short and answers fast).
        - fetch_k=12: consider up to 12 candidates before picking the final 4.
        - lambda_mult=0.75: bias more toward relevance than diversity.
        """
        self.retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 4, "fetch_k": 12, "lambda_mult": 0.75},
        )

    def _build_chain(self) -> None:
        """
        Build the end-to-end RAG chain:
          retriever (find chunks) -> prompt (stuff chunks) -> LLM (write the answer).

        LLM options:
          - num_ctx=2048: context window size (keep moderate for speed).
          - num_predict=200: cap answer length for responsiveness.
          - temperature=0.2: low = focused, stable answers.

        Prompt:
          - system: rules (use context only, add 'Sources:' line).
          - human: injects {input} (the user question) and {context} (retrieved chunks).

        IMPORTANT:
          - You must call .invoke({"input": question}) later (key name is 'input').
          - The chain will return 'answer' and 'context' in the result dict.
        """
        llm = OllamaLLM(
            model=self.model,
            base_url=self.ollama_host,
            options={"num_ctx": 2048, "num_predict": 200, "temperature": 0.2},
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system",
                 "You are a professional event-planning assistant. "
                 "Use ONLY the provided context. If context is insufficient, say so briefly and do not invent. "
                 "End every answer with a 'Sources:' line including file names and pages."),
                ("human",
                 "Question:\n{input}\n\nContext (may include multiple chunks from the same document):\n{context}"),
            ]
        )
        doc_chain = create_stuff_documents_chain(llm, prompt)
        self.rag_chain = create_retrieval_chain(self.retriever, doc_chain)

    # ---------- Ollama ----------
    def check_ollama_connection(self) -> Tuple[bool, List[str]]:
        try:
            r = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
            r.raise_for_status()
            models = [m.get("name", "") for m in r.json().get("models", [])]
            ok = self.model in models
            return ok, models
        except Exception as e:
            print(f"No models found. You may need to run: ollama pull gemma:2b-instruct")
            return False, []

    # ---------- Initialization ----------
    def initialize(self) -> bool:
        """
        Initialize the RAG system.

        This function:
            - Checks if the requested Ollama model is available.
            - If a cached FAISS index and manifest match the current source files and settings,
              it loads from disk and skips file processing.
            - Otherwise, it:
                - Loads the source files,
                - Normalizes and chunks them,
                - Builds a new FAISS index,
                - Creates the retriever and QA chain,
                - Saves the new index and a manifest to disk.

        Returns:
            True if the system was initialized successfully.
            False if initialization failed due to missing files or connection problems.
        """

        # If no input files were provided, we cannot initialize
        if not self.source_paths:
            print("No source files provided.")
            return False

        # Check whether the desired model is available on the Ollama server
        ok, models = self.check_ollama_connection()
        if not ok:
            if "gemma:2b-instruct" in models:
                print("Warning: desired model not found. Falling back to gemma:2b-instruct.")
                self.model = "gemma:2b-instruct"
            else:
                print("No suitable model found on the Ollama server. Try: ollama pull gemma:2b-instruct")

        # Compute a manifest (file list + hash + settings)
        manifest = self._compute_manifest()

        # If a cached index + manifest exist, and we're not forcing a rebuild
        if not self.force_rebuild and self.index_dir.exists() and self.manifest_path.exists():
            if self._manifest_matches(manifest):
                try:
                    # Load cached vector store and pipeline
                    self._load_vector_store()
                    self._build_retriever()
                    self._build_chain()
                    print("FAISS loaded from disk. Skipped file loading/processing.")
                    return True
                except Exception as e:
                    print(f"Failed to load FAISS from cache. Rebuilding from scratch: {e}")

        # Full rebuild: load, clean, chunk, embed, and index
        raw_docs = self._load_and_clean_docs()
        chunks = self._split_docs(raw_docs)
        self._build_vector(chunks)
        self._build_retriever()
        self._build_chain()

        # Save FAISS and manifest to disk for future use
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._save_vector_store()
        self.manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        print("System initialized successfully.")
        return True

    def load_from_cache_only(self) -> bool:
        """
            Load FAISS index, retriever, and chain directly from cache
            without checking or knowing the source files.
            Returns True if loaded successfully, False otherwise.
            """
        try:
            if not self.index_dir.exists():
                print("Cache index directory not found:", self.index_dir)
                return False
            self._load_vector_store()
            self._build_retriever()
            self._build_chain()
            print("Loaded from cache successfully (no file list needed).")
            return True
        except Exception as e:
            print(f"Failed to load from cache: {e}")
            return False

    # ---------- שאילתות ----------
    @staticmethod
    def _format_sources(docs: List[Any]) -> str:
        """
        Format a clean, deduplicated string listing the source files and page numbers
        from which the documents were retrieved.

        Args:
            docs (List[Document]): List of LangChain Document objects with metadata.

        Returns:
            str: A human-readable string like:
                 "Sources: File1.pdf (p. 3); File2.pdf (p. 1)"
                 or "Sources: (not identified)" if no metadata was found.
        """
        items, seen = [], set()
        for d in docs:
            src = d.metadata.get("source_file", "Unknown")
            page = d.metadata.get("page")
            label = f"{src} ({page} pages)" if page is not None else src
            if label not in seen:
                seen.add(label)
                items.append(label)
        return "Sources: " + "; ".join(items) if items else "Sources: (not identified)"

    def ask(self, question: str) -> str:
        """
        Ask a question and get a plain text answer (plus formatted sources) from the RAG system.

        Args:
            question (str): The user question

        Returns:
            str: A formatted answer with a line showing source files/pages.
                 If the system is not initialized or answer is empty, returns a message in Hebrew.
        """
        if not self.rag_chain:
            return "Error: The system is not initialized. Please call initialize() first."
        res = self.rag_chain.invoke({"input": question})
        answer = res.get("answer", "").strip()
        ctx_docs = res.get("context", [])
        sources_line = self._format_sources(ctx_docs)
        if not answer:
            return "no answer found."
        return f"{answer}\n\n{sources_line}"


