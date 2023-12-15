from decouple import config


class Config(object):
    OPENAI_API_KEY = config("OPENAI_API_KEY")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Model assignments for different tasks
MODELS = {
    "reporting": config("REPORTING"),
    "refinement_checking": config("REFINEMENT_CHECKING"),
    "cleaning": config("CLEANING"),
    "crawl": config("CRAWL"),
    "translation": config("TRANSLATION"),
}


token_limit = config("TOKEN_LIMIT")
timeout_default = config("OPENAI_TIMEOUT")

# Directories
dir_json_base = "PdfInfoGatherer/jsons"
dir_pdf_base = "PdfInfoGatherer/pdfs"
