import os
# import numpy as np
import openai
# from openai import OpenAI
# from chatgptmax import send
import tiktoken
# from config import OPENAI_API_KEY

# set the api for chatcpt
openai.api_key = 'sk-proj-U61bfJCZ2rHE7JFXxBN9T3BlbkFJdCwRDhqNqc6bt2deVQHJ'


def read_file_content(file_path1):
    with open(file_path1, 'r', encoding='utf-8') as file:
        return file.read()


def send(
    prompt=None,
    text_data=None,
    chat_model="gpt-3.5-turbo",
    model_token_limit=8192,
    max_tokens=2500,
):
    """
    Send the prompt at the start of the conversation and then send chunks of text_data to ChatGPT via the OpenAI API.
    If the text_data is too long, it splits it into chunks and sends each chunk separately.

    Args:
    - prompt (str, optional): The prompt to guide the model's response.
    - text_data (str, optional): Additional text data to be included.
    - max_tokens (int, optional): Maximum tokens for each API call. Default is 2500.

    Returns:
    - list or str: A list of model's responses for each chunk or an error message.
    """

    # Check if the necessary arguments are provided
    if not prompt:
        return "Error: Prompt is missing. Please provide a prompt."
    if not text_data:
        return "Error: Text data is missing. Please provide some text data."

    # Initialize the tokenizer
    tokenizer = tiktoken.encoding_for_model(chat_model)

    # Encode the text_data into token integers
    token_integers = tokenizer.encode(text_data)

    # Split the token integers into chunks based on max_tokens
    chunk_size = max_tokens - len(tokenizer.encode(prompt))
    chunks = [
        token_integers[i: i + chunk_size]
        for i in range(0, len(token_integers), chunk_size)
    ]

    # Decode token chunks back to strings
    chunks = [tokenizer.decode(chunk) for chunk in chunks]

    responses = []
    messages = [
        {"role": "user", "content": prompt},
        {
            "role": "user",
            "content": "To provide the context for the above prompt, I will send you text in parts. When I am "
                       "finished, I will tell you 'ALL PARTS SENT'. Do not answer until you have received all"
                       " the parts.",
        },
    ]

    for chunk in chunks:
        messages.append({"role": "user", "content": chunk})

        # Check if total tokens exceed the model's limit and remove oldest chunks if necessary
        while (
            sum(len(tokenizer.encode(msg["content"])) for msg in messages)
            > model_token_limit
        ):
            messages.pop(1)  # Remove the oldest chunk

        # client = OpenAI()
        response = openai.ChatCompletion.create(model=chat_model, messages=messages)
        chatgpt_response = response.choices[0].message["content"].strip()
        responses.append(chatgpt_response)

    # Add the final "ALL PARTS SENT" message
    messages.append({"role": "user", "content": "ALL PARTS SENT"})
    response = openai.ChatCompletion.create(model=chat_model, messages=messages)
    final_response = response.choices[0].message["content"].strip()
    responses.append(final_response)

    return responses


if __name__ == "__main__":
    # Specify the path to your file
    file_path = "brain_massage.txt"

    # Read the content of the file
    file_content = read_file_content(file_path)

    # Define your prompt
    prompt_text = "Write me a file that I can transfer to a Raspberry Pi chip that will contain operating " \
                  "instructions for the capsule where you can control the lights and temperature and the " \
                  "frequencies and smells that are activated in the capsule, at suitable times for a text file" \
                  " that dubs the capsule"  # together with a text file that describes when to activate everything

    # Send the file content to ChatGPT
    responses1 = send(prompt=prompt_text, text_data=file_content)

    # Print the responses
    for response1 in responses1:
        print(response1)


