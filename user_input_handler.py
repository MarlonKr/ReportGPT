from LLM_functions import translate


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
