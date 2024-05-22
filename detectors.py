from imutils import contours
import numpy as np
import imutils
import cv2
from PIL import Image, ImageOps
import utils
import os


def findFullAnswerSheet(img, width, height):
    _, countours = utils.getContours(img,minArea=300000)
    points_test_paper = utils.get_4_contour(countours[0][2])
    return utils.wrapImage(img, points_test_paper, width, height)


def get_listen_test_image(image):
    height, width, channels = image.shape
    padding = 0.00886739218057235 * width
    per_width = [0.12615880693268844, 0.5030229746070133]
    per_height = (0.153363740022805, 0.47063854047890535)
    return image[int(per_height[0]*height):int(per_height[1]*height),\
                 int(per_width[0]*width+padding):int(per_width[1]*width-padding)]


def get_reading_test_image(image):
    height, width, channels = image.shape
    padding_left = 0.012494961708988311 * width
    padding_right = 0.004433696090286175 * width
    per_width = [0.5171301894397421, 0.8935912938331319]
    per_height = (0.153363740022805, 0.47063854047890535)
    return image[int(per_height[0]*height):int(per_height[1]*height),\
                 int(per_width[0]*width+padding_left):int(per_width[1]*width-padding_right)]


def get_columns(image, n_col=4, width=2481):
    lst = []
    padding = int(0.008464328899637243*width)
    w = int(round(image.shape[1]/4))
    for i in range(n_col):
        sheet = image[:,w*i:w*(i+1)]
        img = sheet[:, padding:(sheet.shape[1]-padding)]
        lst.append(img)
    return lst


def get_my_ans(image_ans, ANSWER_KEY, draw_img, index_sheet = 0, type_test = "listening", thresh_value = 100, limit_value = 240):
    translate = {"A": 0, "B": 1, "C": 2, "D": 3}
    revert_translate = {0: "A", 1: "B", 2: "C", 3: "D", -1: "N"}
    img = image_ans.copy()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Remove border
    kernel = np.ones((5,5))
    imgDilation = cv2.dilate(blur, kernel, iterations = 2)
    # Zoom in filled color
    erosion = cv2.erode(imgDilation, kernel, iterations = 2)
    # Convert to binary (under 100 convert to 0, otherwise 1)
    _, thresh = cv2.threshold(erosion, thresh_value, 255, cv2.THRESH_BINARY)
    
    ans_char = ['A','B','C','D']
    my_answers = []
    
    height_each_ans = int(round(img.shape[0]/25))
    width_each_ans = int(round(img.shape[1]/4))
    
    n_questions = 25
    for i in range(n_questions):
        row_1_ans = thresh[height_each_ans*i:height_each_ans*(i+1), : ]
        min_mean = float('inf')
        selected_ans = None
        
        for j in range(4):
            mean_value = np.mean(row_1_ans[:, width_each_ans*j : width_each_ans*(j+1)])
            if mean_value < limit_value and mean_value < min_mean:
                min_mean = mean_value
                selected_ans = ans_char[j]
        if selected_ans is not None:
            my_answers.append(selected_ans)
        else:
            my_answers.append("-")
    
    r = 17
    start_h = 538
    padding = 42.25
    if type_test == "listening":
        start_w = int(357 + index_sheet*image_ans.shape[1] + padding*index_sheet)
    else:  # reading
        start_w = int(1283+52.25+ index_sheet*image_ans.shape[1] + padding*index_sheet)
    
    for quest in range(n_questions):
        I_y = int(round(start_h + height_each_ans*(quest*0.99+0.5)))
        x_each_quest = (image_ans.shape[1]/4)
        I_x_key = start_w + int(x_each_quest*translate[ANSWER_KEY[quest]])+(image_ans.shape[1]/4)//2
        if my_answers[quest] == '-':
            cv2.circle(draw_img, (int(I_x_key), int(I_y)), r, (255, 0, 0), 3)
            continue
            
        I_x_my_ans = start_w + int(x_each_quest*translate[my_answers[quest]])+(image_ans.shape[1]/4)//2
        if my_answers[quest] == ANSWER_KEY[quest]:
            cv2.circle(draw_img, (int(I_x_my_ans), int(I_y)), r, (0, 255, 0), 3)
        else: 
            cv2.circle(draw_img, (int(I_x_my_ans), int(I_y)), r, (0, 0, 255), 3)
            cv2.circle(draw_img, (int(I_x_key), int(I_y)), r, (255, 0, 0), 3)
    return np.array(my_answers)
