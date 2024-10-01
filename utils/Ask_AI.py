from openai import OpenAI
import os
def call_gpt(data):
    '''
    Takes the json, calls chatgpt api and generates an answer
    '''
    # code to call gpt api
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    
    with open('./prompt_template/Ask_AI.txt', 'r') as file:
        prompt_template = file.read()
    
    extracted = []
    keys_json = ['answer', 'imageUrl', 'question']
    
    for key in keys_json:
        if key in data:
           extracted.append(data[key])
           
    question = extracted[2].replace('\n', '').replace('\"', '')
    image = extracted[1]
    answer = extracted[0]

    
    prompt = prompt_template.format(question=question, image=image, answer=answer)
    
    
    response = client.chat.completions.create(
        model='gpt-4o-mini',  
        messages=[
            {"role": "assistant", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.2,
        n=1,
        stop=None
    )
    
    content= response.choices[0].message.content
    
    content = content.replace('\n', '').replace('\"', '').replace('\u2019', "'").replace('"','').replace('\u201c', '"').replace('\u201d', '"')
        
    return content
