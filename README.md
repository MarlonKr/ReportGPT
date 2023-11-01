# GPT-based Reports

## Overview

This repository contains a Python application designed to extract relevant information from PDF files.

## Scripts

- `main.py`: The entry point of the application. Coordinates the extraction and processing flow.
- `PdfProcessing.py`: Handles PDF text extraction, cleaning, translating, as well as dumping and organizing the data into .json files.
- `prompts.py`: Contains prompts used for LLM interaction.
- `GptCall.py`: Manages API calls to OpenAI
- `config.py`: Contains configurations for development and production environments.

## Ideas and TODO's
- [ ] Implement a redundancy check for crawling- and refining-processes
- [ ] Option to merge multiple pdf reports into one report
- [ ] Incorporate missed answers iteratively 


## Requirements

Install the required packages using:

pip install -r requirements.txt


## Quick Start

1. Clone the repository.
2. Navigate to the project directory and run `pip install -r requirements.txt`.
3. Set the OpenAI API key in a `.env` file as `OPENAI_API_KEY=your-api-key-here`.
4. place a single or multiple .pdf file(s) into the "PdfInfoGatherer" directory.
3. Run `python main.py`.


## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/fooBar`).
3. Commit your changes (`git commit -m 'Add some fooBar'`).
4. Push to the branch (`git push origin feature/fooBar`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the `LICENSE.md` file for details.

