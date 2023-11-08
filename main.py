import asyncio
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os 
from tqdm import tqdm

webpage = "https://tuhocielts.dolenglish.vn/luyen-thi-ielts/ielts-online-test-answer-key-cambridge-ielts-{cam_no}-test-{test_no}-{skill}?questionNo={question_no}"
check_icon = {'class': 'fa fa-solid fa-circle-check fa-lg', 'style': 'color: #048b26'}
cross_icon = {'class': "fa fa-solid fa-circle-xmark fa-lg", 'style': "color: #f30f0f"}
robot_icon = {'class': "fas fa-robot fa-spin", 'style': "color: #2e6ddc"}
redundant_eles = [{'tag': 'div', 'attrs': {'class': 'header-locate-passage'}},
                  {'tag': 'button', 'attrs': None},
                  {'tag': 'div', 'attrs': {'class': "ResponsiveContainer-sc-1h7phak-0 czDzEq"}}]
font_awesome_cdn = {'rel': 'stylesheet',
                    'href': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css',
                    'integrity': 'sha512-z3gLpd7yknf1YoNbCzqRKc4qyor8gaKU1qmn+CShxbuBusANI9QpRohGBreCFkKxLhei6S9CQXFEbbKuqLg0DA==',
                    'crossorigin': 'anonymous',
                    'referrerpolicy': 'no-referrer'}

cambridge_books = [10, 11, 12, 13, 14, 15, 16]
num_tests = 4
num_questions = 40
skills = ['listening', 'reading']

def crawl_data(question, cam, test, skill):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(webpage.format(question_no=question, cam_no=cam, test_no=test, skill=skill))

        html_content = page.content()
        page.wait_for_timeout(1000)
        browser.close()

    soup = BeautifulSoup(html_content, 'html.parser')
    explanation = soup.find('div', 'section-explanation')

    replace_with_check_icon = lambda x: x.replace_with(soup.new_tag('i', attrs=check_icon))
    replace_with_cross_icon = lambda x: x.replace_with(soup.new_tag('i', attrs=cross_icon))
    replace_with_robot_icon = lambda x: x.replace_with(soup.new_tag('i', attrs=robot_icon))

    # Simplifying HTML
    for redundant_ele in redundant_eles:
        tag, attrs = redundant_ele['tag'], redundant_ele['attrs']
        if attrs:
            remove_items = soup.find_all(tag, attrs=attrs)
        else:
            remove_items = soup.find_all(tag)
        for remove_item in remove_items:
            remove_item.decompose()

    # Add font_awesome_cdn
    new_head = soup.new_tag('head')
    font_awesome_link = soup.new_tag('link', attrs=font_awesome_cdn)
    new_head.append(font_awesome_link)

    explanation.insert(0, new_head)

    if explanation:

        # Replacing cross and check <img>  with cross and check icons
        cross_images = soup.find_all('img', alt='cross')
        check_images = soup.find_all('img', alt='check')
        if len(check_images):
            list(map(replace_with_check_icon, check_images))
        if len(cross_images):
            list(map(replace_with_cross_icon, cross_images))

        # Replacing others <img> with robot icon
        img_eles = explanation.find_all('img')
        if len(img_eles):
            list(map(replace_with_robot_icon, img_eles))

        # Convert the element to a string
        explanation_string = str(explanation)

        return explanation_string

    return None

# Create directories for each book
for cam_book in cambridge_books:
    book_folder = f"Cambridge_{cam_book:02}"  # Format book number with leading zeros
    if not os.path.exists(book_folder):
        os.mkdir(book_folder)

    # Create subfolders for each skill
    for skill in skills:
        skill_folder = os.path.join(book_folder, skill)
        if not os.path.exists(skill_folder):
            os.mkdir(skill_folder)

        # Create subfolders for tests
        for test_num in range(1, num_tests + 1):
            test_folder = os.path.join(skill_folder, f"test_{test_num:02}")
            if not os.path.exists(test_folder):
                os.mkdir(test_folder)

            # Create files for questions
            for question_num in range(1, num_questions + 1):
                question_filename = os.path.join(test_folder, f"question_{question_num:02}.html")

                # Starting to crawl
                html_text = crawl_data(question_num, cam_book, test_num, skill)
                
                if html_text:
                    with open(question_filename, 'w', encoding='utf-8') as file:
                        file.write(html_text)
    
                    print('Done cam {} test {} {} question {}'.format(cam_book, test_num, skill, question_num))

