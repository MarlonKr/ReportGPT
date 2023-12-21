from decouple import config


class Config(object):
    OPENAI_API_KEY = config("OPENAI_API_KEY")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Model assignments for different tasks
MODELS = {
    "reporting": "gpt-3.5-turbo-1106",
    "refinement_checking": "gpt-3.5-turbo-1106",
    "cleaning": "gpt-3.5-turbo-1106",
    "crawl": "gpt-3.5-turbo-1106",
    "translation": "gpt-3.5-turbo-1106",
}

token_limit = 15000
timeout_default = 210
# Directories
dir_json_base = "PdfInfoGatherer/jsons"
dir_pdf_base = "PdfInfoGatherer/pdfs"
