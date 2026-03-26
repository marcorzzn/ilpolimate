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

def optimized_analyzer_list_comp():
    return "".join(f"{item}\n" for item in soup.find_all('div', class_='news-item', recursive=False))

# Setup for generator.py test
clusters_content = {f"Cluster {i}": f"Content {i}" for i in range(100)}

def original_generator():
    md = '\n<div class="feed-section">\n<div class="feed-grid">\n'
    for cluster_name, content in clusters_content.items():
        if content:
            md += f"\n<div class=\"feed-cluster\">\n<div class=\"cluster-header\">{cluster_name}</div>\n\n{content}\n</div>\n"
    md += '\n</div>\n</div>\n'
    return md

def optimized_generator():
    parts = ['\n<div class="feed-section">\n<div class="feed-grid">\n']
    for cluster_name, content in clusters_content.items():
        if content:
            parts.append(f"\n<div class=\"feed-cluster\">\n<div class=\"cluster-header\">{cluster_name}</div>\n\n{content}\n</div>\n")
    parts.append('\n</div>\n</div>\n')
    return "".join(parts)

if __name__ == "__main__":
    n = 1000

    t_orig_a = timeit.timeit(original_analyzer, number=n)
    t_opt_a = timeit.timeit(optimized_analyzer_list_comp, number=n)
    print("Analyzer baseline (+):", t_orig_a)
    print("Analyzer optimized (list comp):", t_opt_a)
    print(f"Improvement: {(t_orig_a - t_opt_a)/t_orig_a*100:.2f}%\n")

    t_orig_g = timeit.timeit(original_generator, number=n)
    t_opt_g = timeit.timeit(optimized_generator, number=n)
    print("Generator baseline (+):", t_orig_g)
    print("Generator optimized (join):", t_opt_g)
    print(f"Improvement: {(t_orig_g - t_opt_g)/t_orig_g*100:.2f}%")
