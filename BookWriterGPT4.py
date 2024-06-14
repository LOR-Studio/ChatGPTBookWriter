import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from openai import OpenAI
import os
from fpdf import FPDF
import time
import webbrowser
pdf = None

# Instantiate the OpenAI client
client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY')
)

def generate_content(prompt, model, retries=5, backoff_factor=5):
    """Generate content using OpenAI API with retry mechanism."""
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            console.insert(tk.END, f"Error generating content: {e}\n")
            if attempt < retries - 1:
                wait_time = backoff_factor ** attempt
                console.insert(tk.END, f"Retrying in {wait_time} seconds...\n")
                time.sleep(wait_time)
            else:
                console.insert(tk.END, "Max retries reached. Skipping content generation.\n")
                return ""

class PDF(FPDF):
    def __init__(self, title='Your Title Here', author='Author Name', font_family='Times', header_font_size=12, body_font_size=12):
        super().__init__()
        self.title = title
        self.author = author
        self.font_family = font_family
        self.header_font_size = header_font_size
        self.body_font_size = body_font_size
        self.chapter_title = ''
        self.chapter_number = 0  # Initialize chapter number
        self.add_page()
        self.set_font(self.font_family, 'B', 16)
        self.cell(0, 10, self.title, 0, 1, 'C')
        self.set_font(self.font_family, 'I', 12)
        self.cell(0, 10, self.author, 0, 1, 'C')
        # Add metadata to the PDF
        self.set_creator('Book Generator')
        self.set_author(self.author)
        self.set_title(self.title)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_family, 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def set_chapter_title(self, chapter_number, chapter_title):
        self.chapter_number = chapter_number
        if self.chapter_title != chapter_title:
            self.chapter_title = chapter_title
            if self.page_no() > 1:
                self.add_page()
            self.set_font(self.font_family, 'B', 14)

    def chapter_body(self, body, align='L'):
        body = self.replace_incompatible_characters(body)
        body = self.remove_large_blank_spaces(body)  # Post-processing to remove large blank spaces
        self.set_font(self.font_family, '', self.body_font_size)
        self.multi_cell(0, 10, body, 0, align)
        self.ln()

    def replace_incompatible_characters(self, text):
        replacements = {
            '\u2013': '-',  # en dash
            '\u2014': '-',  # em dash
            '\u2018': "'",  # left single quotation mark
            '\u2019': "'",  # right single quotation mark
            '\u201C': '"',  # left double quotation mark
            '\u201D': '"',  # right double quotation mark
            '\u2022': '*',  # bullet
            '\u2026': '...',  # ellipsis
            '\u00A0': ' ',  # non-breaking space
            # Add more replacements as needed
        }
        for original, replacement in replacements.items():
            text = text.replace(original, replacement)
        return text

    def remove_large_blank_spaces(self, text):
        """Remove large portions of blank space in the text."""
        import re
        text = re.sub(r'\n{3,}', '\n\n', text)  # Replace three or more newlines with two newlines
        return text

def is_chapter_logical(chapter_title, chapter_content, rolling_context):
    # Check if the chapter title is relevant to the story
    if "irrelevant" in chapter_title.lower():
        return False
    # Check if the chapter content is consistent with the rolling context
    if "inconsistent" in chapter_content.lower():
        return False
    # Check if the chapter content introduces sudden changes without explanation
    if "sudden change" in chapter_content.lower():
        return False
    # Add more checks as needed...
    return True

