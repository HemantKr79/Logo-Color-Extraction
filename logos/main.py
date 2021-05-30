from flask import Flask,jsonify,request
import urllib
import numpy as np
from matplotlib import pyplot as plt
import cv2
from colormap import rgb2hex

app = Flask(__name__)

#function for converting color space BGR -> RGB (cv2 reads image in BGR format)
def cvtColor(img):
    h,w = img.shape[0],img.shape[1]
    for i in range(h):
        for j in range(w):
            img[i][j][0],img[i][j][2] = img[i][j][2],img[i][j][0]
    return img

#function to load images
def load_img(name):
    img = cv2.imread(name,cv2.IMREAD_UNCHANGED)
    img = cvtColor(img)
    return img

#this function find the frequency of each color and returns the color having highest frequency
def get_dominant_color(img):
    channels = img.shape[-1]
    img = img.reshape((-1,channels))
    colors = np.unique(img,return_counts=True,axis=0)
    index1 = 0
    val1 = -1
    val2 = 0
    index2 = 0
    for i in range(len(colors[1])):
        if colors[1][i] > val1:
            val2 = val1
            index2 = index1
            index1 = i
            val1 = colors[1][i]
        elif colors[1][i] > val2:
            val2 = colors[1][i]
            index2 = i    
    most_dominant = colors[0][index1]
    second_most_dominant = colors[0][index2]
    return most_dominant,second_most_dominant

def get_border_color(img,border_width=5):
    border = []

    h,w = img.shape[0],img.shape[1]
    border_width = 5
    channels = img.shape[2]
    
    #storing all the colors present in the image border
    #the color with heightest frequency will be the color of the border
    for j in range(0,w,border_width):
        portion = img[0:border_width,j:j+border_width]
        portion = portion.reshape((-1,channels))
        border.append(portion)

    for j in range(0,w,border_width):
        portion = img[h-border_width:h,j:j+border_width]
        portion = portion.reshape((-1,channels))
        border.append(portion)

    for i in range(border_width,h-border_width,border_width):
        portion = img[i:i+border_width,0:border_width]
        portion = portion.reshape((-1,channels))
        border.append(portion)

    for i in range(border_width,h-border_width,border_width):
        portion = img[i:i+border_width,w-border_width:w]
        portion = portion.reshape((-1,channels))
        border.append(portion)
    
    #border is initially list of lists, so converting it into a single list
    border = [item for sublist in border for item in sublist]
    border = np.array(border)
    border_color = get_dominant_color(border)[0]
    return border_color

def get_primary_color(img,border_color):
    most_dominant,second_most_dominant = get_dominant_color(img)
    primary_color = most_dominant
    channels = img.shape[-1]
    #if border color and most dominant colors are same it means that boarder takes most of the space in image
    #so the primary color of the logo will be the second most dominant color
    if primary_color[0]==border_color[0] and primary_color[1]==border_color[1] and primary_color[2]==border_color[2]:
        #checking the 4th channel (in png images)
        if channels==4:
            if primary_color[3]==border_color[3]:
                primary_color = second_most_dominant
        else:
            primary_color = second_most_dominant
    return primary_color

@app.route('/')
def my_main_function():
	link = request.args.get('src')
	if link is None:
		return "Welcome"
	img_name = link.split('/')[-1]
	for i in range(len(link)):
		if link[i]==' ':
			link = link[:i] + "%20" + link[i+1:]
	try:
		urllib.request.urlretrieve(link,img_name)
	except:
		return "some error occured"
	img = load_img(img_name)
	border_color = get_border_color(img,1)
	primary_color = get_primary_color(img,border_color)
	my_result = {
		'logo_border': str(rgb2hex(border_color[0],border_color[1],border_color[2])),
		'dominant_color': str(rgb2hex(primary_color[0],primary_color[1],primary_color[2]))
	}
	return jsonify(my_result)

if __name__ == "__main__":
	app.run(debug=True)