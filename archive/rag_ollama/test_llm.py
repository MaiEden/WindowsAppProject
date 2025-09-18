# ask_from_cache.py
from llm_agent import MultiPDFRAGAssistant

assistant = MultiPDFRAGAssistant(
    source_paths=[],  # no need to specify source files here, as we are loading from cache
    cache_dir="../../server/agent/multi_source_cache",
    model="gemma:2b-instruct",
    ollama_host="http://localhost:11434"
)

if not assistant.load_from_cache_only():
    print("cant load from cache, exiting.")
    exit()

question = "How do you build a budget for a small wedding?"
print("question: ", question)
print("Answer: \n", assistant.ask(question))
