from Prompts import *
from GptCall import gpt_call


def generate_merged_report(reports, user_objective, format, MODELS):
    prompt, system_message = get_prompt_merge_reports(reports, user_objective, format)
    merged_report = gpt_call(
        prompt,
        model=MODELS["reporting"],
        temperature=0,
        system_message=system_message,
        memory=None,
        timeout=220,
    )

    return merged_report


def generate_inital_report(
    answer_set, user_objective, format, pdf_name, language, MODELS
):
    prompt, system_message = get_prompt_report(answer_set, user_objective, format)
    answer = gpt_call(
        prompt,
        model=MODELS["reporting"],
        temperature=0.3,
        system_message=system_message,
        memory=None,
        timeout=180,
    )

    return answer


def generate_refined_report(
    missing_answers, report, user_objective, format, pdf_name, language, MODELS
):
    new_prompt = get_prompt_refine_report(
        missing_answers, report, user_objective, format
    )
    refined_report = gpt_call(
        new_prompt,
        model=MODELS["reporting"],
        temperature=0,
        system_message=False,
        memory=None,
        timeout=180,
    )
    # if language != "en":
    #    refined_report = translate(refined_report, language, MODELS["translation"])

    return refined_report


def translate(text, language, MODELS):
    translation_prompt, system_message = get_prompt_translate(text, language)
    text = gpt_call(
        translation_prompt,
        model=MODELS["translation"],
        temperature=0,
        system_message=system_message,
        memory=None,
        timeout=120,
    )

    return text


def clean_and_translate(text, MODELS):
    prompt, system_message = get_prompt_clean_and_translate(text)
    cleaned_text = gpt_call(
        prompt,
        model=MODELS["cleaning"],
        temperature=0,
        system_message=system_message,
        memory=None,
        timeout=60,
    )
    return cleaned_text


def clean_text_with_gpt2(text):
    system_message = "You are a Text Cleaner bot. Your job is to clean and format the given text so that it's easier to read and process. Only respond with the cleaned text, nothing else."
    prompt = f"Please clean the following text:\n'''{text}'''"
    cleaned_text = gpt_call(
        prompt,
        model="gpt-3.5-turbo",
        temperature=0,
        system_message=system_message,
        memory=None,
        timeout=60,
    )
    return cleaned_text
