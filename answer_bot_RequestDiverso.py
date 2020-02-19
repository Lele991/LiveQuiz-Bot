import cv2
import pytesseract
import os
import requests
from bs4 import BeautifulSoup
import multiprocessing
import wx
import pyscreenshot as Imagegrab

headers_Get = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# PATH
DOMAIN = "https://www.google.it/search?oe=utf8&ie=utf8&source=uds&start=0&hl=it&q="
INDICE = 1
N_DOMANDA = 0

Debug = False
Test = True

# COLORS
class colors:
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    STOP_UNDERLINE = '\033[24m'
    END = '\033[0m'

# SCREEN CONSTANTS
LEFT_QUESTION = 30
RIGHT_QUESTION = 1035
QUESTION_TOP = 420
QUESTION_BOTTOM = 600

LEFT_OPTION = 80
RIGHT_OPTION = 970
OPTION_HEIGHT = 190
ROW_HEIGHT = 30

OPTION_POSITION = [600, 760, 925]

def get_option(data):
    image = data[0]
    position = data[1]
    row_count = data[2]
    question_text = data[3]
    # Crop image
    top = position + row_count * ROW_HEIGHT
    bottom = top + OPTION_HEIGHT
    option = image[top:bottom, LEFT_OPTION:RIGHT_OPTION]
    # Read option text
    option_text = pytesseract.image_to_string(option, lang='ita').replace('\n', ' ')
    option_list = []
    option_list.append(option_text)
    return option_list

def ricerca(question, option):
    s = requests.Session()

    # Create query
    query1 = DOMAIN + (question + ' ' + option + ' ' + 'wiki').replace(' ', '+')
    query2 = DOMAIN + (question + ' ' + option).replace(' ', '+')
    urls = [query1, query2]
    results_option = []
    results_option.append(option)

    for url in urls:
        r = s.get(url, headers=headers_Get, timeout=5)
        soup = BeautifulSoup(r.text, 'lxml')
        results = soup.find('div',{'id':'mBMHK'}).text.replace('Circa', '')
        results = results.split()[0].replace('.', '')
        results_option.append(int(results))

    return results_option

def maximum(a, b, c):
    if (a >= b) and (a >= c):
        largest = a
    elif (b >= a) and (b >= c):
        largest = b
    else:
        largest = c
    return largest

def minium(a, b, c):
    if (a <= b) and (a <= c):
        largest = a
    elif (b <= a) and (b <= c):
        largest = b
    else:
        largest = c
    return largest

def print_results(result_list, negative):
    x = -1

    sum_option_1 = (((result_list[0][1])*2) + result_list[0][2])
    sum_option_2 = (((result_list[1][1])*2) + result_list[1][2])
    sum_option_3 = (((result_list[2][1])*2) + result_list[2][2])

    sum_option = [sum_option_1, sum_option_2, sum_option_3]

    if Debug:
        print(sum_option_1)
        print(sum_option_2)
        print(sum_option_3)
        print(sum_option)

    if negative:
        guess = minium(sum_option_1, sum_option_2, sum_option_3)
    else:
        guess = maximum(sum_option_1, sum_option_2, sum_option_3)

    if Debug:
        print()
        print(guess)
        print("\n")

    for key in result_list:
        x = x + 1
        if guess == sum_option[x]:
            print(colors.BOLD + "   • ", end='')
            print(colors.GREEN + colors.BOLD, end='')
            print(result_list[x][0], end=' ')
            print(colors.END + colors.BOLD, end='')
            print("{ punti: " + "%d" % sum_option[x] + " }\n")
            print(colors.END, end='')
        else:
            print(colors.BOLD + "   • ", end='')
            print(result_list[x][0], end=' ')
            print("{ punti: " + "%d" % sum_option[x] + " }\n")
    print("-----------------------------------------------------------------------")

def manage_question():
    global N_DOMANDA
    if Test:
        image = cv2.imread("/Users/gabriele.peluzzi/Downloads/LiveQuizBot/test.png", cv2.IMREAD_GRAYSCALE)
    else:
        image = cv2.imread(SCREENSHOT, cv2.IMREAD_GRAYSCALE)
    ret, question = cv2.threshold(image[QUESTION_TOP:QUESTION_BOTTOM, LEFT_QUESTION:RIGHT_QUESTION], 200, 255, cv2.THRESH_BINARY_INV)
    ret, options = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
    question_text = pytesseract.image_to_string(question, lang='ita')

    if not question_text:
        print(colors.RED + colors.BOLD + "Something went wrong reading the screenshot!" + colors.YELLOW + " Please try again." + colors.END)
    else:
        global INDICE
        negative = "NON" in question_text
        row_count = question_text.count('\n')
        question_text = question_text.replace('\n', ' ')
        pool = multiprocessing.Pool(processes=3)
        data = []
        result_research = []

        print("\n" + str(++INDICE) + ". " + colors.YELLOW + colors.UNDERLINE + question_text + colors.STOP_UNDERLINE + colors.END + "\n")

        for i in range(0, 3):
            data.append((options, OPTION_POSITION[i], row_count, question_text))

        try:
            option_list = pool.map(get_option, data)

            if Debug:
                print(option_list)
            for i in range(0, 3):
                result_research.append(ricerca(question_text, option_list[i][0]))
            print_results(result_research, negative)
        except:
            print("\n" + colors.RED + colors.BOLD + "The query produced no result." + colors.YELLOW + " Please try again." + colors.END)

if __name__ == "__main__":
    os.system("")
    while True:
        key = input(colors.BOLD + "\nPress " + colors.BOLD + colors.GREEN + "ENTER" + colors.END + colors.BOLD + " to take a screenshot" + " of the question or press " + colors.BOLD + colors.RED + "q" + colors.END + colors.BOLD + " to quit: ")
        if not key:
            if Test:
                print()
                manage_question()
            else:
                print()
                N_DOMANDA = N_DOMANDA + 1
                SCREENSHOT = "screenshot-domanda-"+ str(N_DOMANDA) +".png"
                ret = os.system(r"%USERPROFILE%\AppData\Local\Android\sdk\platform-tools\adb exec-out screencap -p > " + SCREENSHOT)
                if ret == 0:
                    manage_question()
                else:
                    print(colors.BOLD + colors.YELLOW + "Please check your USB connection" + colors.END)
        elif key == 'q':
            break
