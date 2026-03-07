import sys
import os
import json

# Add the modules directory to the python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from online import gerar_resposta_online

# Avoid Windows cp1252 print errors for accents/emojis.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Test the function with a sample prompt
response = gerar_resposta_online("Hello, who are you?", "en")
print(json.dumps(response, ensure_ascii=False, indent=2))
