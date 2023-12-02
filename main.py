from langchain.chat_models import ChatOpenAI as OpenAI
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from readtext import read_text, write_to_file, read_text_from_offset, read_text_file

import time

load_dotenv()


with open('./docs/prompts/person-list.prompt', 'r') as file:
    PERSON_LIST_PROMPT = file.read().strip()

with open('./docs/prompts/summary-begin.prompt', 'r') as file:
    SUMMARY_BEGIN = file.read().strip()

with open('./docs/prompts/create-summary.prompt', 'r') as file:
    CREATE_SUMMARY_PROMPT = file.read().strip()

with open('./docs/prompts/evaluation.prompt', 'r') as file:
    EVALUATION_PROMPT = file.read().strip()

MAIN_DOCUMENT = 'Teil1.docx'


def create_chain(input_variables, prompt, temperature=0.8):
    llm = OpenAI(
        temperature=temperature,
        model_name="gpt-4-1106-preview"
        )

    prompt_template_name = PromptTemplate(
        input_variables=input_variables,
        template = prompt
    )
        
    name_chain = LLMChain(llm=llm, prompt=prompt_template_name)

    return name_chain



def generate_summary(current_summary, temperature, offset, num_words):


    print("Generating text from word " + str(offset))
    new_section = read_text_from_offset(MAIN_DOCUMENT, offset, num_words) 

    name_chain = create_chain(['summary', 'new_section'], CREATE_SUMMARY_PROMPT, temperature)

    response = name_chain({"summary": current_summary, "new_section": new_section})
    return response


def evaluate_summary(temperature, num_words):
    summary = read_text_file(f"summary-{num_words}.docx")
    full_text = read_text(MAIN_DOCUMENT, num_words)

    name_chain = create_chain(['full_text', 'summary'], EVALUATION_PROMPT, temperature)

    response = name_chain({"full_text": full_text, "summary": summary})
    return response
    

if __name__ == "__main__":

    temperature = 0.8
    num_words = 35000
    
    # evaluation = (evaluate_summary(temperature, num_words)['text'])
    # write_to_file(f"evaluation-{temperature}-{num_words}.docx", evaluation)

    current_summary = SUMMARY_BEGIN
    num_words = 5000

    for offset in range(10000, 15000, 5000):
        current_summary = current_summary + generate_summary(current_summary, temperature, offset, num_words)['text']
        write_to_file(f"continued-summary-{temperature}-{num_words}-{offset}-test.docx", current_summary)
        time.sleep(60)
    