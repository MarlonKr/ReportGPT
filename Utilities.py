import os
import json

from LLM_functions import translate

# Models
MODELS = {
    "reporting": "gpt-4",
    "refinement_checking": "gpt-3.5-turbo",
    "cleaning": "gpt-3.5-turbo",
    "crawl": "gpt-3.5-turbo",
    "translation": "gpt-3.5-turbo",
}


def ensure_directory_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def save_to_json(file_path, data):
    with open(file_path, "w") as outfile:
        json.dump(data, outfile)


def save_report(report, user_objective, format, pdf_name="", suffix=""):
    ensure_directory_exists(f"PdfInfoGatherer/reports")

    with open(
        f"PdfInfoGatherer/reports/{pdf_name}_{format}_{user_objective}{suffix}.txt", "w"
    ) as outfile:
        outfile.write(report)
        print(
            f"PdfInfoGatherer/reports/{pdf_name}_{format}_{user_objective}{suffix}.txt', 'w' has been created"
        )


def handle_user_inputs(MODELS):
    # User-defined inputs
    try:
        window_size = int(
            input("Enter the number of tokens to extract from each PDF: ")
        )
    except ValueError:
        window_size = 250
        print(f"Invalid input. Using default value: {window_size}")

    try:
        overlap = int(input("Enter the number of overlapping tokens between chunks: "))
    except ValueError:
        overlap = 50
        print(f"Invalid input. Using default value: {overlap}")

    user_objective = input("Enter the topic of interest: ")
    format = (
        input("Enter the format you want the report to be in (standard is 'report'): ")
        or "report"
    )
    language = (
        input("Enter the language you want the report to be in (standard is 'en'): ")
        or "en"
    )

    # LLM Translation
    # TODO output "#ENGLISH" rather than repeat the text
    user_objective = translate(user_objective, "english", MODELS)
    if format != "report":
        format = translate(format, "english", MODELS)

    print(f"user_objective: {user_objective}")
    print(f"format: {format}")

    # New user input for choosing the chunk preparation method
    print("Choose the chunk preparation method:")
    print("1. Clean and translate (higher cost, slower)")
    print("2. Use chunk text as is (lower cost, faster)")
    try:
        chunk_prep_method = int(input("Enter your choice (1 or 2): "))
        if chunk_prep_method not in [1, 2]:
            raise ValueError
    except ValueError:
        chunk_prep_method = 1
        print("Invalid input. Defaulting to 'Clean and translate'.")

    return window_size, overlap, user_objective, format, language, chunk_prep_method
