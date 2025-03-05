import os
import random
import string
import time
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field as PydanticField
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fastapi import FastAPI, HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Define the Field model
class Field(BaseModel):
    id: str
    label: str
    type: str
    options: Optional[List[str]] = None
    filled: bool = False
    value: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

# Define the FormState model
class FormState(BaseModel):
    url: str
    fields: List[Field] = PydanticField(default_factory=list)
    current_field_id: Optional[str] = None
    initial_fields_fetched: bool = False
    submission_attempted: bool = False

# Base FormAgent class
class FormAgent:
    def __init__(self, url: str):
        self.url = url
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get(url)
        time.sleep(2)
        print(f"Successfully loaded URL: {url}")

    def get_label_text(self, element):
        try:
            label = self.driver.find_element(By.XPATH, f"//label[@for='{element.get_attribute('id')}']")
            return label.text.strip() or element.get_attribute("name") or "Unknown"
        except:
            return element.get_attribute("name") or "Unknown"

    def close(self):
        self.driver.quit()
        print("Browser closed successfully")

# AI-powered FormAgent
class AIFormAgent(FormAgent):
    def __init__(self, url: str):
        super().__init__(url)
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key="API_KEY",
            temperature=0.3
        )
    
    def get_select_options(self, element) -> List[str]:
        if element.tag_name.lower() == "select":
            return [option.text for option in Select(element).options]
        return []

    def interpret_field(self, field: Field) -> str:
        try:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", "You are a web form filling expert. Generate appropriate values based on the context."),
                ("human", """Generate a valid value for this form field:
                Label: {label}
                Type: {field_type}
                Options: {options}
                
                Rules:
                1. Use realistic values
                2. Match format requirements
                3. No placeholder text
                4. Respond ONLY with the value""")
            ])
            
            chain = prompt_template | self.llm
            response = chain.invoke({
                "label": field.label,
                "field_type": field.type,
                "options": field.options if field.options else "None"
            })
            
            return response.content.strip()
        except Exception as e:
            print(f"LLM Error: {e}")
            return self.fallback_value_generator(field)

    def fallback_value_generator(self, field: Field) -> str:
        # Rule-based fallback
        generators = {
            "text": lambda: f"Test {random.randint(100,999)}",
            "email": lambda: f"user{random.randint(100,999)}@example.com",
            "password": lambda: ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%', k=12)),
            "number": lambda: str(random.randint(1, 1000)),
            "tel": lambda: f"{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
            "select": lambda: random.choice(field.options) if field.options else "Option 1"
        }
        return generators.get(field.type, lambda: "Test Value")()

# Updated form processing functions
def get_form_fields(state: FormState, agent: AIFormAgent) -> FormState:
    try:
        form = agent.driver.find_element(By.XPATH, "//form")
        elements = form.find_elements(By.XPATH, ".//input | .//select | .//textarea")
        
        updated_fields = []
        for element in elements:
            field_id = element.get_attribute("id")
            if not field_id:
                continue
                
            field_type = element.get_attribute("type") or element.tag_name.lower()
            label = agent.get_label_text(element)
            options = agent.get_select_options(element)
            
            updated_fields.append(Field(
                id=field_id,
                label=label,
                type=field_type,
                options=options
            ))
        
        return FormState(
            url=state.url,
            fields=updated_fields,
            initial_fields_fetched=True
        )
    except Exception as e:
        print(f"Field detection error: {e}")
        return state

def fill_field(field: Field, agent: AIFormAgent) -> Field:
    try:
        element = agent.driver.find_element(By.ID, field.id)
        field.value = agent.interpret_field(field)
        
        # Special handling for different field types
        if field.type == "select":
            Select(element).select_by_visible_text(field.value)
        elif field.type == "checkbox":
            if element.is_selected() != (field.value.lower() == "true"):
                element.click()
        elif field.type == "radio":
            agent.driver.find_element(By.XPATH, 
                f"//input[@type='radio' and @value='{field.value}']").click()
        else:
            element.clear()
            element.send_keys(field.value)
            
        field.filled = True
        print(f"AI-filled {field.label} with {field.value}")
        return field
    except Exception as e:
        print(f"Filling error: {e}")
        return field

# FastAPI setup
app = FastAPI()

@app.post("/process-form")
async def process_form(url: str):
    try:
        agent = AIFormAgent(url)
        state = FormState(url=url)
        
        # Get and fill fields
        state = get_form_fields(state, agent)
        for field in state.fields:
            field = fill_field(field, agent)
        
        # Submit form
        submit_button = agent.driver.find_element(By.XPATH, "//form//button[@type='submit']")
        submit_button.click()
        time.sleep(2)
        
        agent.close()
        return {
            "status": "success",
            "filled_fields": [{"label": f.label, "value": f.value} for f in state.fields]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)