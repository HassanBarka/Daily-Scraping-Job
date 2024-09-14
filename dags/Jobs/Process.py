import spacy
import pandas as pd

def load_nlp():
    nlp = spacy.load("en_core_web_lg",disable = ['ner'])
    ruler = nlp.add_pipe("entity_ruler")
    ruler.from_disk("/home/huser/airflow_workspace/airflow/dags/Jobs/jz_skill_patterns.jsonl")
    return nlp

def get_skills(text, nlp):
    doc = nlp(text.lower())
    list_skills = []
    for ent in doc.ents:
        if ent.label_ == "SKILL":
            list_skills.append(ent.text.lower())  
    
    list_skills = list(set(list_skills))
    return ', '.join(list_skills)

def get_type(text):
    if "stage" in text.lower() or "courte durée" in text.lower() or "internship" in text.lower():
        text = "stage"

    elif "alternance" in text.lower():
        text = "alternance"

    elif "cdi" in text.lower():
        text = "cdi"
    
    elif "cdd" in text.lower():
        text = "cdd"
    
    elif "freelance" in text.lower() or "indépendant" in text.lower():
        text = "freelance"
        
    else:
        text = "autre"

    return text.upper()

def read_dfs():
    indeed_path = "/home/huser/airflow_workspace/airflow/dags/Jobs/indeed.csv"
    jungle_path = '/home/huser/airflow_workspace/airflow/dags/Jobs/jungle.csv'
    linked_path = '/home/huser/airflow_workspace/airflow/dags/Jobs/linkedIn.csv'
    glassdoor_path = '/home/huser/airflow_workspace/airflow/dags/Jobs/glassdoor.csv'

    try:
        job_indeed = pd.read_csv(indeed_path)
    except:
        job_indeed = None
    try:
        job_jungle = pd.read_csv(jungle_path)
    except:
        job_jungle = None
    try:
        job_linked = pd.read_csv(linked_path)
    except:
        job_linked = None
    try:
        job_glassdoor = pd.read_csv(glassdoor_path)
    except:
        job_glassdoor = None

    job_df = pd.concat([job_linked,job_jungle,job_indeed,job_glassdoor],axis=0)
    job_df = job_df.dropna()
    job_df.reset_index(drop=True, inplace=True)
    return job_df


def processing():
    nlp = load_nlp()
    data = read_dfs()

    data["job_type"] = data["job_type"].str.lower().apply(lambda x: get_type(x))
    data["skills"] = data["job_text"].str.lower().apply(lambda x: get_skills(x,nlp))
    
    data.to_csv('/home/huser/airflow_workspace/airflow/dags/Jobs/jobs_daily.csv',index=False)