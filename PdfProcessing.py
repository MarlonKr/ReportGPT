import tiktoken
import os
import json
import PyPDF4
import re

from GptCall import gpt_call
from prompts import *

def clean_and_translate(text,MODELS):
    prompt, system_message = get_prompt_clean_and_translate(text)
    cleaned_text = gpt_call(prompt, model=MODELS["cleaning"], temperature=0, system_message=system_message, memory=None, timeout=60)
    return cleaned_text

def clean_text_with_gpt2(text):
    system_message = "You are a Text Cleaner bot. Your job is to clean and format the given text so that it's easier to read and process. Only respond with the cleaned text, nothing else."
    prompt = f"Please clean the following text:\n'''{text}'''"
    cleaned_text = gpt_call(prompt, model="gpt-3.5-turbo", temperature=0, system_message=system_message, memory=None, timeout=60)
    return cleaned_text

def extract_text_from_pdf(pdf_path,MODELS):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF4.PdfFileReader(pdf_file)
        tokens = []
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text = page.extractText()
            page_tokens = list(tiktoken.encoding_for_model(MODELS["cleaning"]).encode(text))
            tokens.extend([(token, page_num) for token in page_tokens])

    return tokens

def split_into_tokens(tokens, num_tokens, overlap,MODELS):
    for i in range(0, len(tokens), num_tokens - overlap):
        chunk_tokens = tokens[i:i + num_tokens]
        chunk_text = tiktoken.encoding_for_model(MODELS["cleaning"]).decode([token for token, _ in chunk_tokens])
        chunk_pages = list(set(page_num for _, page_num in chunk_tokens))
        yield chunk_text, chunk_pages

def pdf_processing(window_size, overlap, user_objective, MODELS, pdf_dir="PdfInfoGatherer/pdfs", json_dir="PdfInfoGatherer/jsons"):

    pdfs = [file for file in os.listdir(pdf_dir) if file.endswith(".pdf")]
    for pdf in pdfs:
        pdf_path = os.path.join(pdf_dir, pdf)
        tokens = extract_text_from_pdf(pdf_path, MODELS)
    
        print(f"===== {pdf} =====")
        iteration = 0
        for chunk, pages in split_into_tokens(tokens, window_size, overlap, MODELS):

            adjusted_pages = [page + 1 for page in pages]  # adjust page numbers to start at 1 instead of 0

            pdf_name = pdf.split(".")[0]
            pdf_name = re.sub(r'[\\/*?:"<>|]', '_', pdf_name)

            final_dir = os.path.join(json_dir, pdf_name, f"{window_size}_{overlap}")
            base_json_path = os.path.join(final_dir, "base", f"{iteration}.json")

            # Create path if it doesn't exist
            if not os.path.exists(os.path.join(final_dir, "base")):
                os.makedirs(os.path.join(final_dir, "base"))

            if os.path.exists(base_json_path):
                print(f"{base_json_path} already exists")
                with open(base_json_path) as json_file:
                    data = json.load(json_file)
                    prepared_chunk = data['chunk']
            else:
                prepared_chunk = clean_and_translate(chunk, MODELS)

                data = {
                    'pdf': pdf,
                    'chunk': prepared_chunk,
                    'pages': adjusted_pages,
                    'iteration': iteration,
                }

                with open(base_json_path, 'w') as outfile:
                    json.dump(data, outfile)

            prompt, system_message = get_prompt_crawl(prepared_chunk, user_objective)
            answer = gpt_call(prompt, model=MODELS["crawl"], temperature=0, system_message=system_message, memory=None, timeout=60)

            data = {
                'pdf': pdf,
                'chunk': prepared_chunk,
                'pages': adjusted_pages,
                'iteration': iteration,
                'answer': answer,
            }

            # Make directory if it doesn't exist
            if not os.path.exists(os.path.join(final_dir, user_objective[:25])):
                os.makedirs(os.path.join(final_dir, user_objective[:25]))

            with open(os.path.join(final_dir, user_objective[:25], f"{iteration}.json"), 'w') as outfile:
                json.dump(data, outfile)

            iteration += 1
            print("-----")
        
        print(f"PDF: {pdf} has been processed.")
        print("==================")

    print("All PDFs have been processed.")

    return final_dir
