# rebuild_cache.py
from llm_agent import MultiPDFRAGAssistant
files = [
    "42 tips - Google Docs.pdf",
    "Bar Mitzva.pdf",
    "Bat Mitzva.pdf",
    "plaining the best event.pdf",
    "Winter bachelorette party.pdf",
    "צק ליסט למסיבת רווקות מושלמת - Google Docs.pdf",
    "טיפים לאירגון אירועים.pdf",
    "טיפים לחתונות.pdf",
    "טיפים לימי הולדת.pdf",
    "bar_mitzva_checklist_he.md",
    "hafrashat_challah_guide_he.md",
]

a = MultiPDFRAGAssistant(
    source_paths=files,
    ollama_host="http://localhost:11434",
    model="gemma:2b-instruct",
    cache_dir="multi_source_cache",
    force_rebuild=True,          # <- חשוב
)
ok = a.initialize()
print("OK" if ok else "FAILED")
