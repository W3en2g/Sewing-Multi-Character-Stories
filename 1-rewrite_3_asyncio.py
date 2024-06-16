import asyncio
import json
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="123",  # Replace with your actual API key
    base_url=""  # Use the correct OpenAI API URL
)


async def ask_question(context,sentence) -> str:
    chat_completion = await client.chat.completions.create(
        messages=[
            {"role": "system","content": "You are a writing assistant. Please change the third-person pronouns (he,him,his,she,her,they,them,their,etc) in the target sentence to the corresponding names according to the context. Please do not modify other parts of the target sentence. If the target sentence does not have a third-person pronoun, please do not modify it. You only need to output the modified sentence."},
            {"role": "user","content": f"Context:{context}, Target sentence:{sentence}"},
            # {"role": "assistant","content": f"Context:{context}, Target sentence:{sentence}"},
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content

async def save_responses_to_jsonl(responses: list, filename: str) -> None:
    """
    Save a list of responses to a JSONL file.
    Each response is a dictionary containing the question and the answer.
    """
    with open(filename, 'w') as f:
        for context, target_sentence, modified_sentence in responses:
            json_record = {"context":context,"target_sentence": target_sentence, "modified_sentence": modified_sentence}
            f.write(json.dumps(json_record) + '\n')

def getContext(sentences,i,j):
    former_sentences = []
    for k in range(1,j):
        former_sentences.append(sentences[str(k)][i])
    return " ".join(former_sentences)

import os
def get_files_in_directory(directory_path):
    """
    获取指定目录下所有文件的名称，并将其存放在一个列表中返回。
    
    :param directory_path: 字符串，表示目标文件夹的路径。
    :return: 包含文件夹下所有文件名的列表。
    """
    # 确保传入的路径存在且为目录
    if not os.path.isdir(directory_path):
        print("指定的路径不存在或不是一个目录")
        return []
    
    # 使用os.listdir()获取目录中的所有文件和子目录名称
    all_entries = os.listdir(directory_path)
    # 过滤出文件（排除子目录），可根据需要调整过滤条件
    files_only = [entry for entry in all_entries if os.path.isfile(os.path.join(directory_path, entry))]
    
    return files_only

import pandas as pd
import time
async def main() -> None:
    data16 = pd.read_csv('ROC_stories/ROCStories__spring2016 - ROCStories_spring2016.csv')
    data17 = pd.read_csv('ROC_stories/ROCStories_winter2017 - ROCStories_winter2017.csv')
    storyid_list = data16['storyid'].tolist() + data17['storyid'].tolist() # +clozeid_list
    # storytitle_list = data16['storytitle'].tolist() + data17['storytitle'].tolist()
    sentences = {}
    sentences['1'] = data16['sentence1'].tolist() + data17['sentence1'].tolist() # + cloze16test["InputSentence1"].tolist() + cloze16val["InputSentence1"].tolist() 
    sentences['2'] = data16['sentence2'].tolist() + data17['sentence2'].tolist() # + cloze16test["InputSentence2"].tolist() + cloze16val["InputSentence2"].tolist()
    sentences['3'] = data16['sentence3'].tolist() + data17['sentence3'].tolist() # + cloze16test["InputSentence3"].tolist() + cloze16val["InputSentence3"].tolist()
    sentences['4'] = data16['sentence4'].tolist() + data17['sentence4'].tolist() # + cloze16test["InputSentence4"].tolist() + cloze16val["InputSentence4"].tolist()
    sentences['5'] = data16['sentence5'].tolist() + data17['sentence5'].tolist() # + right_ends

    print("Total number of stories:", len(storyid_list))
    directory_to_read = 'modified_sentences'  # 请将'your_directory_path'替换为你要读取的文件夹路径
    done_file_names = get_files_in_directory(directory_to_read)
    
    for i in range(len(storyid_list)):
    # for i in range(100):
        if f'{storyid_list[i]}.jsonl' in done_file_names:
            # print("Already processed this story. Skipping...")
            continue
        context_list = []
        target_sentence_list = []
        for j in range(2,6):
            context = getContext(sentences,i,j)
            context_list.append(context)
            target_sentence_list.append(sentences[str(j)][i])

        zip_list = list(zip(context_list,target_sentence_list))
        # Concurrently ask all questions
        responses = await asyncio.gather(*[ask_question(context,tsent) for context,tsent in zip_list])
        
        # Pair questions with their respective answers
        paired_responses = list(zip(context_list, target_sentence_list, responses))
        
        # Save the responses to a JSONL file
        await save_responses_to_jsonl(paired_responses, f'modified_sentences/{storyid_list[i]}.jsonl')
        # await save_modified_story_to_jsonl(paired_responses, f'modified_story/{storyid_list[i]}.jsonl')
        if i % 100 == 0:
            # output the time
            print(f"Processed {i} stories at")
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            print("Responses saved to responses.jsonl")

asyncio.run(main())