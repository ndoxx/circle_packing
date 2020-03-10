#!/usr/bin/python3

from graphics import *
import random, sys
from pyqtree import Index

def euclidean_distance_2(r1, r2):
	return (r1.x - r2.x)*(r1.x - r2.x) + (r1.y - r2.y)*(r1.y - r2.y)


def inversive_distance(r1, r2, R1, R2):
	return (euclidean_distance_2(r1, r2) - R1*R1 - R2*R2)/(2*R1*R2)


def collide_circles(r1, r2, R1, R2):
	return inversive_distance(r1, r2, R1, R2) < 1


def point_in_circle(p, r, R):
	return euclidean_distance_2(p, r) < R*R


def point_in_any_circle(p, circles):
	for circle in circles:
		if point_in_circle(p, circle.getCenter(), circle.radius):
			return True
	return False


def collide_circle_screen(r, R, w, h):
	return (r.x-R < 0) or (r.x+R > w) or (r.y-R < 0) or (r.y+R > h)


def collide_circle_any(r, R, circles, w, h):
	if collide_circle_screen(r, R, w, h):
		return True
	for circle in circles:
		if collide_circles(r, circle.getCenter(), R, circle.radius):
			return True
	return False


def put_pixels(center, p, pixels):
	pixels.add((int(center.x+p.x), int(center.y+p.y)))
	pixels.add((int(center.x-p.x), int(center.y+p.y)))
	pixels.add((int(center.x+p.x), int(center.y-p.y)))
	pixels.add((int(center.x-p.x), int(center.y-p.y)))
	pixels.add((int(center.x+p.y), int(center.y+p.x)))
	pixels.add((int(center.x-p.y), int(center.y+p.x)))
	pixels.add((int(center.x+p.y), int(center.y-p.x)))
	pixels.add((int(center.x-p.y), int(center.y-p.x)))
  

# Bresenham's algorithm for circle generation
def bresenham(center, r):
	x = 0
	y = r
	d = 3 - 2 * r
	pixels = set()
	put_pixels(center, Point(x, y), pixels)
	while y >= x:
		x += 1
		if d > 0:
			y -= 1 
			d = d + 4 * (x - y) + 10
		else:
			d = d + 4 * x + 6
		put_pixels(center, Point(x, y), pixels)
	return pixels


def collide_circle_mask(r, R, image):
	# Obtain list of pixels along circle
	pixels = bresenham(r, R)
	w = image.getWidth()
	h = image.getHeight()
	for pixel in pixels:
		x = pixel[0]
		y = h-pixel[1]
		if x>=0 and x<w and y>=0 and y<h:
			if image.getPixel(x,y)[0] == 0:
				return False
		else:
			return False
	return True


def point_in_mask(p, image):
	w = image.getWidth()
	h = image.getHeight()
	x = int(p.x)
	y = int(h-p.y)
	if x>=0 and x<w and y>=0 and y<h:
		return image.getPixel(x,y)[0] > 0
	return False


def get_bbox(center, radius):
	return [center.x-radius, center.y-radius, center.x+radius, center.y+radius]


def clear_screen(win,W,H):
	rect = Rectangle(Point(0,0), Point(W,H))
	rect.setFill("black")
	rect.draw(win)


def main():
	seed = random.randrange(sys.maxsize)
	rng = random.Random(seed)
	print("Using seed: ", seed)

	# Load mask and colored image
	mask = Image(Point(0,0), "res/ok_mask.png")
	W = mask.getWidth()
	H = mask.getHeight()
	mask = Image(Point(W/2,H/2), "res/ok_mask.png")
	image = Image(Point(W/2,H/2), "res/ok_color.png")

	step = 1
	win = GraphWin('CPack', W, H)
	win.setCoords(0,0,W,H)

	# Initialize quadtree
	spindex = Index(bbox=(0,0,W,H))

	# Clear screen
	clear_screen(win,W,H)
	# mask.draw(win)

	attempts = 0
	while attempts < 10000:
		# Select random point in screen
		center = Point(random.randint(0,W-1), random.randint(0,H-1))
		radius = step
		# Make sure initial center is valid
		matches = spindex.intersect(get_bbox(center, radius))
		while point_in_any_circle(center, matches) or not point_in_mask(center, mask):
			center = Point(random.randint(0,W-1), random.randint(0,H-1))
			matches = spindex.intersect(get_bbox(center, radius))
		# Get circles in the direct vicinity
		matches = spindex.intersect(get_bbox(center, radius+step))
		# Grow circle till it collides with screen or another circle
		while not collide_circle_any(center, radius+step, matches, W, H) and collide_circle_mask(center, radius+step, mask):
			radius += step
			matches = spindex.intersect(get_bbox(center, radius))
		# Get rid of circle if too small
		if radius > 2*step:
			circle = Circle(center, radius)
			color = image.getPixel(int(center.x), int(H-center.y))
			circle.setFill(color_rgb(color[0],color[1],color[2]))
			circle.draw(win)
			# Add circle to quadtree
			spindex.insert(circle, get_bbox(center, radius))
		attempts += 1

	win.getMouse()
	win.close()


if __name__ == '__main__':
	main()