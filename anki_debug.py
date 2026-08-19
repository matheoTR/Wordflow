import requests

URL = "http://localhost:8765"
TARGET_MODEL = "wordflow cloze"  # Set to your exact config value

print("--- 1. Checking existing models ---")
res = requests.post(URL, json={"action": "modelNames", "version": 6}).json()
models = res.get("result", [])
print(f"Models found ({len(models)}): {models}")
print(f"Is '{TARGET_MODEL}' in Anki? -> {TARGET_MODEL in models}\n")

print("--- 2. Attempting createModel directly ---")
payload = {
    "action": "createModel",
    "version": 6,
    "params": {
        "modelName": TARGET_MODEL,
        "inOrderFields": ["front", "translation", "additional notes"],
        "isCloze": True,
        "css": ".card { font-size: 20px; }",
        "cardTemplates": [
            {
                "Name": "Wordflow Cloze",
                "Front": "{{cloze:front}}",
                "Back": "{{cloze:front}}<br>{{translation}}",
            }
        ],
    },
}
create_res = requests.post(URL, json=payload).json()
print("createModel raw response:", create_res)
