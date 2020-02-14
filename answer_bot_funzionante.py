import cv2
import pytesseract
import os
import requests
from bs4 import BeautifulSoup
import multiprocessing
import wx
import pyscreenshot as Imagegrab

""" QUESITO 3 RIGHE:

# SCREEN CONSTANTS
LEFT_QUESTION = 40
RIGHT_QUESTION = 1035
QUESTION_TOP = 500
QUESTION_BOTTOM = 760

LEFT_OPTION = 106
RIGHT_OPTION = 970
OPTION_HEIGHT = 190
ROW_HEIGHT = 36

OPTION_POSITION = [800, 1082, 1274]
"""

""" QUESITO 2 RIGHE:
# SCREEN CONSTANTS
LEFT_QUESTION = 40
RIGHT_QUESTION = 1035
QUESTION_TOP = 500
QUESTION_BOTTOM = 760

LEFT_OPTION = 106
RIGHT_OPTION = 970
OPTION_HEIGHT = 190
ROW_HEIGHT = 36

OPTION_POSITION = [800, 1021, 1274]
"""

# PATH
SCREENSHOT = "screenshot.png"
DOMAIN = "https://www.google.it/search?q="
INDICE = 0

# COLORS
class colors:
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# SCREEN CONSTANTS
LEFT_QUESTION = 40
RIGHT_QUESTION = 1035
QUESTION_TOP = 500
QUESTION_BOTTOM = 760

LEFT_OPTION = 106
RIGHT_OPTION = 970
OPTION_HEIGHT = 190
ROW_HEIGHT = 36

OPTION_POSITION = [800, 1021, 1274]


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
    query = DOMAIN + (question_text + ' ' + option_text + ' ' + 'wiki').replace(' ', '+')
    #print(query)
    # Perform request and read results
    r = requests.get(query)
    soup = BeautifulSoup(r.text, 'lxml')
    results = soup.find('div',{'id':'resultStats'}).text.split()[1].replace('.', '')
    #print(int(results))
    return option_text, int(results)

def print_results(result_list, negative):
    total = sum(n for _, n in result_list)
    if negative:
        guess = min(result_list, key=lambda x:x[1])
    else:
        guess = max(result_list, key=lambda x:x[1])
    for result in result_list:
        if result == guess:
            print(colors.GREEN + colors.BOLD, end='')
        print(result[0], end=' ')
        if result == guess:
            if negative:
                print(colors.END + colors.BOLD, end='')
            else:
                print(colors.END + colors.BOLD, end='')
        #print(result[1])
        print("{ " + "%.2f%%" % ((result[1] / total) * 100) + " }\n")
        if result == guess:
            print(colors.END, end='')
    print("-----------------------------------------------------------------------")

def manage_question():
    # Import image and remove screenshot from directory
    image = cv2.imread(SCREENSHOT, cv2.IMREAD_GRAYSCALE)
    os.remove(SCREENSHOT)
    # Threshold images for OCR
    ret, question = cv2.threshold(image[QUESTION_TOP:QUESTION_BOTTOM,
        LEFT_QUESTION:RIGHT_QUESTION], 200, 255, cv2.THRESH_BINARY_INV)
    ret, options = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
    # Read question text (determining number of rows)
    question_text = pytesseract.image_to_string(question, lang='ita')
    if not question_text:
        print(colors.RED + colors.BOLD + "Something went wrong reading the screenshot!"
                + colors.YELLOW + " Please try again." + colors.END)
    else:
        global INDICE
        INDICE = INDICE + 1
        negative = "NON" in question_text
        row_count = question_text.count('\n')
        question_text = question_text.replace('\n', ' ')
        print("\n" + str(INDICE) + ". " + colors.YELLOW + colors.UNDERLINE + question_text + colors.END + "\n")
        # Get number of results of each option in parallel
        pool = multiprocessing.Pool(processes=3)
        data = []
        for i in range(0, 3):
            data.append((options, OPTION_POSITION[i], row_count, question_text))
        try:
            result_list = pool.map(get_number_of_results, data)
            # Print results
            #print(result_list)
            print_results(result_list, negative)
        except:
            print("\n")
            print(colors.RED + colors.BOLD + "The query produced no result."
                    + colors.YELLOW + " Please try again." + colors.END)

if __name__ == "__main__":
    os.system("")
    while True:
        key = input(colors.BOLD + "\nPress " + colors.BOLD + colors.GREEN + "ENTER" + colors.END + colors.BOLD + " to take a screenshot" +
                " of the question or press " + colors.BOLD + colors.RED + "q" + colors.END + colors.BOLD + " to quit: ")
        if not key:
            print()
            ret = os.system(r"%USERPROFILE%\AppData\Local\Android\sdk\platform-tools\adb exec-out screencap -p > " + SCREENSHOT)
            if ret == 0:
                manage_question()
            else:
                print(colors.BOLD + colors.YELLOW + "Please check your USB connection" + colors.END)
        elif key == 'q':
            break