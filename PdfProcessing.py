import tiktoken
import os
import json
import fitz
import re

from GptCall import gpt_call
from Prompts import *
from Utilities import ensure_directory_exists, save_to_json
from LLM_functions import clean_and_translate


def create_raw_tokens_from_pdf(pdf_path, MODELS):
    # this function does the following:
    # 1. splits the text into pages
    # 2. encodes the text into tokens
    # 3. adds the page number to each token
    # 4. flattens the list of lists into a single list
    # 5. returns the list of tokens

    with open(pdf_path, "rb") as pdf_file:
        pdf = fitz.open(pdf_file)
        tokens_list = []
        for page in pdf:
            text = page.get_text()
            page = page.number
            page_tokens = list(
                tiktoken.encoding_for_model(MODELS["cleaning"]).encode(text)
            )
            tokens_list.extend([(token, page) for token in page_tokens])

    return tokens_list


def decode_tokens_to_text(tokens, num_tokens, overlap, MODELS):
    """
    Decodes a list of tokens into text chunks using the specified models.

    Args:
        tokens (list): A list of tokens to decode.
        num_tokens (int): = window_size; The number of tokens to include in each chunk.
        overlap (int): The number of overlapping tokens between adjacent chunks.
        MODELS (dict): A dictionary of models to use for decoding.

    Yields:
        tuple: A tuple containing the decoded text chunk and a list of page numbers.

    """
    for i in range(0, len(tokens), num_tokens - overlap):
        chunk_tokens = tokens[i : i + num_tokens]
        chunk_text = tiktoken.encoding_for_model(MODELS["cleaning"]).decode(
            [token for token, _ in chunk_tokens]
        )
        chunk_pages = list(set(page_num for _, page_num in chunk_tokens))
        yield chunk_text, chunk_pages


def pdf_processing(
    window_size,
    overlap,
    user_objective,
    MODELS,
    chunk_prep_method,
    pdf_dir="PdfInfoGatherer/pdfs",
    json_dir="PdfInfoGatherer/jsons",
):
    # create pdf_dir if it doesn't exist
    ensure_directory_exists(pdf_dir)

    pdfs = [file for file in os.listdir(pdf_dir) if file.endswith(".pdf")]
    if not pdfs:
        print(
            "No PDFs found in the pdfs directory. Please add some PDFs and try again."
        )
        exit()

    final_dirs = []

    pdf_names = []

    for pdf in pdfs:
        pdf_path = os.path.join(pdf_dir, pdf)

        # create list of single tokens and their corresponding page numbers
        raw_tokens_list = create_raw_tokens_from_pdf(pdf_path, MODELS)

        pdf_name = re.sub(r'[\\/*?:"<>|]', "_", pdf.split(".")[0])
        pdf_names.append(pdf_name)

        final_dir = os.path.join(json_dir, pdf_name, f"{window_size}_{overlap}")
        final_dirs.append(final_dir)

        print(f"===== {pdf} =====")
        iteration = 0

        # decode tokens into text chunks, according to window_size and overlap
        for chunk_text, pages in decode_tokens_to_text(
            raw_tokens_list, window_size, overlap, MODELS
        ):
            # adjust page numbers to start at 1 instead of 0
            adjusted_pages = [page + 1 for page in pages]

            # Create path if it doesn't exist - final_dir base
            ensure_directory_exists(os.path.join(final_dir, "base"))

            base_json_path = os.path.join(final_dir, "base", f"{iteration}.json")

            if os.path.exists(base_json_path):
                print(f"{base_json_path} already exists")
                with open(base_json_path) as json_file:
                    data = json.load(json_file)
                    prepared_chunk = data["chunk"]
            else:
                if chunk_prep_method == 1:
                    prepared_chunk = clean_and_translate(chunk_text, MODELS)
                else:
                    prepared_chunk = chunk_text

                print(f"Prepared chunk: {prepared_chunk}")

                data = {
                    "pdf": pdf,
                    "chunk": prepared_chunk,
                    "pages": adjusted_pages,
                    "iteration": iteration,
                }

                save_to_json(base_json_path, data)

            prompt, system_message = get_prompt_crawl(prepared_chunk, user_objective)
            answer = gpt_call(
                prompt,
                model=MODELS["crawl"],
                temperature=0,
                system_message=system_message,
                memory=None,
                timeout=25,
            )

            data = {
                "pdf": pdf,
                "chunk": prepared_chunk,
                "pages": adjusted_pages,
                "iteration": iteration,
                "answer": answer,
            }

            # Make directory if it doesn't exist
            ensure_directory_exists(os.path.join(final_dir, user_objective[:25]))

            save_to_json(
                os.path.join(final_dir, user_objective[:25], f"{iteration}.json"), data
            )

            iteration += 1
            print("-----")

        print(f"PDF: {pdf} has been processed.")
        print("==================")

    print("All PDFs have been processed.")

    return final_dirs, pdf_names
