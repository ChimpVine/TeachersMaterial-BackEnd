import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize LLM once
llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.5,
    max_tokens=4095
)

# Function to generate passage options based on initial inputs
def generate_question(passage, selected_questions, questions_per_type):
    # Debugging: check current directory
    print("Current working directory:", os.getcwd())

    # Function to load the prompt template based on the difficulty
    def load_prompt_template(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    
    # Construct the file path for the correct prompt
    prompt_template_path = os.path.join('prompt_template', 'Assessment', 'Comprehension','reading','question.txt')

    # Load the selected prompt template
    prompt = load_prompt_template(prompt_template_path)
    if prompt is None:
        raise Exception("Failed to load prompt template.")
    
    # Format the prompt with the provided values

    formatted_prompt = prompt.replace("{passage}", passage).replace("{selected_questions}", str(selected_questions)).replace("{questions_per_type}", str(questions_per_type))


    # Generate the passage using the LLM
    try:
        response = llm.predict(formatted_prompt)
        
        cleaned_response = response.strip()

    # Attempt to parse as JSON
        try:
            parsed_output = json.loads(cleaned_response)
            # Format the parsed output as a JSON string
            return json.dumps(parsed_output, indent=4)
        except json.JSONDecodeError:
            # If not JSON, return the cleaned response directly as a JSON string
            return json.dumps({"response": cleaned_response}, indent=4)
    except Exception as e:
        print(f"Error generating questions: {e}")
        return json.dumps({"error": str(e)}, indent=4)
    except Exception as e:
        return {"error": str(e)}



# # Example usage
# if __name__ == "__main__":
#     # Step 1: First input - generate passage
    
#     passage = "The water cycle is a continuous process that describes how water moves through our environment. This cycle is vital for sustaining life on Earth and consists of four main stages: evaporation, condensation, precipitation, and collection.  Evaporation occurs when the sun heats up water in oceans, lakes, and rivers. As the water warms, it transforms into vapor and rises into the atmosphere. This process is crucial because it helps to purify the water by leaving impurities behind.  Once in the atmosphere, the water vapor cools and undergoes condensation. During this stage, the vapor turns back into tiny water droplets, forming clouds. These clouds can hold a significant amount of water, and when they become too heavy, the water must return to the Earth.  This return is known as precipitation. It can occur in various forms, such as rain, snow, sleet, or hail, depending on the temperature and conditions in the atmosphere. Precipitation replenishes water sources on the ground.  Finally, the collected water gathers in rivers, lakes, and oceans. Some of it seeps into the ground, replenishing underground aquifers. This collection is essential for maintaining ecosystems and providing fresh water for drinking and agriculture.  The water cycle is not just a sequence of events; it is a vital system that supports life. It illustrates how interconnected our planet is, as water continually moves and changes form, ensuring that all living organisms have the water they need to thrive."
#     questions_per_type=5
#     selected_questions=["True/False, MCQs, Fill in the Blanks, Question/Answer"]
#     result=generate_question(passage, selected_questions, questions_per_type)          
#         # Add questions to the generated passage
#     print("\nFull Passage with Questions:\n", result)
