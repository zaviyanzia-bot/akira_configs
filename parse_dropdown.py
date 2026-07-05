from bs4 import BeautifulSoup

def parse():
    with open('body_dropdown.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    print('=== Searching for elements containing ratio text ===')
    # Print elements that contain 9:16 or 16:9 or 1:1 or are select options
    for tag in ['div', 'span', 'p', 'button', 'li', 'a', 'option']:
        elements = soup.find_all(tag)
        for el in elements:
            text = (el.text or '').strip()
            # print if text matches ratio formats
            if text in ['9:16', '16:9', '1:1', '4:3', '3:4', '2:3', 'Ratio', 'ratio'] or any(r in text for r in ['9:16', '16:9']):
                if len(el.find_all()) < 5:
                    print(f'<{tag} class="{el.get("class")}" id="{el.get("id")}">{text}</{tag}>')

if __name__ == "__main__":
    parse()
