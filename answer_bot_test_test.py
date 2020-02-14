import cv2
import pytesseract
import os
import requests
from bs4 import BeautifulSoup
import multiprocessing
import wx
import pyscreenshot as Imagegrab

# PATH
DOMAIN = "https://www.google.it/search?oe=utf8&ie=utf8&source=uds&start=0&hl=it&q="
INDICE = 1
N_DOMANDA = 0

Debug = True

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
LEFT_QUESTION = 40
RIGHT_QUESTION = 1035
QUESTION_TOP = 430
QUESTION_BOTTOM = 630

LEFT_OPTION = 106
RIGHT_OPTION = 1040
OPTION_HEIGHT = 190
ROW_HEIGHT = 36

OPTION_POSITION = [700, 930, 1050]


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

    sum_option_1 = (((result_list[0][0][1])*2) + result_list[0][1][1])
    sum_option_2 = (((result_list[1][0][1])*2) + result_list[1][1][1])
    sum_option_3 = (((result_list[2][0][1])*2) + result_list[2][1][1])

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
            print(result_list[x][0][0], end=' ')
            print(colors.END + colors.BOLD, end='')
            print("{ punti: " + "%d" % sum_option[x] + " }\n")
            print(colors.END, end='')
        else:
            print(colors.BOLD + "   • ", end='')
            print(result_list[x][0][0], end=' ')
            print("{ punti: " + "%d" % sum_option[x] + " }\n")
    print("-----------------------------------------------------------------------")

def get_number_of_results(data):
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
    # Create query
    query1 = DOMAIN + (question_text + ' ' + option_text + ' ' + 'wiki').replace(' ', '+')
    query2 = DOMAIN + (question_text + ' ' + option_text).replace(' ', '+')
    urls = [query1, query2]
    results_option = []
    # Perform request and read results
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        results = soup.find('div',{'id':'resultStats'}).text.split()[1].replace('.', '')
        results_option.append((option_text, int(results)))
        if Debug:
            print(url)
            print(results_option)
    return results_option

def manage_question():
    global N_DOMANDA
    if Debug:
        image = cv2.imread(r"C:\Users\Gabriele\Desktop\LiveQuiz - Bot\screen-domande\13.png", cv2.IMREAD_GRAYSCALE)
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

        print("\n" + str(++INDICE) + ". " + colors.YELLOW + colors.UNDERLINE + question_text + colors.STOP_UNDERLINE + colors.END + "\n")

        for i in range(0, 3):
            data.append((options, OPTION_POSITION[i], row_count, question_text))

        try:
            result_list = pool.map(get_number_of_results, data)

            if Debug:
                print()
                print(result_list)

            print_results(result_list, negative)
        except:
            print("\n" + colors.RED + colors.BOLD + "The query produced no result." + colors.YELLOW + " Please try again." + colors.END)

if __name__ == "__main__":
    os.system("")
    while True:
        key = input(colors.BOLD + "\nPress " + colors.BOLD + colors.GREEN + "ENTER" + colors.END + colors.BOLD + " to take a screenshot" + " of the question or press " + colors.BOLD + colors.RED + "q" + colors.END + colors.BOLD + " to quit: ")
        if not key:
            if Debug:
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