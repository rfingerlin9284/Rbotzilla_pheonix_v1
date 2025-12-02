#!/usr/bin/env python3
import sys,json,datetime
q=" ".join(sys.argv[1:]).strip()
if not q:
    print("Usage: ask_rick.py <plain-English question>"); exit(1)
msg={"ts":datetime.datetime.utcnow().isoformat()+"Z","question":q}
print("🗣️  Sent to Rick:", q)
open("prompts/human_inbox.jsonl","a",encoding="utf-8").write(json.dumps(msg)+"\n")
try:
    from util.rick_narrator import RickNarrator
    r=RickNarrator()
    if hasattr(r,"generate_commentary"):
        r.generate_commentary("HUMAN_QUESTION", {"question": q})
        print("✅ Logged to narration")
except Exception as e:
    print(f"⚠️  {e}")
