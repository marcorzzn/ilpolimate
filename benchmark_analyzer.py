import timeit
from bs4 import BeautifulSoup

# Setup for analyzer.py test
html_content = ""
for i in range(100):
    html_content += f'<div class="news-item">Content {i}</div>\n'
soup = BeautifulSoup(html_content, "html.parser")

def original_analyzer():
    clean_html = ""
    for item in soup.find_all('div', class_='news-item', recursive=False):
        clean_html += str(item) + "\n"
    return clean_html

def optimized_analyzer_append_join():
    clean_html_parts = []
    for item in soup.find_all('div', class_='news-item', recursive=False):
        clean_html_parts.append(str(item) + "\n")
    return "".join(clean_html_parts)

def optimized_analyzer_list_comp():
    return "".join([f"{item}\n" for item in soup.find_all('div', class_='news-item', recursive=False)])

if __name__ == "__main__":
    n = 1000

    t_orig_a = timeit.timeit(original_analyzer, number=n)
    t_opt_a = timeit.timeit(optimized_analyzer_append_join, number=n)
    t_opt_l = timeit.timeit(optimized_analyzer_list_comp, number=n)
    print("Analyzer baseline (+):", t_orig_a)
    print("Analyzer append+join:", t_opt_a)
    print("Analyzer list comp  :", t_opt_l)
    print(f"Improvement (append+join): {(t_orig_a - t_opt_a)/t_orig_a*100:.2f}%")
    print(f"Improvement (list comp)  : {(t_orig_a - t_opt_l)/t_orig_a*100:.2f}%")
