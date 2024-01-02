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


def write_stats(df, url):
    dir_path, file_name = url_to_filepaths(url)

    print("Writing stats...")
    df.describe().to_csv(dir_path+"/"+file_name+".csv")
    with open(dir_path+"/"+file_name+".txt", "w") as f:
        f.write(df.describe().to_string())
    print("Done")


def make_histogram(df, url):
    print("Making histogram...")

    sns.histplot(df['baseSalaryNumber'], bins=25)
    plt.title(url.split("https://")[1])
    plt.xlabel("Salary")
    plt.ylabel("Frequency")

    dir_path, file_name = url_to_filepaths(url)
    plt.savefig(dir_path+"/"+file_name)
    print("Done")


def main():
    url = "https://techpays.eu/europe/netherlands"

    print("Downloading...")
    compensation_list = load_and_parse(url)
    print("Done")

    df = pd.DataFrame(compensation_list)

    make_histogram(df, url)
    write_stats(df, url)


if __name__ == '__main__':
    main()
