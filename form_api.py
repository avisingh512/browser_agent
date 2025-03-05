import random
import string
import time
from typing import List, Optional
from pydantic import BaseModel, Field as PydanticField
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fastapi import FastAPI, HTTPException

# Define the Field model
class Field(BaseModel):
    id: str
    label: str
    type: str
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

# FormAgent class to interact with the form
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

# Function to get form fields
def get_form_fields(state: FormState, agent: FormAgent) -> FormState:
    try:
        # Try to find the form in multiple ways
        try:
            form = agent.driver.find_element(By.ID, "myForm")
        except:
            print("Form with ID 'myForm' not found, trying first form")
            form = agent.driver.find_element(By.TAG_NAME, "form")
            
        elements = form.find_elements(By.XPATH, ".//input | .//select | .//textarea")
        current_field_ids = {field.id for field in state.fields}
        new_fields = []

        for element in elements:
            field_id = element.get_attribute("id")
            if not field_id or field_id in current_field_ids:
                continue
            field_type = element.get_attribute("type") or element.tag_name
            label = agent.get_label_text(element)
            new_fields.append(Field(id=field_id, label=label, type=field_type))

        updated_fields = state.fields + new_fields
        print(f"Found {len(updated_fields)} fields: {[f.label for f in updated_fields]}")
        return FormState(
            url=state.url,
            fields=updated_fields,
            initial_fields_fetched=True,
            current_field_id=state.current_field_id,
            submission_attempted=state.submission_attempted
        )
    except Exception as e:
        print(f"Error in get_form_fields: {e}")
        return state

# Function to generate input for a field
def generate_input_for_field(field: Field) -> Field:
    value_generators = {
        "text": lambda: ''.join(random.choices(string.ascii_letters, k=8)),
        "email": lambda: f"{''.join(random.choices(string.ascii_lowercase, k=5))}@example.com",
        "password": lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
        "number": lambda: str(random.randint(1, 100)),
        "tel": lambda: f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        "url": lambda: f"https://{''.join(random.choices(string.ascii_lowercase, k=5))}.com",
        "date": lambda: "2023-10-15",  # Example date
        "time": lambda: "12:34",  # Example time
        "datetime-local": lambda: "2023-10-15T12:34",  # Example datetime
        "month": lambda: "2023-10",  # Example month
        "week": lambda: "2023-W42",  # Example week
        "color": lambda: "#{:06x}".format(random.randint(0, 0xFFFFFF)),  # Random color
        "range": lambda: str(random.randint(0, 100)),  # Random range value
        "file": lambda: "C:/Users/avi/Downloads/meeting_analysis.txt",  # Example file path
        "search": lambda: ''.join(random.choices(string.ascii_letters, k=8)),
        "checkbox": lambda: random.choice([True, False]),
        "radio": lambda: random.choice(["option1", "option2", "option3"]),
        "select": lambda: random.choice(["Credit Card", "PayPal", "Bank Transfer"]),  # Example options
        "textarea": lambda: ' '.join(''.join(random.choices(string.ascii_letters, k=5)) for _ in range(3)),
        "multiselect": lambda: random.sample(["Feature 1", "Feature 2", "Feature 3", "Feature 4"], 2)  # Randomly select 2 options
    }
    
    field.value = value_generators.get(field.type, lambda: "default")()
    print(f"Generated value for {field.label}: {field.value}")
    return field

# Function to fill a field
def fill_field(field: Field, agent: FormAgent) -> Field:
    try:
        element = agent.driver.find_element(By.ID, field.id)
        if field.type in ["text", "email", "password", "textarea", "tel", "number", "url", "search"]:
            element.clear()
            element.send_keys(field.value)
        elif field.type == "select":
            Select(element).select_by_visible_text(field.value)
        elif field.type == "multiselect":
            select = Select(element)
            select.deselect_all()
            for value in field.value:
                select.select_by_visible_text(value)
        elif field.type == "checkbox":
            if element.is_selected() != field.value:
                element.click()
        elif field.type == "radio":
            agent.driver.find_element(By.XPATH, f"//input[@type='radio' and @value='{field.value}']").click()
        elif field.type in ["date", "time", "datetime-local", "month", "week"]:
            element.clear()
            element.send_keys(field.value)
        elif field.type == "color":
            element.clear()
            element.send_keys(field.value)
        elif field.type == "range":
            element.clear()
            element.send_keys(field.value)
        elif field.type == "file":
            element.send_keys(field.value)
        
        field.filled = True
        print(f"Filled {field.label} with {field.value}")
        return field
    except Exception as e:
        print(f"Error filling field {field.label}: {e}")
        return field

# Function to submit the form
def submit_form(agent: FormAgent) -> bool:
    try:
        try:
            form = agent.driver.find_element(By.ID, "myForm")
        except:
            print("Form with ID 'myForm' not found for submission, trying first form")
            form = agent.driver.find_element(By.TAG_NAME, "form")
            
        try:
            submit_button = form.find_element(By.XPATH, ".//button[@type='submit']")
        except:
            print("Submit button not found, trying input type submit")
            submit_button = form.find_element(By.XPATH, ".//input[@type='submit']")
            
        submit_button.click()
        time.sleep(2)
        print("Form submitted successfully")
        return True
    except Exception as e:
        print(f"Error submitting form: {e}")
        return False

# FastAPI app
app = FastAPI()

# API endpoint to process the form
@app.post("/process-form")
async def process_form(url: str):
    try:
        # Initialize the agent
        agent = FormAgent(url)
        state = FormState(url=url)

        # Get all form fields
        state = get_form_fields(state, agent)

        # Generate and fill all fields
        for field in state.fields:
            field = generate_input_for_field(field)
            field = fill_field(field, agent)

        # Submit the form
        submission_success = submit_form(agent)

        # Close the agent
        agent.close()

        # Return the result
        return {
            "status": "success",
            "submission_success": submission_success,
            "filled_fields": [{"label": field.label, "value": field.value} for field in state.fields]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)