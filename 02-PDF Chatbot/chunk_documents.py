
from pathlib import Path
import json

from tqdm import tqdm

from core.chunker import chunker

PROCESSED = Path("data/processed")
OUTPUT = Path("data/chunks")

OUTPUT.mkdir(exist_ok=True)

chunker = chunker()

strategy= "recursive"

for file in tqdm(PROCESSED.glob("*.json")):

    with open(file,encoding="utf-8") as f:
        document= json.load(f)

    chunks = []

    chunk_id = 1

    for page in document["content"]:

        text=page["text"]

        if strategy == "fixed":
            result=chunker.fixed_chunks(text)

        elif strategy=="sliding":
            result=chunker.sliding_chunks(text)

        else:
            result = chunker.recursive_chunks(text)

        for chunk in result:

            chunks.append({

                "chunk_id": chunk_id,
                "page":page["page"],
                "text":chunk,
                "length":len(chunk)

            })
            chunk_id +=1

    output={

        "filename":document["filename"],

        "strategy":strategy,

        "total_chunks":len(chunks),

        "chunks":chunks   
    }

    save_path=OUTPUT/(file.stem+"_chunks.json")

    with open(save_path,"w",encoding="utf-8") as out:

        json.dump(output,out,indent=4,ensure_ascii=False)

print("Chunking completed.")