def check_originality(chapters):
    # Placeholder function for originality check
    # In a real implementation, you would use an API like OpenAI's Originality or another plagiarism detection tool

    # Check for repeated phrases or sentences within the story
    all_sentences = []
    for chapter in chapters:
        sentences = chapter.split('.')
        all_sentences.extend(sentences)

    unique_sentences = set(all_sentences)
    if len(unique_sentences) < len(all_sentences) * 0.9:  # Allow up to 10% repetition
        console.insert(tk.END, "Originality check: Failed due to excessive repetition within the story.\n")
        return False

    # Check for clichés or overused expressions (this is a basic example, you can expand this list)
    cliches = ["once upon a time", "happily ever after", "in the nick of time", "dead as a doornail"]
    for sentence in all_sentences:
        for cliche in cliches:
            if cliche in sentence.lower():
                console.insert(tk.END, f"Originality check: Failed due to the use of clichés (e.g., '{cliche}').\n")
                return False

    # Check for diversity in character names and settings (simple example)
    character_names = ["John", "Mary", "Bob", "Alice"]  # Example list, should be based on your story
    setting_keywords = ["castle", "forest", "city", "village"]  # Example list, should be based on your story
    if any(name.lower() in ' '.join(chapters).lower() for name in character_names):
        console.insert(tk.END, "Originality check: Failed due to common character names.\n")
        return False
    if any(keyword.lower() in ' '.join(chapters).lower() for keyword in setting_keywords):
        console.insert(tk.END, "Originality check: Failed due to common setting keywords.\n")
        return False

    # If all checks pass
    console.insert(tk.END, "Originality check: Passed. The story appears to be original.\n")
    return True

def save_as_pdf():
    global pdf
    global book_title
    save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if save_path:
        try:
            pdf.output(save_path)
            console.insert(tk.END, f"Book '{book_title}' saved successfully as PDF.\n")
        except Exception as e:
            console.insert(tk.END, f"Error saving PDF: {e}\n")

def generate_book():
    global pdf
    global book_title
    console.delete('1.0', tk.END)  # Clear the console
    book_title = title_entry.get()
    author = author_entry.get()
    description = description_text.get("1.0", tk.END).strip()
    num_chapters = int(chapters_combobox.get())
    model = model_combobox.get()  # Get the selected model
    rolling_context = description
    pdf = PDF(title=book_title, author=author)
    generated_chapters = []
    progress_bar['value'] = 0
    progress_bar['maximum'] = num_chapters
    for chapter_num in range(1, num_chapters + 1):
        chapter_generated = False
        while not chapter_generated:
            try:
                # Generate chapter title
                if chapter_num == 1:
                    chapter_title_prompt = f"<context>{rolling_context}</context> <prompt>Generate a title for the first chapter of a book titled '{book_title}' by {author}. The chapter should introduce the main character and the unique setting.</prompt>"
                elif chapter_num == num_chapters:
                    chapter_title_prompt = f"<context>{rolling_context}</context> <prompt>Generate a title for the concluding chapter of a book titled '{book_title}' by {author}. The chapter should wrap up the story and provide a satisfying conclusion.</prompt>"
                else:
                    chapter_title_prompt = f"<context>{rolling_context}</context> <prompt>Generate a title for Chapter {chapter_num} of a book titled '{book_title}' by {author}. The chapter should continue the story, adding depth to characters and plot.</prompt>"
                chapter_title = generate_content(chapter_title_prompt, model).strip()
                # Generate chapter content
                if chapter_num == 1:
                    chapter_content_prompt = f"<context>{rolling_context}</context> <prompt>Write the first chapter of the book '{book_title}' titled '{chapter_title}'. Introduce the main character and the unique setting of the story. Begin the chapter with an intriguing event that sets the tone for the adventure. Highlight the emotional impact and vivid descriptions to captivate the reader.</prompt>"
                elif chapter_num == num_chapters:
                    chapter_content_prompt = f"<context>{rolling_context}</context> <prompt>Write the final chapter of the book '{book_title}' titled '{chapter_title}'. Bring the story to a satisfying conclusion, resolving the main conflict and reflecting on the journey of the characters. Ensure a cohesive world-building and a strong emotional impact.</prompt>"
                else:
                    chapter_content_prompt = f"<context>{rolling_context}</context> <prompt>Write Chapter {chapter_num} of the book '{book_title}' titled '{chapter_title}'. Continue the story, developing the characters and introducing a plot twist that deepens the conflict or mystery. End the chapter with a cliffhanger to keep the readers engaged. Incorporate genre-specific elements and themes that add depth to the narrative.</prompt>"
                chapter_content = generate_content(chapter_content_prompt, model).replace("To be continued...", "").strip()
                # Validate and add chapter
                if is_chapter_logical(chapter_title, chapter_content, rolling_context):
                    rolling_context += f"\n\nChapter {chapter_num}: {chapter_title}\n{chapter_content}"
                    pdf.set_chapter_title(chapter_num, f"Chapter {chapter_num}: {chapter_title}")
                    pdf.chapter_body(chapter_content)
                    chapter_generated = True
                    generated_chapters.append(f"Chapter {chapter_num}: {chapter_title}\n{chapter_content}")
                    console.insert(tk.END, f"Generated Chapter {chapter_num}: {chapter_title}\n")
                else:
                    console.insert(tk.END, f"Regenerating Chapter {chapter_num} due to logical inconsistencies.\n")
            except Exception as e:
                console.insert(tk.END, f"Error generating chapter {chapter_num}: {e}\n")
        progress_bar['value'] += 1
        root.update_idletasks()
    # Originality check
    check_originality(generated_chapters)
    save_button.config(state='normal')  # Enable the "Save as PDF" button
    console.insert(tk.END, "Book generation completed.\n")
    # Print generated chapters
    console.insert(tk.END, "Generated Chapters:\n")
    for chapter in generated_chapters:
        console.insert(tk.END, chapter + "\n\n")

