# b_analyzer.py
import csv, os, json
from collections import Counter
from datetime import datetime
import re

IN_CSV = "data/products_raw.csv"
OUT_CSV = "data/products_filtered.csv"

def extract_keywords(text):
    # simple splitter; reemplaza por spaCy/RAKE para producción
    tokens = re.findall(r"[a-zA-ZñÑáéíóúÁÉÍÓÚ]{3,}", text.lower())
    common = Counter(tokens)
    return ",".join([k for k,_ in common.most_common(5)])

def score_product(row):
    # regla básica: más reviews + rating alto => score
    try:
        reviews = int(row.get("reviews_count") or 0)
        rating = float(row.get("rating") or 0)
    except:
        reviews = 0; rating = 0.0
    return reviews * (1 + rating/5)

def main():
    if not os.path.exists(IN_CSV):
        print("Analyzer: input no existe")
        return
    out = []
    with open(IN_CSV, encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            row["extracted_keywords"] = extract_keywords(row.get("title","")[:200] + " " + row.get("top_keywords",""))
            row["score_est"] = score_product(row)
            # criterio para shortlist
            if row["score_est"] > 20: 
                row["reason_to_consider"] = "Alta demanda estimada"
            else:
                row["reason_to_consider"] = ""
            out.append(row)
    os.makedirs("data", exist_ok=True)
    keys = list(out[0].keys()) if out else []
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in out:
            w.writerow(r)
    print("Analyzer: procesado", len(out))

if __name__ == "__main__":
    main()
