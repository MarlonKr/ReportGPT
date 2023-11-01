# GPT-based reports

## Overview

This repository contains a Python application designed to extract relevant information from PDF files.
The main idea is to iterate through chunks of the pdf(s) and "note down", so to say, what's there about the user's query. 

## Features

The process inherits several token-consuming but quality-enhancing approaches:

- Chunk cleaning from PDF artifacts
- Chunk translation into English (for consistency and best LLM performance)
- Report refinement (second iteration that checks for missing information in the final report)
- Reundancy removal (planned)

## User Input

- Chunk size: The size of the token window that iterates through the PDF
- Overlap size: The size of the overlapping tokens which are used to catch otherwise missing context
- Topic of interest: The information that the user is looking for. Can be quite specific. 
- Format: The final format of the output. A 'report' format is default, can be changed to any other output format (e.g. table, bullet points, or even a poem).

## Scripts

- `main.py`: The entry point for the application. Coordinates the extraction and processing flow.
- `PdfProcessing.py`: Handles PDF text extraction, cleaning, translation, as well as dumping and organizing the data into .json files.
- `prompts.py`: Holds the prompts used for LLM interaction.
- `GptCall.py`: Manages API calls to OpenAI
- `config.py`: Contains configurations for development and production environments.

## Ideas and TODO's
- [ ] Implement redundancy check for crawling and refining processes
- [ ] Allow multiple PDF reports to be merged into a single report
- [ ] Incorporate missed answers iteratively 
- [ ] Translate user input (if not in English)
- [ ] Report output translation (if needed)


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

