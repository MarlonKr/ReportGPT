import os
import tiktoken
import openai 
import json 
from decouple import config

from GptCall import gpt_call
from Prompts import *
from PdfProcessing import pdf_processing
from Utilities import *
from LLM_functions import * 

openai.api_key = config('OPENAI_API_KEY')


def chunk_in_token_limit_lists(answer_list, token_limit, MODELS):
    # Tokenizer initialization
    tokenizer = tiktoken.encoding_for_model(MODELS["crawl"])  

    # count tokens of answer_list
    token_count = 0
    for answer_dict in answer_list:
        token_count += len(tokenizer.encode(answer_dict['answer']))
        
    print(f"token_count: {token_count}")
    
    if token_count > token_limit: # split answer_list into multiple answer_lists with a token_count of token_limit
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
        print(f"answer_lists: {answer_lists}")
 
    else: # just one answer_list since token_count below token_limit
        print("token_count < token_limit")
        answer_lists = [answer_list]
        print(f"answer_lists: {answer_lists}")

    return answer_lists

def check_missing_answers(answer_lists, report, format, MODELS):
    missing_answers = ""
    
    for answer_list in answer_lists:
        for answer_dict in answer_list:
            answer = answer_dict['answer']
            prompt, system_message = get_prompt_self_supervising(answer, report, format)
            check_result = gpt_call(prompt, model=MODELS["refinement"], temperature=0, system_message=system_message, memory=None, timeout=80)
            
            if "#FALSE" in check_result:
                pages = ", ".join(map(str, answer_dict['pages']))
                pdf = answer_dict['pdf']
                missing_answers += f"- {answer} (Pages: {pages}, PDF: {pdf})\n"
                
    print(f"missing_answers:\n\n {missing_answers}")
    return missing_answers

def create_answer_list_and_clean_jsons(json_dir, user_objective):
    answer_list = []

    # mkdir if not exists
    ensure_directory_exists(json_dir+f"/{user_objective[:25]}")

    for file in os.listdir(json_dir+f"/{user_objective[:25]}"):
        if file.endswith(".json"):
            with open(json_dir+f"/{user_objective[:25]}/{file}") as json_file:
                data = json.load(json_file)
                if "not relevant" in data['answer'].lower():
                    os.remove(json_dir+f"/{user_objective[:25]}/{file}")
                    print(f"{file} has been deleted")
                else:
                    print(f"{file} has been kept")
                    answer_list.append({
                        'answer': data['answer'],
                        'pages': data['pages'],
                        'pdf': data['pdf']
                    })

    print("Proceeding...")
    return answer_list

def handle_user_inputs(MODELS):
        # User-defined inputs
    try:
        window_size = int(input("Enter the number of tokens to extract from each PDF: "))
    except ValueError:
        window_size = 250
        print(f"Invalid input. Using default value: {window_size}")

    try:
        overlap = int(input("Enter the number of overlapping tokens between chunks: "))
    except ValueError:
        overlap = 50
        print(f"Invalid input. Using default value: {overlap}")

    user_objective = input("Enter the topic of interest: ")
    format = input("Enter the format you want the report to be in (standard is 'report'): ") or "report"
    language = input("Enter the language you want the report to be in (standard is 'en'): ") or "en"

    # LLM Translation
    user_objective = translate(user_objective, "english", MODELS)
    if format != "report":
        format = translate(format, "english", MODELS)

    print(f"user_objective: {user_objective}")
    print(f"format: {format}")

    return window_size, overlap, user_objective, format, language


# Models
MODELS = {
    "reporting": "gpt-3.5-turbo-16k",
    "refinement": "gpt-3.5-turbo-16k",
    "cleaning": "gpt-3.5-turbo",
    "crawl": "gpt-3.5-turbo",
    "translation": "gpt-3.5-turbo",
}

window_size, overlap, user_objective, format, language = handle_user_inputs(MODELS)



token_limit = 15000 # token limit for very large files, can stay like this

# Directories
json_dir = "PdfInfoGatherer/jsons"
pdf_dir = "PdfInfoGatherer/pdfs"

# Iterate through PDFs and process content; create jsons with answers
final_dirs, pdf_names = pdf_processing(window_size, overlap, user_objective, MODELS, pdf_dir=pdf_dir, json_dir=json_dir)

"""proceed = input("Do you want to proceed? (y/n): ")
proceed = "y"
if proceed == "n":
    print("All done.")
    exit()"""

reports_list = []
for final_dir, pdf_name in zip(final_dirs, pdf_names):
    answer_list = create_answer_list_and_clean_jsons(final_dir, user_objective)

    # check token count of answer_list and split into multiple answer_lists if token count is too high for model token limit
    answer_lists = chunk_in_token_limit_lists(answer_list, token_limit, MODELS)

    if len(answer_lists) > 1:
        temp_reports = []
        for answer_set in answer_lists:
            if not answer_set:  # Skip empty answer_set
                print("Skipping empty answer_set...")
                continue
            temp_report = generate_inital_report(answer_set, user_objective, format, pdf_name, MODELS)
            temp_reports.append(temp_report)
        
        report = generate_merged_report(temp_reports, user_objective, format, MODELS)
        save_report(report, user_objective, format, pdf_name, suffix="")

    else:
        if answer_lists[0]:  # Only proceed if not empty
            report = generate_inital_report(answer_lists[0], user_objective, format, pdf_name, language, MODELS)
            save_report(report, user_objective, format, pdf_name, suffix="")

        else:
            continue 
    
    # append initial_report to reports_list
            
    proceed = input("Do you want to look for missing answers and refine the report? (y/n): ")
    #proceed  = "y"
    if proceed == "n":
        print("done.")

    elif proceed == "y":
        missing_answers = check_missing_answers(answer_lists, report, format, MODELS)
        if missing_answers != "": 
            report = generate_refined_report(missing_answers, report, user_objective, format, pdf_name, language, MODELS)
            save_report(report, user_objective, format, pdf_name, suffix="_refined")

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
        merged_report = generate_merged_report(reports_list, user_objective, format, MODELS)
        reports_list.append(merged_report)
        # make pdf_names a string, but cut each pdf_name to 10 characters and split via underscore
        pdf_names = "_".join([pdf_name[:10] for pdf_name in pdf_names])
        save_report(merged_report, user_objective, format, pdf_names, suffix="_merged")
    
    else:
        print("Not merging reports. Proceeding...")
    
# iterate through reports_list and translate each report if language != "en"
if language != "en":
    translated_reports_list = []
    i = 0
    for report in reports_list:
        i+=1
        translated_report = translate(report, language, MODELS)
        
        #TODO collect the names of the reports and add them to this function
        save_report(translated_report, user_objective, format, "", suffix=f"_translated_{i}")
        translated_reports_list.append(translated_report)
    
    reports_list = translated_reports_list

