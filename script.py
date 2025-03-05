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
from langgraph.graph import StateGraph, END

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
    iteration_count: int = 0
    max_iterations: int = 30  # Safety limit

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
            submission_attempted=state.submission_attempted,
            iteration_count=state.iteration_count + 1,  # Increment iteration counter
            max_iterations=state.max_iterations
        )
    except Exception as e:
        print(f"Error in get_form_fields: {e}")
        return state

# Function to check if there are new or unfilled fields
def has_new_or_unfilled_fields(state: FormState) -> bool:
    # Check if max iterations reached
    if state.iteration_count >= state.max_iterations:
        print(f"Max iterations ({state.max_iterations}) reached")
        return False
    
    unfilled_fields = [field for field in state.fields if not field.filled]
    result = len(unfilled_fields) > 0 and not state.submission_attempted
    print(f"Checking unfilled: {len(unfilled_fields)} fields remain, submission_attempted: {state.submission_attempted}")
    return result

# Function to find an unfilled field
def find_unfilled_field(state: FormState) -> FormState:
    unfilled_fields = [field for field in state.fields if not field.filled]
    if not unfilled_fields:
        print("No unfilled fields found")
        return state
    
    field = unfilled_fields[0]
    print(f"Selected field to fill: {field.label}")
    return FormState(
        url=state.url,
        fields=state.fields,
        current_field_id=field.id,
        initial_fields_fetched=state.initial_fields_fetched,
        submission_attempted=state.submission_attempted,
        iteration_count=state.iteration_count,
        max_iterations=state.max_iterations
    )

# Function to generate input for a field
def generate_input_for_field(state: FormState, agent: FormAgent) -> FormState:
    fields = state.fields.copy()
    current_field = next(field for field in fields if field.id == state.current_field_id)
    
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
        "file": lambda: "path/to/file.txt",  # Example file path
        "search": lambda: ''.join(random.choices(string.ascii_letters, k=8)),
        "checkbox": lambda: random.choice([True, False]),
        "radio": lambda: random.choice(["option1", "option2", "option3"]),
        "select": lambda: random.choice([opt.text for opt in Select(agent.driver.find_element(By.ID, current_field.id)).options if opt.text]) or "Credit Card",
        "textarea": lambda: ' '.join(''.join(random.choices(string.ascii_letters, k=5)) for _ in range(3)),
        "multiselect": lambda: random.sample([opt.text for opt in Select(agent.driver.find_element(By.ID, current_field.id)).options if opt.text], 2)  # Randomly select 2 options
    }
    
    current_field.value = value_generators.get(current_field.type, lambda: "default")()
    fields = [f if f.id != current_field.id else current_field for f in fields]
    print(f"Generated value for {current_field.label}: {current_field.value}")
    
    return FormState(
        url=state.url,
        fields=fields,
        current_field_id=state.current_field_id,
        initial_fields_fetched=state.initial_fields_fetched,
        submission_attempted=state.submission_attempted,
        iteration_count=state.iteration_count,
        max_iterations=state.max_iterations
    )

# Function to fill a field
def fill_field(state: FormState, agent: FormAgent) -> FormState:
    fields = state.fields.copy()
    current_field = next(field for field in fields if field.id == state.current_field_id)
    
    try:
        element = agent.driver.find_element(By.ID, current_field.id)
        if current_field.type in ["text", "email", "password", "textarea", "tel", "number", "url", "search"]:
            element.clear()
            element.send_keys(current_field.value)
        elif current_field.type == "select":
            Select(element).select_by_visible_text(current_field.value)
        elif current_field.type == "multiselect":
            select = Select(element)
            select.deselect_all()
            for value in current_field.value:
                select.select_by_visible_text(value)
        elif current_field.type == "checkbox":
            if element.is_selected() != current_field.value:
                element.click()
        elif current_field.type == "radio":
            agent.driver.find_element(By.XPATH, f"//input[@type='radio' and @value='{current_field.value}']").click()
        elif current_field.type in ["date", "time", "datetime-local", "month", "week"]:
            element.clear()
            element.send_keys(current_field.value)
        elif current_field.type == "color":
            element.clear()
            element.send_keys(current_field.value)
        elif current_field.type == "range":
            element.clear()
            element.send_keys(current_field.value)
        elif current_field.type == "file":
            element.send_keys(current_field.value)
        
        current_field.filled = True
        fields = [f if f.id != current_field.id else current_field for f in fields]
        print(f"Filled {current_field.label} with {current_field.value}")
        return FormState(
            url=state.url,
            fields=fields,
            current_field_id=state.current_field_id,
            initial_fields_fetched=state.initial_fields_fetched,
            submission_attempted=state.submission_attempted,
            iteration_count=state.iteration_count,
            max_iterations=state.max_iterations
        )
    except Exception as e:
        print(f"Error filling field {current_field.label}: {e}")
        return state

# Function to submit the form
def submit_form(state: FormState, agent: FormAgent) -> FormState:
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
        return FormState(
            url=state.url,
            fields=state.fields,
            current_field_id=state.current_field_id,
            initial_fields_fetched=state.initial_fields_fetched,
            submission_attempted=True,
            iteration_count=state.iteration_count,
            max_iterations=state.max_iterations
        )
    except Exception as e:
        print(f"Error submitting form: {e}")
        return FormState(
            url=state.url,
            fields=state.fields,
            current_field_id=state.current_field_id,
            initial_fields_fetched=state.initial_fields_fetched,
            submission_attempted=True,  # Mark as attempted even if failed
            iteration_count=state.iteration_count,
            max_iterations=state.max_iterations
        )

# Main function
def main():
    url = "http://localhost:3000"
    try:
        agent = FormAgent(url)
        initial_state = FormState(url=url)
        
        # Manual execution
        state = initial_state
        while True:
            state = get_form_fields(state, agent)
            if not has_new_or_unfilled_fields(state):
                state = submit_form(state, agent)
                break
            state = find_unfilled_field(state)
            state = generate_input_for_field(state, agent)
            state = fill_field(state, agent)
            if state.iteration_count >= state.max_iterations:
                print(f"Breaking manual execution after {state.iteration_count} iterations")
                break
        
        print("Form processing completed!")
        print("Final state:")
        for field in state.fields:
            print(f"  {field.label}: {field.value} (filled: {field.filled})")
        print(f"Submission attempted: {state.submission_attempted}")
        print(f"Iterations: {state.iteration_count}")
        
    except Exception as e:
        print(f"Main execution error: {e}")
    finally:
        agent.close()

if __name__ == "__main__":
    main()