import requests
import json
import pandas as pd
import os
import streamlit as st
import plotly.express as px
from time import sleep

job_categories = {
    'eng': 'Software Engineering',
    'eng_generic': '-> Software Engineer',
    'eng_backend': '-> Backend',
    'eng_web': '-> Frontend',
    'eng_fullstack': '-> Fullstack',
    'eng_mobile': '-> Mobile',
    'eng_cloud': '-> Cloud',
    'eng_embedded': '-> Embedded',
    'eng_devops': '-> DevOps Engineer',
    'eng_sre': '-> Site Reliability Engineer (SRE)',
    'eng_infra': '-> Platform Infra',
    'eng_security': '-> Security Engineering',
    'eng_data': '-> Data Engineer',
    'eng_ml': '-> ML Engineer',
    'eng_ai': '-> AI Engineer',
    'eng_architect': '-> Architect',
    'eng_solutions_architect': '-> Solutions Architect',
    'eng_partner': '-> Partner Engineer',
    'eng_sales': '-> Sales Engineer',
    'eng_bi': '-> BI Engineer',
    'eng_consultant': '-> Consultant',
    'eng_support': '-> Support Engineer',
    'eng_test': '-> Test/QA/SDET',
    'eng_management': 'Engineering Management',
    'tech_lead': '-> Tech Lead',
    'eng_manager': '-> Engineering Manager',
    'delivery_manager': '-> Delivery Manager',
    'product': 'Product Program Management',
    'product_manager': '-> Product Manager',
    'program_manager': '-> Program Manager',
    'tpm': '-> TPM',
    'product_owner': '-> Product Owner',
    'project_manager': '-> Project Manager',
    'product_marketing_manager': '-> Product Marketing Manager',
    'business_analyst': '-> Business Analyst',
    'design': 'Design',
    'designer': '-> Designer',
    'ux_designer': '-> UX Designer',
    'user_researcher': '-> User Researcher',
    'data_science': 'Data Science',
    'data_scientist': '-> Data Scientist',
    'data_analyst': '-> Data Analyst',
    'quant_analyst': '-> Quant Analyst',
    'ops': 'Operations',
    'dev_advocacy': 'Developer Advocacy',
    'dev_advocate': '-> Developer Advocate',
    'tech_evangelist': '-> Technical Evangelist',
    'tech_writer': '-> Technical Writer',
    'sales': 'Sales Related',
    'tech_sales': '-> Sales',
    'tech_account_manager': '-> Account Manager',
    'tech_customer_success_manager': '-> Customer Success Manager',
    'recruiter': 'Recruitment',
    'tech_recruiter': '-> Tech Recruiter',
    'tech_sourcer': '-> Tech Sourcer',
    'exec_recruiter': '-> Executive Recruiter',
    'exec': 'Executive',
    'other': 'Other'
}

seniority_map = {
    "intern-level": "Intern",
    "entry-level": "Entry-level",
    "mid-level": "Mid-level",
    "senior": "Senior"
}


def url_to_filepaths(url):
    dir_path_split = url.split("europe/")[1].split("/")
    dir_path = "/".join(dir_path_split)
    file_name = url.split("/")[-1]
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    return dir_path, file_name


@st.cache_data
def load_and_parse(url):
    print(f"Downloading {url}")
    try:
        request = requests.get(url)
        # split request.text on the string "COMPENSATION_LIST"
        request_split = request.text.split("COMPENSATION_LIST = ")[
            1].split("</script>")[0].replace("'", "\"")
        # parse the string as JSON
        request_split = request_split.replace("'", "\"")
        request_split = request_split.split("\n")
        for index, line in enumerate(request_split):
            if line.strip().startswith("{"):
                continue
            if line.strip().startswith("}"):
                continue
            if line.strip().startswith("["):
                continue
            if line.strip().startswith("]"):
                continue
            if len(line.strip()) == 0:
                continue
            line_split = line.strip().split(":")
            line_split[0] = "\"" + line_split[0] + "\""
            line = ":".join(line_split)
            request_split[index] = line
        request_split = request_split[:-1]
        request_split[-2] = "}"
        request_split[-1] = "]"
        request_split = "\n".join(request_split)
        json_data = json.loads(request_split)

        json_formatted_str = json.dumps(json_data, indent=2)
        with open('techpays.json', 'w') as f:
            f.write(json_formatted_str)

        return json_data
    except Exception as e:
        with st.sidebar:
            st.error("Uh oh")
        st.error('Something went wrong when retrieving the data!', icon="🚨")
        exit(e)


def add_extra_compensation(df):
    df["extraCompensation"] = df["totalCompensationNumber"] - df["baseSalaryNumber"]


def st_basesalary_histogram(df, compensation_type):
    st.header(format_compensation_type(compensation_type) + " distribution")
    fig = px.histogram(df, x=compensation_type,
                       nbins=100, height=300)
    st.plotly_chart(fig, use_container_width=True,
                    config={'displayModeBar': False})


