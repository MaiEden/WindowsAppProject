from llm_agent import ingest_texts, ask_ai
from pathlib import Path

base = Path(__file__).parent / "info"

texts = [ (base / fn).read_text(encoding="utf-8") for fn in [
    "events_corporate_playbook_he.md",
    "events_wedding_showcase_he.md",
    "events_community_festival_he.md",
    "events_weather_guidelines_he.md",
]]

#ingest_texts(texts)  # one-time seeding

print(ask_ai("Is it worth holding a product launch in Tel Aviv in September outdoors or indoors, and why?"))
