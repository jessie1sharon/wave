import openai
# from chatgptmax import send
import tiktoken

# set the api for chatcpt
openai.api_key = 'sk-proj-611ezXEzdT6v9R7Ofv1TT3BlbkFJdqm7QgqpbuNd2qVRNUdq'


def read_file_content(file_path1):
    with open(file_path1, 'r', encoding='utf-8') as file:
        return file.read()


def send(
    prompt=None,
    text_data=None,
    instruction_data=None,
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

    start_phrase = "To provide the context for the above prompt, I will send you text in parts. When I am " \
                   "finished, I will tell you 'ALL PARTS SENT'. Do not answer until you have received all" \
                   " the parts."
    # Initialize the tokenizer
    tokenizer = tiktoken.encoding_for_model(chat_model)

    # Encode the text_data into token integers
    token_integers = tokenizer.encode(text_data)

    # Split the token integers into chunks based on max_tokens
    chunk_size = max_tokens - len(tokenizer.encode(prompt)) - \
                 len(tokenizer.encode(start_phrase)) - 3 * (len(tokenizer.encode("\"role\": \"user\", \"content\": ")))
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
                       " the parts. the instruction file:",
        },
    ]

    first = messages.append({"role": "user", "content": instruction_data})  # send the API the instruction file
    response = openai.ChatCompletion.create(model=chat_model, messages=messages)
    chatgpt_response = response.choices[0].message["content"].strip()
    responses.append(chatgpt_response)
    # print("response")
    # print(responses)
    # print("message")
    # print(messages)
    # print(chatgpt_response)
    messages.pop(2)
    messages.pop(1)
    # messages.pop(0)
    # breakpoint()

    for chunk in chunks:
        messages.append({"role": "user", "content": chunk})

        # Check if total tokens exceed the model's limit and remove oldest chunks if necessary
        while (
            sum(len(tokenizer.encode(msg["content"])) for msg in messages)
            > model_token_limit
        ):
            messages.pop(1)  # Remove the oldest chunk

        response = openai.ChatCompletion.create(model=chat_model, messages=messages)
        chatgpt_response = response.choices[0].message["content"].strip()
        responses.append(chatgpt_response)
        # print(messages)
        messages.pop(0)

    # Add the final "ALL PARTS SENT" message
    # messages.pop(0)
    messages.append({"role": "user", "content": "ALL PARTS SENT"})
    response = openai.ChatCompletion.create(model=chat_model, messages=messages)
    final_response = response.choices[0].message["content"].strip()
    responses.append(final_response)
    print(messages)

    return responses


if __name__ == "__main__":
    # Specify the path to your file
    file_path = "brain_massage.txt"

    instruction_path = "instructions.txt"

    # Read the content of the files
    file_content = read_file_content(file_path)
    instruction_content = read_file_content(instruction_path)

    # Define your prompt
    prompt_text = "Write me a file that I can transfer to a Raspberry Pi chip that will contain operating " \
                  "instructions for a capsule where you can control the lights and temperature and the " \
                  "frequencies and smells that are activated in the capsule, at according times to a text" \
                  " file that dubs the capsule, together with instructions that describes when to activate everything" \
                  ". first the instructions and then the dub file,please don't reply with the text translated"

    # Send the file content & instruction to ChatGPT
    answers = send(prompt=prompt_text, text_data=file_content, instruction_data=instruction_content)

    # Print the responses
    for answer in answers:
        print(answer)
