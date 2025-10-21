# b_ideator.py
import csv, os, json, time
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
IN_CSV = "data/products_filtered.csv"
OUT_DIR = "output/ideator"
os.makedirs(OUT_DIR, exist_ok=True)

PROMPT_TEMPLATE = """
Eres un experto en e-commerce y productos digitales. Toma este producto base:
Título: {title}
Keywords: {keywords}
Genera 3 ideas de productos digitales (ebooks, plantillas o mini-cursos), cada una con:
- nombre (<=60 chars)
- 5 bullets (beneficios)
- descripción (2-3 frases)
- público objetivo
- 1 idea de bundle o upsell
Devuelve JSON array.
"""

def call_openai(prompt):
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        max_tokens=600,
        temperature=0.8
    )
    return resp["choices"][0]["message"]["content"]

def main():
    if not os.path.exists(IN_CSV):
        print("Ideator: no hay input")
        return
    with open(IN_CSV, encoding="utf-8") as f:
        r = csv.DictReader(f)
        for i,row in enumerate(r):
            prompt = PROMPT_TEMPLATE.format(title=row.get("title",""), keywords=row.get("extracted_keywords",""))
            try:
                out = call_openai(prompt)
            except Exception as e:
                print("OpenAI error:", e)
                continue
            fname = os.path.join(OUT_DIR, f"idea_{i}.json")
            with open(fname, "w", encoding="utf-8") as fw:
                fw.write(json.dumps({"source":row,"idea_raw":out}, ensure_ascii=False))
            print("Ideator: creado", fname)
            time.sleep(1)  # respetar rate limits

if __name__ == "__main__":
    main()
