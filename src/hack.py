from subprocess import call
import cv2
from matplotlib import pyplot as plt
import numpy as np
import time
import math
import queue
import util
import random

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
def get_next_block_position(cur_img, direction, a, b):
	feature_ptrs = []
	ymax, xmax, layer = cur_img.shape

	if (direction == 'l'):
		prev = (int(a * 1 + b), 2)

		for x in range(3, xmax):
			y = int(a * x + b)
			cur = (y, x)
			ad = cv2.absdiff(cur_img[cur[0], cur[1]], cur_img[prev[0], prev[1]])
			if (np.sum(ad) > 20):
				feature_ptrs.append((cur[1], cur[0]))

			prev = cur

		first_block = feature_ptrs[0]

	else:
		prev = (int(a * (xmax - 1) + b), xmax - 1)

		for x in range((xmax - 6), 4, -2):
			y = int(a * x + b)
			cur = (y, x)
			ad = cv2.absdiff(cur_img[cur[0], cur[1]], cur_img[prev[0], prev[1]])
			if (np.sum(ad) > 20):
				feature_ptrs.append((cur[1], cur[0]))

			prev = cur

		first_block = feature_ptrs[0]

	return first_block

# bfs to find surface of block and get the center
def get_block_center(cur_img, root, direction):
	q = queue.Queue()
	visited = set()

	croot = (root[1], root[0])

	q.put(croot)

	original_color = np.array([0, 1, 2], dtype='uint8')

	original_color[0] = cur_img[croot[0], croot[1], 0]
	original_color[1] = cur_img[croot[0], croot[1], 1]
	original_color[2] = cur_img[croot[0], croot[1], 2]

	print("block base color: " + str(original_color))

	step = 3

	threshold_right_down = 15
	threshold_left_up = 15

	top_upper = (1950, 0)
	right_most = (0, 0)

	while q.qsize() > 0:
		cur = q.get()
		
		if cur_img[cur[0], cur[1], 0] == 0 and cur_img[cur[0], cur[1], 1] == 255  and cur_img[cur[0], cur[1], 2] == 0:
			continue

		if (cur[0] < top_upper[0]):
			top_upper = cur

		if (cur[1] > right_most[1]):
			right_most = cur

		cur_img[cur[0], cur[1]] = [0, 255, 0]

		ad = cv2.absdiff(original_color, cur_img[cur[0] - step, cur[1]])
		if (np.sum(ad) < threshold_left_up):
			q.put((cur[0] - step, cur[1]))

		ad = cv2.absdiff(original_color, cur_img[cur[0], cur[1] + step])
		if (np.sum(ad) < threshold_right_down):
			q.put((cur[0], cur[1] + step))

		ad = cv2.absdiff(original_color, cur_img[cur[0], cur[1] - step])
		if (np.sum(ad) < threshold_left_up):
			q.put((cur[0], cur[1] - step))

		ad = cv2.absdiff(original_color, cur_img[cur[0] + step, cur[1]])
		if (np.sum(ad) < threshold_right_down):
			q.put((cur[0] + step, cur[1]))

	cv2.circle(cur_img, (right_most[1], right_most[0]), 5, [0, 0, 250], thickness = 4)
	cv2.circle(cur_img, (top_upper[1], top_upper[0]), 5, [0, 250, 0], thickness = 2)
	top_right_dist = ((right_most[0] - top_upper[0]) ** 2) +  ((right_most[1] - top_upper[1]) ** 2)

	if top_right_dist < 200:
		print("cannot find center, using approx center")

		if (direction == 'r'):
			return (top_upper[0] + 40, top_upper[1] - 60)
		else:
			return (top_upper[0] + 40 , top_upper[1] + 60)

	else:
		intersect = util.line_intersection([[ right_most[0], right_most[1] ],[  right_most[0] ,  right_most[1] -200 ]] ,   [ [top_upper[0], top_upper[1] ], [     top_upper[0] + 100, top_upper[1]      ] ] )
		intersect = (int(intersect[0]), int(intersect[1]))
		return intersect

def main():
	# get initial screenshoot
	call(["adb", "shell", "screencap", "-p", "/sdcard/screencap.png"])
	call(["adb", "pull", "/sdcard/screencap.png"]) 

	cur_img = cv2.imread('screencap.png', cv2.IMREAD_COLOR)

	height, width, depth = cur_img.shape
	level = 0

	# mainloop
	while (True):
		print("* * * " + str(level) + " * * *")
		# get current screenshoot
		call(["adb", "shell", "screencap", "-p", "/sdcard/screencap.png"])
		call(["adb", "pull", "/sdcard/screencap.png"]) 

		# update most recent screen
		cur_img = cv2.imread('screencap.png', cv2.IMREAD_COLOR)

		chessman_coordinator = chessman_loc(cur_img)

		print("chessman location: " + str(chessman_coordinator))

		# determine l2r or r2l
		# l2r
		if (chessman_coordinator[0] < width // 2):
			print('jump from left -> right')
			next_loc = get_next_block_position(cur_img, 'r', -0.602, 1300)
			next_block_ctr = get_block_center(cur_img, next_loc, 'r')
		# r2l
		else:
			print('jump from right -> left')
			next_loc = get_next_block_position(cur_img, 'l', 0.602, 650)
			next_block_ctr = get_block_center(cur_img, next_loc, 'l')

		next_block_ctr = (next_block_ctr[1], next_block_ctr[0])

		# draw chessman location
		cv2.circle(cur_img, next_block_ctr, 5, [0, 7, 190], thickness = 5)

		# draw target location
		cv2.circle(cur_img, chessman_coordinator, 5, [0, 0, 250], thickness = 5)

		# draw start to end line
		cv2.line(cur_img, next_block_ctr, chessman_coordinator, (255, 0, 0), 5)


		dist = ((next_block_ctr[0] - chessman_coordinator[0]) ** 2) +  ((next_block_ctr[1] - chessman_coordinator[1]) ** 2)
		dist = math.sqrt(dist)

		# reszie image
		cur_img = cv2.resize(cur_img, (432, 768))
		cv2.imshow('image', cur_img)
		cv2.waitKey(1)

		cv2.imwrite("last_jump.png", cur_img)

		print("distance: " + str(dist))
		dist *= 1.35
		dist = int(dist)
		print("normalized distance: " + str(dist))

		level+=1

		# random click position
		x = str(random.randint(400, 500))
		y = str(random.randint(500, 600))

		# mimic click
		call(["adb", "shell", "input", "swipe", x, y, x, y, str(dist)])

		time.sleep(4)

if __name__ == "__main__":
	main()