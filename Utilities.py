import os
import json

from LLM_functions import translate


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
