import os
import tiktoken
import openai
import json
from decouple import config

from GptCall import gpt_call
from Prompts import *
from PdfProcessing import process_pdf_to_embedding_jsons
from Utilities import ensure_directory_exists, save_report
from LLM_functions import *
from user_input_handler import handle_user_inputs
from config import MODELS, token_limit, dir_json_base, dir_pdf_base

openai.api_key = config("OPENAI_API_KEY")


def get_relevant_answers_from_json(json_file):
    relevant_answers = []
    with open(json_file) as json_file:
        all_json_answers = json.load(json_file)
        for entry in all_json_answers:
            if entry[user_objective].lower() != "not relevant":
                # append answer, pages and pdf to relevant_answers
                relevant_answers.append(
                    {
                        "answer": entry[user_objective],
                        "pages": entry["pages"],
                        "pdf": entry["pdf"],
                    }
                )
    return relevant_answers


def chunk_in_token_limit_lists(answer_list, token_limit, MODELS):
    # Tokenizer initialization
    tokenizer = tiktoken.encoding_for_model(MODELS["crawl"])

    # count tokens of answer_list
    token_count = 0
    for answer_dict in answer_list:
        token_count += len(tokenizer.encode(answer_dict["answer"]))

    print(f"token_count: {token_count}")

    if (
        token_count > token_limit
    ):  # split answer_list into multiple answer_lists with a token_count of token_limit
        print("token_count > token_limit")
        answer_lists = []
        token_count = 0
        for answer in answer_list:
            if token_count + len(tokenizer.encode(answer)) < token_limit:
                answer_list.append(answer)
                token_count += len(tokenizer.encode(answer))
            else:
                answer_lists.append(answer_list)
                answer_list = []
                token_count = 0

    else:  # just one answer_list since token_count below token_limit
        print("token_count < token_limit")
        answer_lists = [answer_list]

    return answer_lists


def check_missing_answers(answer_lists, report, format, MODELS):
    missing_answers = ""

    for answer_list in answer_lists:
        for answer_dict in answer_list:
            answer = answer_dict["answer"]
            prompt, system_message = get_prompt_self_supervising(answer, report, format)
            check_result = gpt_call(
                prompt,
                model=MODELS["refinement_checking"],
                temperature=0,
                system_message=system_message,
                memory=None,
                timeout=80,
            )

            if "#FALSE" in check_result:
                pages = ", ".join(map(str, answer_dict["pages"]))
                pdf = answer_dict["pdf"]
                missing_answers += f"- {answer} (Pages: {pages}, PDF: {pdf})\n"

    print(f"missing_answers:\n\n {missing_answers}")
    return missing_answers


def create_answer_list_and_clean_jsons(json_dir, user_objective):
    answer_list = []

    # iterate through jsons

    for file in os.listdir(json_dir + f"/{user_objective[:25]}"):
        if file.endswith(".json"):
            with open(json_dir + f"/{user_objective[:25]}/{file}") as json_file:
                data = json.load(json_file)
                if "not relevant" in data["answer"].lower():
                    os.remove(json_dir + f"/{user_objective[:25]}/{file}")
                    print(f"{file} has been deleted")
                else:
                    print(f"{file} has been kept")
                    answer_list.append(
                        {
                            "answer": data["answer"],
                            "pages": data["pages"],
                            "pdf": data["pdf"],
                        }
                    )

    print("Proceeding...")
    return answer_list


(
    window_size,
    overlap,
    user_objective,
    user_format,
    language,
    chunk_prep_method,
) = handle_user_inputs(MODELS)


# Iterate through PDFs and process content; create jsons with answers
json_file_paths, pdf_names = process_pdf_to_embedding_jsons(
    window_size,
    overlap,
    user_objective,
    user_format,
    MODELS,
    chunk_prep_method,
    pdf_dir=dir_pdf_base,
    json_dir=dir_json_base,
)

"""proceed = input("Do you want to proceed? (y/n): ")
proceed = "y"
if proceed == "n":
    print("All done.")
    exit()"""

reports_list = []
for json_file, pdf_name in zip(json_file_paths, pdf_names):
    # get answers from json_file that are not "not relevant"
    relevant_answers = get_relevant_answers_from_json(json_file)

    # check token count of answer_list and split into multiple answer_lists if token count is too high for model token limit
    answer_lists = chunk_in_token_limit_lists(relevant_answers, token_limit, MODELS)

    if len(answer_lists) > 1:
        # if token count was above token limit, iterate through answer_lists and generate a report for each answer_list
        temp_reports = []
        for answer_set in answer_lists:
            if not answer_set:  # Skip empty answer_set
                print("Skipping empty answer_set...")
                continue
            temp_report = generate_inital_report(
                answer_set, user_objective, user_format, pdf_name, MODELS
            )
            temp_reports.append(temp_report)

        report = generate_merged_report(
            temp_reports, user_objective, user_format, MODELS
        )
        save_report(report, user_objective, user_format, pdf_name, suffix="")

    else:
        # if token count was below token limit, generate a report for the answer_list
        if answer_lists[0]:  # Only proceed if not empty
            report = generate_inital_report(
                answer_lists[0], user_objective, user_format, pdf_name, language, MODELS
            )
            save_report(report, user_objective, user_format, pdf_name, suffix="")

        else:
            continue

    proceed = input(
        "Do you want to look for missing answers and refine the report? (y/n): "
    )
    # proceed  = "y"
    if proceed == "n":
        print("done.")

    elif proceed == "y":
        missing_answers = check_missing_answers(
            answer_lists, report, user_format, MODELS
        )
        if missing_answers != "":
            report = generate_refined_report(
                missing_answers,
                report,
                user_objective,
                user_format,
                pdf_name,
                language,
                MODELS,
            )
            save_report(
                report, user_objective, user_format, pdf_name, suffix="_refined"
            )

        else:
            print("No missing answers found. No need to refine the report.")

        print("done.")
    else:
        print("Invalid input.")

    reports_list.append(report)


if len(reports_list) > 1:
    merge = input("Do you want to merge all reports into one report? (y/n): ")
    if merge == "y":
        print("Merging reports...")
        merged_report = generate_merged_report(
            reports_list, user_objective, user_format, MODELS
        )
        reports_list.append(merged_report)
        # make pdf_names a string, but cut each pdf_name to 10 characters and split via underscore
        pdf_names = "_".join([pdf_name[:10] for pdf_name in pdf_names])
        save_report(
            merged_report, user_objective, user_format, pdf_names, suffix="_merged"
        )

    else:
        print("Not merging reports. Proceeding...")

# iterate through reports_list and translate each report if language != "en"
if language != "en":
    translated_reports_list = []
    i = 0
    for report in reports_list:
        i += 1
        translated_report = translate(report, language, MODELS)

        # TODO collect the names of the reports and add them to this function
        save_report(
            translated_report,
            user_objective,
            user_format,
            "",
            suffix=f"_translated_{i}",
        )
        translated_reports_list.append(translated_report)

    reports_list = translated_reports_list
