# %%
# from openai import OpenAI


from openai import AzureOpenAI
    
client = AzureOpenAI(
    api_key="",  
    api_version="2024-02-01",
    azure_endpoint = ""
    )

def get_eval_prompt(response,reference_sentence):
    prompt = f"""Please assess the degree of integration between a specific subplot and the main narrative of the story using the following scale of 0 to 100. If you determine that the subplot is seamlessly integrated and indispensable to the main storyline, award a score of 100. Conversely, if it stands entirely on its own with minimal relevance to the main plot, rate it as 0.

### Subplot
{reference_sentence}

### Complete Story
{response}

Evaluate based on how closely the subplot is intertwined with the main story, and just provide a deterministic score followed by a concise and brief explanation, with a blank line between the two.

Score:

Explanation:"""
    return prompt

def asking(response,reference_sentence):
    prompt = get_eval_prompt(response,reference_sentence)
    # print(prompt)
    chat_completion = client.chat.completions.create(
        messages=[
            # {"role": "system","content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4",
        temperature=0.0, 
        # top_p=TopPValue,
        # max_tokens = 1024,
    )
    return chat_completion.choices[0].message.content
    # print(chat_completion.choices[0].message.content)
    # return upwarp_eval(chat_completion.choices[0].message.content)
    # res = "Score: 100\nExplanation: The subplot is seamlessly integrated with the main narrative, and it is indispensable to the main storyline."
    # return upwarp_eval(res)


# def upwarp_eval(eval_result):
#     # score = eval_result.split("Explanation:")[0].split("Score:")[1]
#     # explanation = eval_result.split("Explanation:")[1]
#     score = eval_result.split("\n\n")[0]
#     explanation = eval_result.split("\n\n")[1]
#     return int(score), explanation,eval_result


def ask_score_by_type(outline,response,type):

    if type == "a0 a1 B3 a3 a4":
        subplot = outline[2]
        # score,explanation,eval_result = asking(response,subplot)
        eval_result = asking(response,subplot)
        # return [score], [explanation], [eval_result]
        return [eval_result]
    
    elif type == "a0 B0 a2 B4 a4":
        subplot = outline[1]+" "+outline[3]
        # score,explanation,eval_result = asking(response,subplot)
        eval_result = asking(response,subplot)
        # return [score],[explanation], [eval_result]
        return [eval_result]
    elif type == "a0 B0 C0 a2 B4 C4 a4":
        subplot1 = outline[1]+" "+outline[4]
        # score1,explanation1,eval_result1 = asking(response,subplot1)
        eval_result1 = asking(response,subplot1)
        subplot2 = outline[2]+" "+outline[5]
        # score2,explanation2,eval_result2 = asking(response,subplot2)
        eval_result2 = asking(response,subplot2)
        # return [score1,score2],[explanation1,explanation2], [eval_result1,eval_result2]
        return [eval_result1,eval_result2]
    
    elif type == "a0 B0 a1 B1 a2 B2 a3 B3 a4 B4":
        subplot1 = outline[1]+" "+outline[3]+" "+outline[5]+" "+outline[7]+" "+outline[9]
        # score,explanation,eval_result = asking(response,subplot1)
        eval_result = asking(response,subplot1)
        # return [score],[explanation], [eval_result]
        return [eval_result]
    else:
        print("No such type")
        return None

from tqdm import trange
def get_gpt4_evaluation(results,type):
    # scores = []
    # score_box_list = []
    # explanation_box_list = []
    eval_result_box_list = []
    for i in trange(len(results)):
        outline = results[i]['outline']
        response = results[i]['response']
        # score_box,explanation_box,eval_result_box = ask_score_by_type(outline,response,type)
        eval_result_box = ask_score_by_type(outline,response,type)
        # explanation_box_list.append(explanation_box)
        eval_result_box_list.append(eval_result_box)
        # if len(score_box) == 1:
        #     score = score_box[0]
        # else:
        #     score = sum(score_box)/len(score_box)
        # scores.append(score)
    # return scores,score_box_list,explanation_box_list,eval_result_box_list
    return eval_result_box_list


# %%
def unwarp_response(response):
    if "\n\nStory:" in response:
        return response.rsplit("\n\nStory:",1)[-1].strip(), True
    elif "\n\nstory:" in response:
        return response.rsplit("\n\nstory:",1)[-1].strip(), True
    elif "\n\n**Story:" in response:
        return response.rsplit("\n\n**Story:",1)[-1].strip(), True
    elif "\n\n**story:" in response:
        return response.rsplit("\n\n**story:",1)[-1].strip(), True
    else:
        return response, False

# %%
import os
import json

type_match = {
    "主线情节点": "a0 a1 B3 a3 a4",
    "主线支线": "a0 B0 a2 B4 a4",
    "主线双支线": "a0 B0 C0 a2 B4 C4 a4",
    "双主线": "a0 B0 a1 B1 a2 B2 a3 B3 a4 B4"
}
task_result = "GPT4/COT/temp_0_7"
print(f"Start evaluating {task_result} results")
for filename in os.listdir(f"{task_result}_results"):
    file_path = os.path.join(f"{task_result}_results", filename)
    type_file = file_path.split('/')[-1].split('.')[0]
    type = type_match[type_file]
    if type_file != "主线情节点":
        continue
    with open(file_path, 'r', encoding='utf-8') as file:
        results = []
        for line in file:
            res = {}
            data = json.loads(line.strip())
            
            aid = data.get('Aid_list')
            bid = data.get('Bid_list')
            cid = data.get('Cid_list')
            outline = data.get('outline')
            raw_response = data.get('responses')
            response,flag = unwarp_response(raw_response)
            res['aid'] = aid
            res['bid'] = bid
            res['cid'] = cid
            res['outline'] = outline
            res['response'] = response
            results.append(res)

        # print(type)
        # gpt4_scores,score_box_list,explanation_box_list,eval_result_box_list = get_gpt4_evaluation(results,type)
        eval_result_box_list = get_gpt4_evaluation(results,type)

        # print(sum(gpt4_scores)/len(gpt4_scores))
        # print(gpt4_scores)
        # if file not exists, create it
        if not os.path.exists(f"{task_result}_eval_results"):
            os.makedirs(f"{task_result}_eval_results")
        with open(f"{task_result}_eval_results/{type_file}_eval_results.json", 'w', encoding='utf-8') as file:
            for i in range(len(results)):
                res = {}
                res['aid'] = results[i]['aid']
                res['bid'] = results[i]['bid']
                res['cid'] = results[i]['cid']
                res['outline'] = results[i]['outline']
                res['response'] = results[i]['response']
                # res['score'] = gpt4_scores[i]
                # res['explanation'] = explanation_box_list[i]
                res['eval_result'] = eval_result_box_list[i]
                file.write(json.dumps(res, ensure_ascii=False) + '\n')


