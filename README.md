# GPT-based Reports

## Overview

This repository contains a Python application designed to extract relevant information from PDF files.

## Scripts

- `main.py`: The entry point of the application. Coordinates the extraction and processing flow.
- `PdfProcessing.py`: Handles PDF reading and text extraction. Also responsible for cleaning and translating text.
- `prompts.py`: Contains predefined prompts used for GPT-3 interaction.
- `GptCall.py`: Manages API calls to the GPT-3 service.
- `config.py`: Contains configurations for development and production environments.

## Requirements

Install the required packages using:

pip install -r requirements.txt


## Quick Start

1. Clone the repository.
2. Navigate to the project directory and run `pip install -r requirements.txt`.
3. Run `python main.py`.

## Configuration

Set the OpenAI API key in a `.env` file as `OPENAI_API_KEY=your-api-key-here`.

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/fooBar`).
3. Commit your changes (`git commit -m 'Add some fooBar'`).
4. Push to the branch (`git push origin feature/fooBar`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the `LICENSE.md` file for details.

