def get_prompt_crawl(chunk, user_objective):
    system_message = """You are a helpful Information Extractor chatbot. Your job is to extract information from PDF snippets that might be relevant to the client's interest. 

Please review the PDF snippets and report back any somehow relevant sections that the client is looking for. 

Don't introduce your answer, just answer straight away.

Make sure to add an appropriate amount of context for coherence.

Use bullet point(s) to structure your answer."""

    fewshot_crawl_date_user = """'''PDF SNIPPET
The first moon landing occurred on July 20, 1969, marking a significant milestone in space exploration. It was an achievement people never forgot. |2014 DOCUMENTATION OF IMPORTANT HISTORY| PAGE 4 The Berlin Wall fell on November 9, 1989, leading to the end of the Cold War.
'''

client is looking for: 'Dates'. What does the PDF snippet tell you about this?
"""

    fewshot_crawl_date_assistant = """- July 20, 1969: First moon landing, significant milestone in space exploration
- November 9, 1989, Berlin Wall fell, leading to the end of the Cold War"""

    fewshot_crawl_warranty_user = """'''PDF SNIPPET
For customer support, please call our hotline. The warranty period for this product is 12 months from the date of purchase. Battery not included. Consumer is responsible for shipping costs. |WARRANTY| PAGE 2
'''

client is looking for: 'What is the warranty period for the product?'. What does the PDF snippet tell you about this?

"""
    fewshot_crawl_date_waranty_assistant = (
        """- Warranty is 12 months from the date of purchase"""
    )

    fewshot_crawl_notrelevant1_user = """'''PDF SNIPPET
We were recognized as the most innovative company last year. Our environmental initiatives have been widely applauded.
'''

client is looking for: 'Revenue in the last fiscal year'. What does the PDF snippet tell you about this?
"""

    fewshot_crawl_notrelevant1_assistant = """Not relevant"""

    fewshot_crawl_notrelevant2_user = """'''PDF SNIPPET
    The city was bustling with activity, and the tall buildings touched the sky. The weather was gloomy.
'''

client is looking for: 'Main Character traits'. What does the PDF snippet tell you about this?

"""

    fewshot_crawl_notrelevant2_assistant = """Not relevant"""

    fewshot_crawl_statistics_user = """'''PDF SNIPPET
The study showed that 80% of participants improved their sleep quality. This was a huge sucess for us. NEXT PAGE - STUDY OF SLEEP In contrast, the control group showed no significant changes. Our lab equipment was sourced from various vendors.
'''

client is looking for: 'statistics'. What does the PDF snippet tell you about this?
"""

    fewshot_crawl_statistics_assistant = """- 80% of participants improved their sleep quality
- control group showed no significant changes in sleep quality"""

    fewshot_crawl_crimeratenumbers_user = """'''PDF SNIPPET
Last year, violence in the city increased by 10%. The mayor is planning new community programs. The unemployment rate is at 5%.
'''

client is looking for: 'crime rate numbers'. What does the PDF snippet tell you about this?
"""

    fewshot_crawl_crimeratenumbers_assistant = (
        """- violence in the city increased by 10% in the last year"""
    )

    call = f"""'''PDF SNIPPET
{chunk}
'''

client is looking for: '{user_objective}'. What does the PDF snippet tell you about this?
"""

    messages = [
        {"role": "user", "content": fewshot_crawl_date_user},
        {"role": "assistant", "content": fewshot_crawl_date_assistant},
        {"role": "user", "content": fewshot_crawl_notrelevant1_user},
        {"role": "assistant", "content": fewshot_crawl_notrelevant1_assistant},
        {"role": "user", "content": fewshot_crawl_statistics_user},
        {"role": "assistant", "content": fewshot_crawl_statistics_assistant},
        {"role": "user", "content": fewshot_crawl_crimeratenumbers_user},
        {"role": "assistant", "content": fewshot_crawl_crimeratenumbers_assistant},
        {"role": "user", "content": fewshot_crawl_notrelevant2_user},
        {"role": "assistant", "content": fewshot_crawl_notrelevant2_assistant},
        {"role": "user", "content": fewshot_crawl_warranty_user},
        {"role": "assistant", "content": fewshot_crawl_date_waranty_assistant},
    ]

    # append the call to the messages
    messages.append({"role": "user", "content": call})

    return messages, system_message


