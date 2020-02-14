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
DOMAIN = "https://www.google.it/search?oe=utf8&ie=utf8&source=uds&start=0&hl=it&q="
INDICE = 0

Debug = False

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
QUESTION_TOP = 500
QUESTION_BOTTOM = 760

LEFT_OPTION = 106
RIGHT_OPTION = 970
OPTION_HEIGHT = 190
ROW_HEIGHT = 36

OPTION_POSITION = [800, 1021, 1274]


def get_number_of_results_1(data):
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
    #query = DOMAIN + (question_text + ' ' + option_text + ' ' + 'wiki&tbs=li:1').replace(' ', '+')
    query = DOMAIN + (question_text + ' ' + option_text + ' ' + 'wiki').replace(' ', '+')
    if Debug:
        print(query)
    # Perform request and read results
    r = requests.get(query)
    soup = BeautifulSoup(r.text, 'lxml')
    results = soup.find('div',{'id':'resultStats'}).text.split()[1].replace('.', '')
    #print(int(results))
    return option_text, int(results)
	
def get_number_of_results_2(data):
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
    #query = DOMAIN + (question_text + ' ' + option_text + '&tbs=li:1').replace(' ', '+')
    query = DOMAIN + (question_text + ' ' + option_text).replace(' ', '+')
    if Debug:
        print(query)
    # Perform request and read results
    r = requests.get(query)
    soup = BeautifulSoup(r.text, 'lxml')
    results = soup.find('div',{'id':'resultStats'}).text.split()[1].replace('.', '')
    #print(int(results))
    return option_text, int(results)
	
def maximum(a, b, c): 
    if (a >= b) and (a >= b): 
        largest = a 
    elif (b >= a) and (b >= a): 
        largest = b 
    else: 
        largest = c        
    return largest
	
def minium(a, b, c): 
    if (a <= b) and (a <= b): 
        largest = a 
    elif (b <= a) and (b <= a): 
        largest = b 
    else: 
        largest = c 
    return largest 

def print_results(result_list_1, result_list_2, negative):
    x = -1
    total_1 = sum(n_1 for _, n_1 in result_list_1)
    total_2 = sum(n_2 for _, n_2 in result_list_2)
	
    total = total_1 + total_2
	
    sum_option_1 = (((result_list_1[0][1])*2) + result_list_2[0][1])
    sum_option_2 = (((result_list_1[1][1])*2) + result_list_2[1][1])
    sum_option_3 = (((result_list_1[2][1])*2) + result_list_2[2][1])
	
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
	
    for key in result_list_1:
        x = x + 1
        if guess == sum_option[x]:
            print(colors.BOLD + "   • ", end='')
            print(colors.GREEN + colors.BOLD, end='')
            print(result_list_1[x][0], end=' ')
            print(colors.END + colors.BOLD, end='')
            print("{ punti: " + "%d" % sum_option[x] + " }\n")
            print(colors.END, end='')
        else:
            print(colors.BOLD + "   • ", end='')
            print(result_list_1[x][0], end=' ')
            print("{ punti: " + "%d" % sum_option[x] + " }\n")
    print("-----------------------------------------------------------------------")

def manage_question():
    # Import image and remove screenshot from directory
    image = cv2.imread(r"C:\Users\Gabriele\Desktop\Screenshots\3.png", cv2.IMREAD_GRAYSCALE)
    # os.remove(SCREENSHOT)
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
        print("\n" + str(INDICE) + ". " + colors.YELLOW + colors.UNDERLINE + question_text + colors.STOP_UNDERLINE + colors.END + "\n")
        # Get number of results of each option in parallel
        pool = multiprocessing.Pool(processes=3)
        data = []
        for i in range(0, 3):
            data.append((options, OPTION_POSITION[i], row_count, question_text))
        try:
            result_list_1 = pool.map(get_number_of_results_1, data)
            result_list_2 = pool.map(get_number_of_results_2, data)
            # Print results
            if Debug:
                print()
                print(result_list_1)
                print(result_list_2)
            print_results(result_list_1, result_list_2, negative)
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
            manage_question()
        elif key == 'q':
            break