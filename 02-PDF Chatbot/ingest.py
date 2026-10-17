
from pathlib import Path
import json

from tqdm import tqdm
from core.pdf_loader import PDFLoader
from core.utils import word_count, character_count

RAW_DIR = Path("data/raw")

PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok= True)

def process_pdf(pdf_path):

    loader = PDFLoader(pdf_path)

    pages = loader.extract_text()

    page_data=[]

    for page_number, text in enumerate(pages,start=1):

        page_data.append({

            "page":page_number,
            "text":text,
            "words": word_count(text),
            "characters": character_count(text)
        })

    document = {

        "filename":Path(pdf_path).name,
        "pages": loader.page_count(),
        "content": page_data
    }

    output = PROCESSED_DIR/(Path(pdf_path).stem+".json")

    with open(output,"w", encoding="utf-8") as f:
        json.dump(document,f, indent=4, ensure_ascii=False)

    print(f"Saved -> {output}")

def main():

    pdfs = list(RAW_DIR.glob("*.pdf"))

    if not pdfs:
        print("No PDFs found.")
        return

    for pdf in tqdm(pdfs):
        process_pdf(pdf)

if __name__=="__main__":

    main()
