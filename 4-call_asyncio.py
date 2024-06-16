import asyncio
import json
from openai import AsyncOpenAI
# timeout_config = httpx.Timeout(600.0)  
# async_client = httpx.AsyncClient(timeout=timeout_config)


client = AsyncOpenAI(
    api_key="123",  # Replace with your actual API key
    # base_url="",  # Use the correct OpenAI API URL
    base_url="http://0.0.0.0:8000/v1/",  # Use the correct OpenAI API URL
    # http_client=async_client
)
Temperature = 0.0
TopPValue = 1.0


async def ask_question(prompt) -> str:
    whole_story_gen = await client.chat.completions.create(
        messages=[
            # {"role": "system","content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-3.5-turbo",
        temperature=Temperature, 
        top_p=TopPValue,
        max_tokens = 1024,
    )
    return whole_story_gen.choices[0].message.content

async def save_responses_to_jsonl(responses: list, filename: str) -> None:
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


async def working(type_name, step, id_A_list, id_B_list, id_C_list, prompt_list, outline_list):
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

        responses = await asyncio.gather(*[ask_question(prompt) for prompt in working_prompt_list])
        
        # Pair questions with their respective answers
        if id_C_list:
            paired_responses = list(zip(working_id_A_list, working_id_B_list, working_id_C_list, working_outline_list, responses))
        else:
            paired_responses = list(zip(working_id_A_list, working_id_B_list, working_outline_list, responses))
        
        # Save the responses to a JSONL file
        os.makedirs(f'qwen2-7b/IO/temp_{str(Temperature).replace(".","_")}_results', exist_ok=True)
        await save_responses_to_jsonl(paired_responses, f'qwen2-7b/IO/temp_{str(Temperature).replace(".","_")}_results/{type_name}.jsonl')
        if i % 100 == 0:
            print(f"Processed {i} stories")
    return 

import json,os
async def main() -> None:
    folder_path = 'task_story/IO'  # 指定文件夹路径
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
        await working(type_name, 8, id_A_list, id_B_list, id_C_list, prompt_list, outline_list)

asyncio.run(main())