def get_prompt_self_supervising(answer, report, format):
    system_message = f"You are a Supervising Assistant. Your job is to check whether a certain information is present in the {format}. Your objective is to output a number (#TRUE or #FALSE) that indicates whether the information is sufficently present in the {format} (#TRUE) or not (#FALSE)."

    prompt = f"""Is the following information sufficently present in the {format}?

Information to check:
'''
{answer}
'''

{format}:
'''
{report}
'''

Take a deep breath and work on this question step-by-step. Afterwards, conclude by either writing a '#TRUE' (= "{format} contains sufficient amount of the information") or '#FALSE' (= "significant information is missing in {format}, revision necessary").

Example: [Your reasoning about whether the answer is present in the {format} or not.], therefore significant information is missing in {format}, revision necessary. I answer with #FALSE.
Mind the hashtag before the TRUE or FALSE.
"""
    return prompt, system_message


def get_prompt_report(answer_set, user_objective, format):
    system_message = f"You are a {format} creator assistant. Your job is to create a {format} using the extracted information from PDFs to a given query. The query might be a question, a keyword, a topic of interest, a certain type of information type or something else. If you are not sure about an information, rather add it to the {format} than not. Don't do smalltalk nor introduce your answer, just answer with the final {format}. The {format} should be structured, readable, throughout and extensive."

    answer_list = ""
    for answer_dict in answer_set:
        answer = answer_dict["answer"]
        pages = ", ".join(map(str, answer_dict["pages"]))
        pdf = answer_dict["pdf"]
        answer_list += f"- {answer} (Pages: {pages}, PDF: {pdf})\n"
    answer_list += "\n"

    prompt = f"""Hello {format} creator assistant, it's nice to have you.
What now follows is information that has been extracted from PDFs to the query: {user_objective}
Cite the respective pages to each of the extracted information. If only one pdf is being mentioned, also cite the pdf only once.
Please be as precise, accurate and throughout as possible or else I will get punished for your mistakes by my boss.


Extracted information:
'''
{answer_list}
'''

Use this extracted information and bring it into a readable and structured {format}. Pleaes make sure to don't forget any information, because I will get punished for your mistakes by my boss.
"""

    return prompt, system_message


def get_prompt_refine_report(missing_answer_list, report, user_objective, format):
    prompt = f"""Hello {format} creator assistant, it seems some information was missing in the initial {format} related to the user's interest of: {user_objective}.
Please refine the existing {format} by integrating the following missing information into it so we have a complete {format}:

Potentially missing information:
'''
{missing_answer_list}
'''

{format}:
{report}

When incorporating be as precise, accurate and throughout as possible, or I will be punished by my boss for your mistakes. 

Only reply with the refined {format}, nothing else.
"""
    return prompt


def get_prompt_clean_and_translate(text):
    system_message = "You are a Clean and Translate Assistant. Your job is to clean and format the given text so that it is easier to read and process, and to translate it into English if it isn't already (in this case, ignore the translation task). Respond only with the cleaned and translated text, nothing else"

    prompt = f"Please clean and translate the following text into English if it's written in another language:\n'''{text}'''' \nOnly reply with the cleaned and translated text, nothing else"

    return prompt, system_message


def get_prompt_merge_reports(reports_list, user_objective, format):
    system_message = f"You are a {format} creator assistant. Your job is to merge the given {format}(s) into a single one."

    reports = ""
    for report in reports_list:
        reports += f"'''{report}'''\n\n"

    prompt = f"""Hello {format} creator assistant, it's nice to have you. 
What now follows are the {format}(s) that have been created by different {format} creator assistants to the topic of {user_objective}.
Please merge them into one {format}.

{format}(s):
{reports}

Please, use these {format}s and bring them into a single readable, coherent and structured {format}. Pleaes make sure to don't forget any information, because I will get punished for your mistakes by my boss.
"""

    return prompt, system_message


def get_prompt_translate(user_input, language):
    system_message = f"You are a Translate Assistant. Your job is to translate the given text into {language} if it isn't already (in this case, ignore the translation task and just repeat the text). Respond only with the translated text, nothing else"

    prompt = f"Please translate the following text into {language} if it's written in another language:\n\n'''{user_input}'''\n\nOnly reply with the translated text, nothing else. If the text is already in {language}, just repeat the text."

    return prompt, system_message
