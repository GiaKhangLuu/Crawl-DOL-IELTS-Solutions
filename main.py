import asyncio
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

webpage = "https://tuhocielts.dolenglish.vn/luyen-thi-ielts/ielts-online-test-answer-key-cambridge-ielts-13-test-3-listening?questionNo={}"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()
    page.goto(webpage.format(17))

    html_content = page.content()

    soup = BeautifulSoup(html_content, 'html.parser')
    explanation = soup.find('div', 'ant-card-body')

    if explanation:

        # Find all <img> elements within the div
        img_eles = explanation.find_all('img')

        # Find <img> elements with "alt" attribute set to "cross" and "check"
        cross_images = soup.find_all('img', alt='cross')
        check_images = soup.find_all('img', alt='check')

        for cross_img in cross_images:
            cross_img.replace_with(soup.new_tag('<i class="fas fa-check" style="color: #19d76b;"></i>'))

        # Convert the element to a string
        explanation_string = str(explanation)

        # Define the file name and open it in write mode
        with open('output.html', 'w', encoding='utf-8') as file:
            # Write the div content to the HTML file
            file.write(explanation_string)
        print('Saved')
    else:
        print('Cant find explanation section')
    # wait for 1 second
    page.wait_for_timeout(1000)

    #page.screenshot(path="example.png")
    browser.close()
