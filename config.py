from decouple import config


class Config(object):
    OPENAI_API_KEY = config("OPENAI_API_KEY")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Models
MODELS = {
    "reporting": "gpt-4-1106-preview",
    "refinement_checking": "gpt-3.5-turbo-1106",
    "cleaning": "gpt-3.5-turbo-1106",
    "crawl": "gpt-3.5-turbo-1106",
    "translation": "gpt-3.5-turbo-1106",
}


token_limit = 15000  # token limit for very large files, can stay like this

# Directories
dir_json_base = "PdfInfoGatherer/jsons"
dir_pdf_base = "PdfInfoGatherer/pdfs"
