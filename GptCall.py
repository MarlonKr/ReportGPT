import openai
import tiktoken

def gpt_call (message_input, model="gpt-3.5-turbo", temperature=0, system_message=False, memory=None, timeout=None):
        
        # Function to truncate a string to the maximum token count.
        def truncate_string(message):
            message_tokens = tokenizer.encode(message)
            return tokenizer.decode(message_tokens[:max_tokens]) if len(message_tokens) > max_tokens else message

        # Function to truncate a list of messages to the maximum token count.
        def truncate_messages(messages):
            truncated_messages = []
            current_tokens = 0
            for message in messages:
                content = message["content"]
                content_tokens = tokenizer.encode(content)
                current_tokens += len(content_tokens)
                if current_tokens > max_tokens:
                    excess_tokens = current_tokens - max_tokens
                    message["content"] = tokenizer.decode(content_tokens[:-excess_tokens])
                    truncated_messages.append(message)
                    break
                truncated_messages.append(message)
            return truncated_messages
        
        # Initialize tokenizer .
        tokenizer = tiktoken.encoding_for_model(model)
        # if len(tokenizer.encode(message_input)) > 4050: use gpt-3.5-turbo-16k
        if "gpt-3.5" in model and len(tokenizer.encode(str(message_input))) > 4050:
            model = "gpt-3.5-turbo-16k"
            tokenizer = tiktoken.encoding_for_model(model)

        # Set maximum tokens for the given model.
        max_tokens = {
            "gpt-3.5-turbo": 4050,
            "gpt-4": 8150,
            "gpt-3.5-turbo-16k": 16000,
            }.get(model)

        # If system_message is provided, subtract its token count from max_tokens.
        if system_message != False and tokenizer:
            system_message_tokens = len(tokenizer.encode(system_message))
            max_tokens -= system_message_tokens
        
        # Prepare final_message according to the format of message_input.
        final_message = None
        # check if message_input is a string or a list of messages
        format = "string" if isinstance(message_input, str) else "message"

        if format == "string":
            truncated_message = truncate_string(message_input)
            final_message = [{"role": "user", "content": truncated_message}]
            if system_message:
                final_message.insert(0, {"role": "system", "content": system_message})

        else:
            final_message = truncate_messages(message_input)
            if isinstance(system_message, str):
                final_message.insert(0, {"role": "system", "content": system_message})
                

        #app.logger.debug(model)

        # Make chat requests until successful, up to a maximum of 5 retries.
        response = None
        # Use Default Timeout if None was given
        if timeout is None:
            set_timeout = 200
        else:
            set_timeout = timeout
        for _ in range(5):
            try:
                chat_kwargs = {"model": model, "messages": final_message, "temperature": temperature}
                response = openai.ChatCompletion.create(request_timeout=set_timeout, **chat_kwargs)
                break  # Break if request is successful.

            except openai.error.Timeout as timeout_err: 
                print("Encountered a timeout error. Not retrying.")
                # Dont break, until we have retry button in the UI
                # break  # Break immediately if it's a timeout error.

            except Exception as e:
                print(e)
                print("Encountered an error. Retrying...")
                # time.sleep(2)  # Retry after 2 seconds.

        if not response:
            raise Exception("Unable to get a response from the model")

        response = response.choices[0].message.content
        # print seperator
        print("-" * 50 + "\n\n")
        print(f"response_content: \n\n{response}")
        print("-" * 50 + "\n\n")
        #app.logger.debug("-" * 50 + "\n\n")
        
        
        #input_tokens += len(tokenizer.encode(str(final_message)))
        #output_tokens += len(tokenizer.encode(str(response)))
        # Return response content
        return response