def open_discord():
    webbrowser.open("https://discord.gg/FPN7vx4eVY")

root = tk.Tk()
root.title("Book Generator")
root.geometry("1000x950")  # Increase the size of the window to accommodate the console

tk.Label(root, text="Book Title").grid(row=0, column=0, sticky='w')
tk.Label(root, text="Author Name").grid(row=1, column=0, sticky='w')
tk.Label(root, text="Description").grid(row=2, column=0, sticky='nw')
tk.Label(root, text="Number of Chapters").grid(row=3, column=0, sticky='w')
tk.Label(root, text="Model").grid(row=4, column=0, sticky='w')  # Label for the model selection

title_entry = tk.Entry(root, width=50)
author_entry = tk.Entry(root, width=50)
description_text = tk.Text(root, width=50, height=10)  # Use Text widget for multi-line input
chapters_combobox = ttk.Combobox(root, width=48, values=[str(i) for i in range(1, 21)])
model_combobox = ttk.Combobox(root, width=48, values=["gpt-3.5-turbo-16k","gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"])  # Add more models as needed

title_entry.grid(row=0, column=1, padx=10, pady=10)
author_entry.grid(row=1, column=1, padx=10, pady=10)
description_text.grid(row=2, column=1, padx=10, pady=10)
chapters_combobox.grid(row=3, column=1, padx=10, pady=10)
model_combobox.grid(row=4, column=1, padx=10, pady=10)  # Position the model selection box
chapters_combobox.current(0)  # Set the default value to 1
model_combobox.current(0)  # Set the default model

progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=300)
progress_bar.grid(row=6, column=0, columnspan=2, pady=10)

tk.Button(root, text="Generate Book", command=generate_book).grid(row=5, column=0, columnspan=2, pady=10)

console_label = tk.Label(root, text="Output Console")
console_label.grid(row=7, column=0, sticky='w', padx=10, pady=5)
console = scrolledtext.ScrolledText(root, width=80, height=10)
console.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

save_button = tk.Button(root, text="Save as PDF", command=save_as_pdf, state='disabled')
save_button.grid(row=11, column=1, sticky='e', padx=10, pady=(0, 10))

about_label = tk.Label(root, text="About", font=("Arial", 14, "bold"))
about_label.grid(row=9, column=0, sticky='w', padx=10, pady=(20, 5))

creator_label = tk.Label(root, text="Creator: Legend of Ray")
creator_label.grid(row=10, column=0, sticky='w', padx=10)

discord_button = tk.Button(root, text="Join Ray's Discord", command=open_discord)
discord_button.grid(row=11, column=0, sticky='w', padx=10, pady=(0, 10))

root.mainloop()
