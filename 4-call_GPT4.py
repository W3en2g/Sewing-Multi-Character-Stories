import asyncio
import json
from openai import AzureOpenAI
from openai import OpenAI
# timeout_config = httpx.Timeout(600.0)  
# async_client = httpx.AsyncClient(timeout=timeout_config)


# client = AsyncOpenAI(
#     api_key="123",  # Replace with your actual API key
#     # base_url="",  # Use the correct OpenAI API URL
#     base_url="http://0.0.0.0:8001/v1/",  # Use the correct OpenAI API URL
#     # http_client=async_client
# )

client = AzureOpenAI(
    api_key="",  
    # api_version="2023-12-01-preview",
    api_version="2024-02-01",

    azure_endpoint = ""
    )
Temperature = 0.7
TopPValue = 1.0


def ask_question(prompt) -> str:
    try:
        whole_story_gen = client.chat.completions.create(
            messages=[
                # {"role": "system","content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4",
            temperature=Temperature, 
            top_p=TopPValue,
            max_tokens = 1024,
        )
    except Exception as e:
        print(e)
        return "Error"
    return whole_story_gen.choices[0].message.content

def save_responses_to_jsonl(responses: list, filename: str) -> None:
    """
    Save a list of responses to a JSONL file.
    Each response is a dictionary containing the question and the answer.
    """
    with open(filename, 'a') as f:
        if len(responses[0]) == 4:
            for Aid_list, Bid_list, story_list, responses in responses:
                json_record = {"Aid_list":Aid_list,"Bid_list": Bid_list, "outline": story_list, "responses": responses}
                f.write(json.dumps(json_record) + '\n')
        else:
            for Aid_list, Bid_list, Cid_list, story_list, responses in responses:
                json_record = {"Aid_list":Aid_list,"Bid_list": Bid_list, "Cid_list": Cid_list, "outline": story_list, "responses": responses}
                f.write(json.dumps(json_record) + '\n')


def working(type_name, step, id_A_list, id_B_list, id_C_list, prompt_list, outline_list):
    for i in range(0,len(id_A_list),step):
    # for i in range(0,8,step):

        working_id_A_list = []
        working_id_B_list = []
        working_id_C_list = []
        working_prompt_list = []
        working_outline_list = []
        for j in range(step):
            if i+j < len(id_A_list):
                working_id_A_list.append(id_A_list[i+j])
                working_id_B_list.append(id_B_list[i+j])
                if id_C_list:
                    working_id_C_list.append(id_C_list[i+j])
                working_prompt_list.append(prompt_list[i+j])
                working_outline_list.append(outline_list[i+j])

        responses = [ask_question(prompt) for prompt in working_prompt_list]
        
        # Pair questions with their respective answers
        if id_C_list:
            paired_responses = list(zip(working_id_A_list, working_id_B_list, working_id_C_list, working_outline_list, responses))
        else:
            paired_responses = list(zip(working_id_A_list, working_id_B_list, working_outline_list, responses))
        
        # Save the responses to a JSONL file
        os.makedirs(f'GPT4/COT/temp_{str(Temperature).replace(".","_")}_results', exist_ok=True)
        save_responses_to_jsonl(paired_responses, f'GPT4/COT/temp_{str(Temperature).replace(".","_")}_results/{type_name}.jsonl')
        print(f"Processed {i} stories")

        # if i % 100 == 0:
        #     print(f"Processed {i} stories")
    return 

import json,os
def main() -> None:
    folder_path = 'task_story/COT'  # 指定文件夹路径
    files = [os.path.join(folder_path, file) for file in os.listdir(folder_path)]
    for file in files:
        id_A_list = []
        id_B_list = []
        id_C_list = []
        prompt_list = []
        outline_list = []
        with open(file, 'r', encoding='utf-8') as file:
            for line in file:
                data = json.loads(line.strip())

                id_A_list.append(data.get("storyID_A"))
                id_B_list.append(data.get("storyID_B"))
                if data.get("storyID_C"):
                    id_C_list.append(data.get("storyID_C"))
                prompt_list.append(data.get("prompt"))
                outline_list.append(data.get("outline"))
        type_name = file.name.split('/')[-1].replace('.jsonl', '')
        working(type_name, 2, id_A_list, id_B_list, id_C_list, prompt_list, outline_list)

main()