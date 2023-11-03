from decouple import config


class Config(object):
    OPENAI_API_KEY = config("OPENAI_API_KEY")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Models
MODELS = {
    "reporting": "gpt-4",
    "refinement_checking": "gpt-3.5-turbo",
    "cleaning": "gpt-3.5-turbo",
    "crawl": "gpt-3.5-turbo",
    "translation": "gpt-3.5-turbo",
}


token_limit = 15000  # token limit for very large files, can stay like this

# Directories
json_dir = "PdfInfoGatherer/jsons"
pdf_dir = "PdfInfoGatherer/pdfs"
