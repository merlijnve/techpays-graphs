## Techpays.eu scraping and visualization
#### All credits go to [Gergely Orosz](https://github.com/gergelyorosz) for building [techpays.eu](https://techpays.eu)

### Usage:
1. Install requirements with `pip install -r requirements.txt`
2. Copy a url from techpays.eu to the program to use the filters (country, location, seniority, etc)
3. Run the program `python techpays.py`

If your specific filters don't give a lot of entries back and the boxplot doesn't have much companies, change min_entries in the main.

### What does it create?
- Best paying companies (by base salary) boxplot 
- Base salary histogram
- Base salary describe files: (min, max, mean, median, etc) in csv and (more human readable) txt

The files are put in a folder structure which copies the url, for example `netherlands/amsterdam/entry-level/entry-level.png`


### Best paying companies
<img width="1126" alt="Screenshot 2024-01-10 at 16 54 04" src="https://github.com/merlijnve/techpays-graphs/assets/20463804/00afd5dd-00ea-4fef-b15f-45692f50eb33">



### Base salary histogram
![netherlands](https://github.com/merlijnve/techpays-graphs/assets/20463804/c9a11bd9-33d4-4995-993a-553e2b349696)

### Base salary Describe
```
       totalCompensationNumber  baseSalaryNumber
count              3852.000000       3852.000000
mean              92103.901869      79132.516874
std               51774.682228      32031.588999
min                1200.000000        115.000000
25%               62000.000000      60000.000000
50%               79500.000000      75000.000000
75%              109000.000000      93000.000000
max              830000.000000     325000.000000
```
