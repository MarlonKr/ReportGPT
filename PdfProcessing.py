import tiktoken
import os
import json
import fitz
import re

from GptCall import gpt_call
from Prompts import *
from Utilities import ensure_directory_exists, save_to_json
from LLM_functions import clean_and_translate


def add_LLM_answer_to_json(json_file_path, user_objective, user_format, MODELS):
    # load json
    with open(json_file_path, "r") as json_file:
        all_chunks_data = json.load(json_file)

    for entry in all_chunks_data:
        if user_objective in entry and entry.get("user_format") == user_format:
            print("user_objective and user_format already in chunk")
            continue

        else:
            # get chunk_text
            chunk_text = entry["chunk"]
            prompt, system_message = get_prompt_crawl(chunk_text, user_objective)
            answer = gpt_call(
                prompt,
                model=MODELS["crawl"],
                temperature=0,
                system_message=system_message,
                memory=None,
                timeout=25,
            )

            entry[user_objective] = answer
            entry["user_format"] = user_format

    with open(json_file_path, "w") as json_file:
        json.dump(all_chunks_data, json_file)


def save_text_and_page_to_json(
    json_file_path,
    raw_tokens_list,
    window_size,
    overlap,
    MODELS,
    pdf,
    chunk_prep_method=1,
):
    iteration = 0

    # decode tokens into text chunks, according to window_size and overlap
    for chunk_text, pages in decode_tokens_to_text(
        raw_tokens_list, window_size, overlap, MODELS
    ):
        # adjust page numbers to start at 1 instead of 0
        adjusted_pages = [page + 1 for page in pages]

        # if json_file_path exists (it's a json file)
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as json_file:
                # load json data into existing_data_to_update, so we can append to it later
                existing_data_to_update = json.load(json_file)
                # check if iteration already exists in json
                if iteration in [
                    entry["iteration"] for entry in existing_data_to_update
                ]:
                    # if yes, skip chunk
                    print(
                        f"{json_file_path} already contains iteration {iteration}. Skipping chunk."
                    )
                    iteration += 1
                    continue
        else:
            existing_data_to_update = []

        if chunk_prep_method == 1:
            chunk_text = clean_and_translate(chunk_text, MODELS)

        data = {
            "pdf": pdf,
            "chunk": chunk_text,
            "pages": adjusted_pages,
            "iteration": iteration,
        }

        # append data to existing_data_to_update, because saving data to json_file_path will overwrite existing data
        existing_data_to_update.append(data)

        # save json in pdf_name_window_size_overlap.json
        save_to_json(
            json_file_path,
            existing_data_to_update,
        )
        iteration += 1


def create_raw_tokens_from_pdf(pdf_path, MODELS):
    """
    This function takes a path to a PDF file and a dictionary of models as input.
    It performs the following steps:
    1. Splits the text into pages
    2. Encodes the text into tokens
    3. Adds the page number to each token
    4. Flattens the list of lists into a single list
    5. Returns the list of tokens

    Args:
        pdf_path (str): The path to the PDF file.
        MODELS (dict): A dictionary of models.

    Returns:
        list: A list of tokens.
    """
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


def process_pdf_to_embedding_jsons(
    window_size,
    overlap,
    user_objective,
    user_format,
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

    json_file_paths = []

    pdf_names = []

    for pdf in pdfs:
        print(f"===== {pdf} =====")

        pdf_path = os.path.join(pdf_dir, pdf)

        # create list of single tokens and their corresponding page numbers
        raw_tokens_list = create_raw_tokens_from_pdf(pdf_path, MODELS)

        pdf_name = re.sub(r'[\\/*?:"<>|]', "_", pdf.split(".")[0])
        pdf_names.append(pdf_name)

        ensure_directory_exists(os.path.join(json_dir))

        json_file_path = os.path.join(
            json_dir, f"{pdf_name}_{window_size}_{overlap}.json"
        )

        save_text_and_page_to_json(
            json_file_path,
            raw_tokens_list,
            window_size,
            overlap,
            MODELS,
            pdf,
            chunk_prep_method,
        )

        add_LLM_answer_to_json(json_file_path, user_objective, user_format, MODELS)

        print(f"PDF: {pdf} has been processed.")
        print("==================")

        # append json_file_path to json_file_paths
        json_file_paths.append(json_file_path)

    print("All PDFs have been processed.")

    return json_file_paths, pdf_names
