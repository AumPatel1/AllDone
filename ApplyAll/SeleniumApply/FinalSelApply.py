from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from llmApply import generate_llm_response
from ResumeExtract import extract_resume_data


def apply_to_job(job_url: str, job_dscr: str, user_data: dict, resume_path: str, password: str):
    """
    Automates job application process using Selenium.
    
    Args:
        job_url: URL of the job application page
        job_dscr: Job description text
        user_data: Dictionary containing user information (name, email, mobile_number, experience, etc.)
        resume_path: Path to the resume file
        password: Password for account creation/login
    """
    # Setup Chrome options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Initialize driver
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(job_url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Try to create account if needed
        try:
            driver.find_element(By.XPATH, '//button[contains(text(), "Create Account")]').click()
            time.sleep(1)
            driver.find_element(By.ID, 'email-input').send_keys(user_data.get('email', ''))
            driver.find_element(By.ID, 'password-input').send_keys(password)
            driver.find_element(By.ID, 'confirm-password').send_keys(password)
            driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            time.sleep(3)
        except (NoSuchElementException, TimeoutException):
            pass  # Skip if logged in or no prompt

        # Fill standard fields
        try:
            name_parts = user_data.get('name', '').split()
            if len(name_parts) > 0:
                driver.find_element(By.NAME, 'firstName').send_keys(name_parts[0])
            if len(name_parts) > 1:
                driver.find_element(By.NAME, 'lastName').send_keys(name_parts[-1])
            
            driver.find_element(By.NAME, 'email').send_keys(user_data.get('email', ''))
            driver.find_element(By.NAME, 'phone').send_keys(user_data.get('mobile_number', ''))
        except NoSuchElementException:
            print("Warning: Could not find some standard form fields")

        # Experience/Skills: If textarea, send as string
        if 'experience' in driver.page_source.lower():
            try:
                exp_field = driver.find_element(By.CLASS_NAME, 'experience-textarea')
                experience_list = user_data.get('experience', [])
                if isinstance(experience_list, list):
                    exp_field.send_keys('\n'.join(experience_list))
                else:
                    exp_field.send_keys(str(experience_list))
            except NoSuchElementException:
                pass

        # Upload resume
        try:
            resume_upload = driver.find_element(By.XPATH, '//input[@type="file"]')
            resume_upload.send_keys(resume_path)
        except NoSuchElementException:
            print("Warning: Could not find file upload element")

        # Answer questions using LLM
        try:
            questions = driver.find_elements(By.CLASS_NAME, 'questions')
            for q in questions:
                question_text = q.text
                answer = generate_llm_response(question_text, job_dscr, user_data)
                try:
                    text_area = q.find_element(By.TAG_NAME, 'textarea')
                    text_area.send_keys(answer)
                except NoSuchElementException:
                    pass
        except NoSuchElementException:
            pass

        # Select country if dropdown exists
        try:
            select = Select(driver.find_element(By.NAME, 'country'))
            select.select_by_visible_text('United States')  # Hardcode or add to user_data
        except (NoSuchElementException, TimeoutException):
            pass

        # Submit
        try:
            driver.find_element(By.XPATH, '//button[contains(text(), "Submit")]').click()
            time.sleep(2)
            
            if "submitted" in driver.page_source.lower():
                print("Success! Application submitted.")
            else:
                print("Warning: Submission confirmation not found.")
        except NoSuchElementException:
            print("Warning: Could not find submit button")
            
    except Exception as e:
        print(f"Error during application process: {e}")
        raise
    finally:
        driver.quit()


if __name__ == "__main__":
    user_data = extract_resume_data('/path/to/resume.pdf')
    apply_to_job(
        'https://company.workday.com/jobs/123',
        'Job desc from scraper',
        user_data,
        '/path/to/resume.pdf',
        'yourpassword123'
    )
