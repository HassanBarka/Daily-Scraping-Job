from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import Jobs.IndeedScraper as indeed_scraper
import Jobs.JungleScraper as jungle_scraper
import Jobs.LinkedScrper as linked_scraper
import Jobs.GlassdoorScraper as glassdoor_scraper
from Jobs.Load_Data import load_data, create_jobDB
from Jobs.Process import processing


def get_indeed_data():
    Keywords = ["data Scientist","data analyst","data engineer","web developer",'mobile developer']
    indeed_path = '/home/huser/airflow_workspace/airflow/dags/Jobs/indeed.csv'
    df = indeed_scraper.get_datas(Keywords)
    df.dropna(inplace=True)
    df.to_csv(indeed_path,index=False)
    print("Done!")

def get_jungle_data():
    Keywords = ["data Scientist","data analyst","data engineer","web developer",'mobile developer']
    jungle_path = '/home/huser/airflow_workspace/airflow/dags/Jobs/jungle.csv'
    df = jungle_scraper.get_datas(Keywords)
    df.dropna(inplace=True)
    df.to_csv(jungle_path,index=False)
    print("Done!")

def get_glassdoor_data():
    Keywords = ["data Scientist","data analyst","data engineer","web developer",'mobile developer']
    glassdoor_path = '/home/huser/airflow_workspace/airflow/dags/Jobs/glassdoor.csv'
    df = glassdoor_scraper.get_datas(Keywords)
    df.dropna(inplace=True)
    df.to_csv(glassdoor_path,index=False)
    print("Done!")

def get_linked_data():
    Keywords = ["data Scientist","data analyst","data engineer","web developer",'mobile developer']
    Locations = ["france","Tunisie"]
    linked_path = '/home/huser/airflow_workspace/airflow/dags/Jobs/linkedIn.csv'

    driver = linked_scraper.connect()
    df = linked_scraper.get_datas(driver,Keywords,Locations)
    df.dropna(inplace=True)
    df.to_csv(linked_path,index=False)
    print("Done!")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 17),
    'email': ['hassounibarka@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG('jobs_etl',
         default_args=default_args,
         schedule_interval='0 18 * * *',
         catchup=False
         ) as dag:

    task0 = PythonOperator(
        task_id='jungle_scraper',
        python_callable=get_jungle_data,
        provide_context=True,
    )
    task1 = PythonOperator(
        task_id='indeed_scraper',
        python_callable=get_indeed_data,
        provide_context=True,
    )
    task2= PythonOperator(
        task_id='glassdoor_scraper',
        python_callable=get_glassdoor_data,
        provide_context=True,
    )
    task3= PythonOperator(
        task_id='linkedIn_scraper',
        python_callable=get_linked_data,
        provide_context=True,
    )
    task4= PythonOperator(
        task_id='Data_processing',
        python_callable=processing,
        provide_context=True,
    )
    task5= PythonOperator(
        task_id='Create_Job_Table',
        python_callable=create_jobDB,
        provide_context=True,
    )
    task6= PythonOperator(
        task_id='Loading_Data_to_DataBase',
        python_callable=load_data,
        provide_context=True,
    )
    
    #set task dependencies
    task0 >> task1 >> task2 >> task3 >> task4 >> task5 >> task6

print('DAG defined successfully')