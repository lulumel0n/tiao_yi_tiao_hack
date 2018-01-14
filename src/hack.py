from subprocess import call
import cv2
from matplotlib import pyplot as plt
import numpy as np
import time
import math

chessman_base_color = [102, 59, 55]

# scan line for next block
# left <-
#cv2.line(cur_img, (0, 1300), (1080, 650), (255, 0, 0), 1)

# rignt ->
#cv2.line(cur_img, (0, 650), (1080, 1300), (0, 255, 0), 1)

# Return the base location
def chessman_loc(cur_img):	
	candidate = np.empty([6, 2])
	index = 0

	for i in range(1000, 1250):
		for j in range(0, 1080):
			if np.array_equal(cur_img[i, j], chessman_base_color):
				candidate[index] = [i, j]
				index+=1

				if (index == 6):
					break
		if (index == 6):
			break

	candidate = np.resize(candidate, (index, 2))

	loc = np.mean(candidate, dtype = int, axis = 0)

	return (loc[1], loc[0])


# function: y = a * x + b
# 
def get_next_block_position(cur_img, direction, a, b):

	x = 0

	feature_ptrs = []

	ymax, xmax, layer = cur_img.shape

	if (direction == 'l'):
	
		prev = (b, 3)

		for x in range(3, xmax):
			y = int(a * x + b)

			cur = (y, x)

			ad = cv2.absdiff(cur_img[cur[0], cur[1]], cur_img[prev[0], prev[1]])

			if (np.sum(ad) > 15):
				# print (ad)
				# print (str(cur[0]) + '  ' + str(cur[1]))
				# print (cur_img[cur[0], cur[1]])
				feature_ptrs.append((cur[1], cur[0]))

			prev = cur


		first_block = feature_ptrs[0]

		cv2.circle(cur_img, (first_block[0], first_block[1]), 10, [0, 33, 250], thickness = 2)

	else:
		
		prev = (b, xmax - 1)

		for x in range((xmax - 6), 4, -1):
			y = int(a * x + b)

			cur = (y, x)
			ad = cv2.absdiff(cur_img[cur[0], cur[1]], cur_img[prev[0], prev[1]])

			if (np.sum(ad) > 15):
				# print (ad)
				# print (str(cur[0]) + '  ' + str(cur[1]))
				# print (cur_img[cur[0], cur[1]])
				feature_ptrs.append((cur[1], cur[0]))


			prev = cur

		first_block = feature_ptrs[1]

		cv2.circle(cur_img, (first_block[0], first_block[1]), 10, [0, 33, 250], thickness = 2)



	for ct in feature_ptrs:
		cv2.circle(cur_img, (ct[0], ct[1]), 5, [0, 0, 200], thickness = 2)


	return first_block



def main():

	# call(["/Users/Admin_Magix/Library/Android/sdk/platform-tools/adb", "shell", "screencap", "-p", "/sdcard/screencap.png"])

	# call(["/Users/Admin_Magix/Library/Android/sdk/platform-tools/adb", "pull", "/sdcard/screencap.png"]) 
	call(["/Users/Admin_Magix/Library/Android/sdk/platform-tools/adb", "shell", "screencap", "-p", "/sdcard/screencap.png"])
	call(["/Users/Admin_Magix/Library/Android/sdk/platform-tools/adb", "pull", "/sdcard/screencap.png"]) 

	cur_img = cv2.imread('screencap.png', cv2.IMREAD_COLOR)


#	cv2.line(cur_img, (0, 1300), (1080, 650), (255, 0, 0), 3)

#	cv2.line(cur_img, (0, 650), (1080, 1300), (255, 255, 0), 3)


#	plt.imshow(cur_img)

	# print (chessman_coordinator)
	# print (chessman_coordinator[0])

#	plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis

	#cncncn = plt.imshow(cv2.cvtColor(cur_img, cv2.COLOR_BGR2RGB))
		

	height, width, depth = cur_img.shape


	while (True):

		# get screenshoot
		call(["/Users/Admin_Magix/Library/Android/sdk/platform-tools/adb", "shell", "screencap", "-p", "/sdcard/screencap.png"])
		call(["/Users/Admin_Magix/Library/Android/sdk/platform-tools/adb", "pull", "/sdcard/screencap.png"]) 

		# update most recent screen
		cur_img = cv2.imread('screencap.png', cv2.IMREAD_COLOR)

		chessman_coordinator = chessman_loc(cur_img)


		# determine l2r or r2l
		# l2r
		if (chessman_coordinator[0] < width // 2):
			print('zai left')
			next_loc = get_next_block_position(cur_img, 'r', -0.602, 1300)
		# r2l
		else:
			print('zai right')
			next_loc = get_next_block_position(cur_img, 'l', 0.602, 650)

		cv2.circle(cur_img, chessman_coordinator, 5, [0, 0, 250], thickness = 5)


		cv2.line(cur_img, next_loc, chessman_coordinator, (255, 0, 0), 5)


	#	dist = plt.mlab.dist(next_loc, chessman_coordinator)

		dist = ((next_loc[0] - chessman_coordinator[0]) ** 2) +  ((next_loc[1] - chessman_coordinator[1]) ** 2)
		dist = math.sqrt(dist)

		print("Distance: " + str(dist))


		#cncncn.set_data(cur_img)

		plt.show(block = False)


		# plt.imshow(cv2.cvtColor(cur_img, cv2.COLOR_BGR2RGB))

		# plt.imshow(cv2.cvtColor(cur_img, cv2.COLOR_BGR2RGB))
		
		# plt.show()

		#cv2.namedWindow('image', cv2.WINDOW_NORMAL)


		cv2.line(cur_img, (0, 1300), (1080, 650), (255, 0, 0), 1)

		cv2.line(cur_img, (0, 650), (1080, 1300), (0, 255, 0), 1)

		cur_img = cv2.resize(cur_img, (432, 768))                    # Resize image

		cv2.imshow('image', cur_img)


		# tuning

		if (dist < 500):
			dist = dist * 1.04
		elif (dist > 600):
			dist = dist * 1.15
		else:
			dist = dist * 1.1

		cv2.waitKey(1)

		call(["/Users/Admin_Magix/Library/Android/sdk/platform-tools/adb", "shell", "input", "swipe", "100", "500", "100", "500", str(int(dist))])

		time.sleep(4)



	# cv2.namedWindow('image', cv2.WINDOW_NORMAL)

	# cv2.imshow('image', cur_img)

	# cv2.waitKey(0)

	# cv2.destroyAllWindows()





if __name__ == "__main__":
	main()