def st_best_paying_companies(df, filters, compensation_type):
    with st.sidebar:
        st.header("Data described")
        st.caption(
            "Total compensation is the sum of salary, bonus, equity and benefits")
        st.write(df.describe())
        st_basesalary_histogram(df, compensation_type)
        st.header("Boxplot settings")
        sort_highest = st.toggle('Sort by highest paying', value=True)
        n_companies = st.slider('Number of companies', 5, 150, 20, 5)
        min_entries = st.slider('Minimum entries', 2, 50, 10, 2)

    df = df[df.groupby('companyName')[
        'companyName'].transform('count') >= min_entries]

    if df.empty:
        st.warning(
            """No results, try lowering minimum entries or
            removing some filters""", icon="⚠️")
        return

    median_salaries = df.groupby(
        'companyName')[compensation_type].median()
    top_companies = median_salaries.sort_values(
        ascending=not sort_highest).head(n_companies).index

    filtered_df = df[df['companyName'].isin(top_companies)]
    order = list(filtered_df.groupby('companyName')[
        compensation_type].median().
        sort_values(ascending=not sort_highest).index)
    order.reverse()

    unique_companies = len(filtered_df['companyName'].unique())
    fig = px.box(filtered_df, x=compensation_type,
                 y="companyName",
                 points="all",
                 width=800,
                 height=400 + 20 * unique_companies)
    fig.update_yaxes(categoryorder='array', categoryarray=order)
    st.plotly_chart(fig, use_container_width=True)


def build_url(country, seniority, job_category):
    url = "https://techpays.eu/europe/" + country
    if seniority is not None:
        url += "/" + seniority
    if job_category is not None:
        url += "/" + job_category
    return url


def format_country(country):
    return country.replace('-', ' ').title()


def format_seniority(seniority):
    return seniority_map.get(seniority, seniority)


def format_job_category(job_category):
    return "All" if job_category is None else job_categories[job_category]


def init():
    st.set_page_config(page_title="Techpays Explorer",
                       page_icon="🖥️", layout="wide")

    with open('styles.css', 'r') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    if 'first_run' not in st.session_state:
        st.session_state['first_run'] = True


def init_sidebar():
    with st.sidebar:
        st.title("Techpays Explorer")
        st.caption(
            "Data from [Techpays.eu](https://techpays.eu) | Built by [Merlijn](https://linkedin.com/in/merlijnvanengelen)")
        st.caption("Scroll down for more settings")


def switch_first_run():
    st.session_state['first_run'] = False if st.session_state['first_run'] else True


def show_intro():
    _, col2, _ = st.columns(3)

    with col2:
        with st.container(border=True):
            st.subheader("Tech compensation in Europe is a taboo.")
            st.title("Let's change this.")
            st.markdown("""
                **The same role can pay 2-4x more at different companies in tech.** However, it's extremely hard to tell which companies pay more, and which pay less.
                        
                This site has been built as an addition to Techpays.eu, and adds the ability to explore the data in a more visual way. 
            """)
            st.markdown(
                "First things first, if you haven't already, contribute by adding your salary on [techpays.eu](https://techpays.eu)!")
        col11, col12 = st.columns(2)
        with col11:
            st.link_button("Contribute at techpays.eu", "https://techpays.eu")
        with col12:
            st.button("Explore the data", on_click=switch_first_run)
        st.divider()
        st.write(
            "Built by [Merlijn](https://linkedin.com/in/merlijnvanengelen)")


def format_compensation_type(compensation_type):
    if compensation_type == "totalCompensationNumber":
        return "Total compensation"
    if compensation_type == "baseSalaryNumber":
        return "Base salary only"
    if compensation_type == "extraCompensation":
        return "Extra compensation only"


def explore():
    st.subheader("Best paying companies")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        compensation_type = st.selectbox(
            'Compensation type',
            ('totalCompensationNumber', 'baseSalaryNumber', 'extraCompensation'),
            format_func=format_compensation_type,
        )
    with col2:
        country = st.selectbox(
            'Country',
            (
                'netherlands',
                'belgium',
                'estonia',
                'germany',
                'luxembourg',
                'hungary',
                'united-kingdom',
            ), format_func=format_country)
    with col3:
        seniority = st.selectbox(
            'Seniority',
            ('intern-level', 'entry-level', 'mid-level', 'senior'),
            format_func=format_seniority,
            index=None,
        )
    with col4:
        job_category = st.selectbox(
            'Job category',
            tuple(job_categories.keys()),
            format_func=format_job_category,
            index=None,)

    url = build_url(country, seniority, job_category)
    compensation_list = load_and_parse(url)

    if compensation_list is None:
        st.warning('There are no salaries matching these filters', icon="⚠️")
    else:
        df = pd.DataFrame(compensation_list)
        add_extra_compensation(df)
        st_best_paying_companies(
            df, (country, seniority, job_category), compensation_type)


def main():
    init()

    if st.session_state['first_run']:
        show_intro()
    else:
        init_sidebar()
        explore()


if __name__ == '__main__':
    main()
