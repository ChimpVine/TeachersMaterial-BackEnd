from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
import json
import langchain_core

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
def quiz_generator(topic, language, subject, number, difficulty):  
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.5,
        max_tokens=4095
    )

    prompt_template = """Role: Act as a particular subject teacher and complete the given task below as shown in example.

        Task: Generate quiz with questions. The quiz should contain MCQ with 4 options and only one correct answer. 

        Example:
        Query : Generate quiz on the topic 'linear algebra'. The language should be 'English' and difficulty should be 'medium'. The subject is 'maths'. Generate '5' number of questions in each quiz.

        AI Output : 
        (
          "Quiz": [
        (
              "Answer 1": "1 0 0, 0 1 0, 0 0 1",
              "Answer 2": "1 0 0, 0 1 0, 0 0 0",
              "Answer 3": "1 0 0, 0 0 0, 0 0 1",
              "Answer 4": "1 0 0, 0 0 1, 0 1 0",
              "Category": "Math",
              "Correct Answer": "1 0 0, 0 1 0, 0 0 1",
              "Question": "What is the identity matrix of size 3x3?",
              "Tags": [
                "Linear Algebra"
              ],
              "Topic": "linearalgebra"
            ),
            (
              "Answer 1": "0",
              "Answer 2": "1",
              "Answer 3": "2",
              "Answer 4": "-2",
              "Category": "Math",
              "Correct Answer": "-2",
              "Question": "What is the determinant of a 2x2 matrix [[1, 2], [3, 4]]?",
              "Tags": [
                "Linear Algebra"
              ],
              "Topic": "linearalgebra"
            ),
            (
              "Answer 1": "[19, 22], [43, 50]",
              "Answer 2": "[19, 22], [26, 50]",
              "Answer 3": "[7, 10], [15, 22]",
              "Answer 4": "[5, 12], [21, 32]",
              "Category": "Math",
              "Correct Answer": "[19, 22], [43, 50]",
              "Question": "What is the result of matrix multiplication of [[1, 2], [3, 4]] and [[5, 6], [7, 8]]?",
              "Tags": [
                "Linear Algebra"
              ],
              "Topic": "linearalgebra"
            ),
            (
              "Answer 1": "0",
              "Answer 2": "1",
              "Answer 3": "2",
              "Answer 4": "3",
              "Category": "Math",
              "Correct Answer": "0",
              "Question": "What is the rank of a 3x3 matrix with all elements as 0?",
              "Tags": [
                "Linear Algebra"
              ],
              "Topic": "linearalgebra"
            ),
            (
              "Answer 1": "[d, -b], [-c, a]",
              "Answer 2": "[a, c], [b, d]",
              "Answer 3": "[d, c], [b, a]",
              "Answer 4": "[a, -b], [-c, d]",
              "Category": "Math",
              "Correct Answer": "[d, -b], [-c, a]",
              "Question": "What is the inverse of a 2x2 matrix [[a, b], [c, d]]?",
              "Tags": [
                "Linear Algebra"
              ],
              "Topic": "linearalgebra"
            )
          ]
        )
        Instructions:
        1. This is super important to always generate exact number of questions given in query.
        2. Always maintain the particular topic and output format while generating.
        3. Randomize the correct answer option number.
        4. Maintain the json format perfectly.
        {context} 
       """

    prompt = langchain_core.prompts.PromptTemplate(
                input_variables=["context"],
                template=prompt_template,
            )
    chain = LLMChain(llm=llm, prompt= prompt)

    int_number= int(number)
    new_number = int_number+10
    
    query = f" Generate quiz on the topic '{topic}'. The language should be '{language}' and difficulty should be '{difficulty}'. The subject is '{subject}'. Generate '{new_number}' number of questions in each quiz."
    quizz = chain.invoke({'context':query}) 
    print(quizz)
    
    main_quiz=(quizz['text']).replace('(','{')
    main_quiz=main_quiz.replace(')','}')
    main_quiz=main_quiz.replace('```json','')
    main_quiz=main_quiz.replace('```','')
    
    main_quiz=json.loads(main_quiz)
    return main_quiz


# time_1= time.time()
# quiz_generator(topic='photosynthesis', language='english', subject='science', number='5', difficulty='easy')
# time_2 = time.time()
# time_3 = time_2 - time_1
# print(time_3)
