
# ChatGPT Book Generator Application

![Book Generator](https://i.imgur.com/FLyAJ12.png)

## Overview
This is a Python application that uses the OpenAI API to generate a book based on user inputs such as title, author, description, and the number of chapters. The generated content is compiled into a PDF file. The application features a graphical user interface (GUI) built with Tkinter.

## Prerequisites
- Python 3.x
- OpenAI Python client library
- Tkinter
- FPDF
- API key for OpenAI

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/LOR-Studio/ChatGPTBookWriter.git
    cd book-generator
    ```
2. Install the required packages:
    ```sh
    pip install openai fpdf tk
    ```

## Usage
1. Set your OpenAI API key as an environment variable:
    ```sh
    export OPENAI_API_KEY='your-api-key'
    ```
2. Run the application:
    ```sh
    python book_generator.py
    ```
3. Fill in the fields for book title, author name, description, and select the number of chapters and model.
4. Click "Generate Book" to start the content generation process.
5. Monitor progress and output in the console.
6. Once completed, click "Save as PDF" to save the generated book.
