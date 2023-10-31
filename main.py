import os
import tiktoken
import openai 
import json 
from decouple import config

from GptCall import gpt_call
from prompts import *
from PdfProcessing import pdf_processing


openai.api_key = config('OPENAI_API_KEY')

def save_report(answer, user_objective):
    if not os.path.exists("PdfInfoGatherer/reports"):
        os.makedirs("PdfInfoGatherer/reports")
    with open(f'PdfInfoGatherer/reports/report_{user_objective}.txt', 'w') as outfile:
        outfile.write(answer)
        print(f"PdfInfoGatherer/reports/report_{user_objective}.txt has been created")

def chunk_in_token_limit_lists(answer_list, tokenizer, token_limit):
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

def refine_report(answer, answer_lists, user_objective, MODELS):

    report = answer

    # List to store missing answers
    missing_answers = []

    # String to store formatted missing answers
    missing_answer_list = ""

    # Self-supervising by comparing answer_lists to report
    for answer_list in answer_lists:
        for answer_dict in answer_list:
            answer = answer_dict['answer']
            prompt, system_message = get_prompt_self_supervising(answer, report)
            check_result = gpt_call(prompt, model=MODELS["refinement"], temperature=0, system_message=system_message, memory=None, timeout=80)
            
            if  "0" in check_result.lower(): 
                print("-----")
                print(f"Answer missing in report:\n\n {answer}")
                print("-----")

                missing_answers.append(answer_dict)
                pages = ", ".join(map(str, answer_dict['pages']))
                pdf = answer_dict['pdf']
                missing_answer_list += f"- {answer} (Pages: {pages}, PDF: {pdf})\n"

    # If there are missing answers, refine the report
    if missing_answers:
        print("refining report...")
        # Generate a new prompt with missing answers and call ChatGPT to refine the report
        new_prompt = get_prompt_refine_report(missing_answer_list, report, user_objective)
        refined_report = gpt_call(new_prompt, model=MODELS["refinement"], temperature=0, system_message=system_message, memory=None, timeout=120)
        
        report = refined_report

    # Save the final report
    with open(f'PdfInfoGatherer/reports/report_{user_objective}.txt', 'w') as outfile:
        outfile.write(report)
        print(f"PdfInfoGatherer/reports/report_{user_objective}.txt has been updated")

    print("All done.")

def create_answer_list_and_clean_jsons(json_dir):
    answer_list = []

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

# User-defined inputs
window_size = int(input("Enter the number of tokens to extract from each PDF: "))
overlap = int(input("Enter the number of overlapping tokens between chunks: "))
user_objective = input("Enter the topic of interest: ")
format = input("Enter the format you want the report to be in (standard is 'report'): ") if input("Enter the format you want the report to be in (standard is 'report'): ") else "report"

# Models
MODELS = {
    "report_initial": "gpt-3.5-turbo-16k",
    "refinement": "gpt-3.5-turbo-16k",
    "cleaning": "gpt-3.5-turbo",
    "crawl": "gpt-3.5-turbo",
}

tokenizer_crawl = tiktoken.encoding_for_model(MODELS["crawl"])
token_limit = 15000 # token limit for very large files, can stay like this

# Iterate through PDFs and process content; create jsons with answers
json_dir = pdf_processing(window_size, overlap, user_objective, MODELS)

proceed = input("Do you want to proceed? (y/n): ")
if proceed == "n":
    print("All done.")
    exit()
else:
    # create answer_list by removing jsons with "not relevant" in the answer, thus irrelevant answers
    answer_list = create_answer_list_and_clean_jsons(json_dir)

# check token count of answer_list and split into multiple answer_lists if token count is too high for model token limit
answer_lists = chunk_in_token_limit_lists(answer_list, tokenizer_crawl, token_limit)

# TODO for all lists in answer_lists: create report, then combine all reports into one report
prompt, system_message = get_prompt_report(answer_lists, user_objective,format)
answer = gpt_call(prompt, model=MODELS["report_initial"], temperature=0.3, system_message=system_message, memory=None, timeout=300)

print(f"Report: \n###\n {answer} \n###n")

save_report(answer, user_objective)

proceed = input("Do you want to look for missing answers and refine the report? (y/n): ")

if proceed == "n":
    print("All done.")
elif proceed == "y":
    refine_report(answer, answer_lists, user_objective, MODELS)
    print("All done.")
else:
    print("Invalid input. All done.")

# TODO Implement a redundancy check for crawling and refining