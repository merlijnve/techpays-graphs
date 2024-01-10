import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns


def url_to_filepaths(url):
    dir_path_split = url.split("europe/")[1].split("/")
    dir_path = "/".join(dir_path_split)
    file_name = url.split("/")[-1]
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    return dir_path, file_name


def load_and_parse(url):
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


def basesalary_stats(df, url):
    dir_path, file_name = url_to_filepaths(url)

    print("Writing stats...")
    df.describe().to_csv(dir_path+"/" + "baseSalary-" + file_name+".csv")
    with open(dir_path+"/" + "baseSalary-" + file_name+".txt", "w") as f:
        f.write(df.describe().to_string())


def basesalary_histogram(df, url):
    """
    Plot a histogram of base salaries.
    """
    print("Making histogram...")

    sns.histplot(df['baseSalaryNumber'], bins=25)
    plt.title(url.split("europe/")[1])
    plt.xlabel("Salary")
    plt.ylabel("Frequency")

    dir_path, file_name = url_to_filepaths(url)
    plt.savefig(dir_path+"/" + "baseSalary-" + file_name)

    basesalary_stats(df, url)


def write_best_paying_companies(df, url):
    """
    Write sorted best paying companies to file.
    """
    dir_path, file_name = url_to_filepaths(url)

    stats = df.groupby(['companyName'])[
        'baseSalaryNumber'].agg(['mean', 'median', 'count']).sort_values(by=['median'], ascending=False)
    stats.to_csv(dir_path+"/" + "bestPayingCompanies-" +
                 file_name+".csv")

    with open(dir_path+"/" + "bestPayingCompanies-" + file_name + ".txt", "w") as f:
        f.write(stats.to_string())


def best_paying_companies(df, url, min_entries=10, n_companies=40):
    """
    Plot a boxplot of the best paying companies.
    """
    print("Best paying companies...")
    dir_path, file_name = url_to_filepaths(url)

    df = df[df.groupby('companyName')[
        'companyName'].transform('count') >= min_entries]

    write_best_paying_companies(df, url)

    median_salaries = df.groupby(
        'companyName')['baseSalaryNumber'].median()
    top_companies = median_salaries.sort_values(
        ascending=False).head(n_companies).index

    filtered_df = df[df['companyName'].isin(top_companies)]
    order = filtered_df.groupby('companyName')[
        'baseSalaryNumber'].median().sort_values(ascending=False).index

    plt.figure(figsize=(12, 8))
    plt.subplots_adjust(left=0.2)
    sns.boxplot(
        filtered_df, x="baseSalaryNumber", y="companyName",
        width=.5, palette="vlag", order=order
    )
    sns.stripplot(filtered_df, x="baseSalaryNumber",
                  y="companyName", size=2, color=".3")
    plt.title(" Best paying companies in " +
              url.split("europe/")[1] + " (sorted by median, minimum of %d entries per company)" % min_entries)
    plt.savefig(dir_path+"/" + "bestPayingCompanies-" + file_name)
    plt.show()


def main():
    url = "https://techpays.eu/europe/netherlands"

    print("Downloading...")
    compensation_list = load_and_parse(url)

    df = pd.DataFrame(compensation_list)

    basesalary_histogram(df, url)
    best_paying_companies(df, url, min_entries=10)


if __name__ == '__main__':
    main()
