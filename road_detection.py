# Code to find end points of the street 
# Input: cropped map image from RPA bot
# Output: Bounding box coordinates (4 points) for the street

# The steps involved:
# 1)Read the map image sent by RPA bot, check its shape and find the center point
# 2)Detect the roads using White colour threshold
# 3)Detect the straight lines using HoughLinesP
# 4)Find the nearest distance road - get endpoints
# 5)Find the bounding box coordinates - shift the origin and get final bounding box coordinates

# -------------------------- xxx ------------------------------------------------------ 

# Do necessary imports
from shapely.geometry import LineString
import numpy as np
import cv2

# -------------------------- xxx ------------------------------------------------------ 
# Argument Parser

# import argparse
# ap = argparse.ArgumentParser()

# ap.add_argument("-f","--filename_map", required=True,
#     help="name of the map image, eg. albanypark.png")
# ap.add_argument("-r","--rootdir", required=True,
#     help="root directory name, eg. .")

# args = vars(ap.parse_args())

# filename_map = args["filename_map"]
# Root_directory_name = args["rootdir"]

# -------------------------- xxx ------------------------------------------------------ 

# Define necessary functions


# Input: Line segment endpoints [x1,y1,x2,y2]
# Output: Coordinates of 4 vertices of the bounding box
def bbox(line_endpoints, width=10):
  x1,y1,x2,y2 = line_endpoints
  a = (x1,y1)
  b = (x2,y2)
  cd_length = width

  ab = LineString([a,b]) # Original Line segment
  left = ab.parallel_offset(cd_length / 2, 'left') # One Parallel line above at width/2 distance
  right = ab.parallel_offset(cd_length / 2, 'right') # One Parallel line below at width/2 distance
  # These are the bbox coordinates = endpoints of the parallel lines
  c = left.boundary[1]
  d = right.boundary[0]  # note the different orientation for right offset
  e = right.boundary[1]
  f = left.boundary[0]

  bbox = [(int(c.x),int(c.y)),(int(d.x), int(d.y)),(int(e.x),int(e.y)),(int(f.x),int(f.y))]
  return bbox

def origin_adjusted_bbox(bbox, shift):
    newbbox = []
    for i in range(len(bbox)):
        newpoint =[0,0]
        newpoint[0] = bbox[i][0] + shift[0]
        newpoint[1] = bbox[i][1] + shift[1]
        # print("This is new Point",newpoint)
        newbbox.append(newpoint)
        # print("This is new bbox", newbbox)
    return newbbox

def perp_dist(point, linep1, linep2):
  p1 = np.array(linep1)
  p2 = np.array(linep2)
  p3 = np.array(point)
  d=abs(np.cross(p2-p1,p3-p1)/np.linalg.norm(p2-p1))
  # print("Distance is ",d)
  return d

def dist2points(point_a, point_b):
  # a = np.array((1, 2, 3))
  # b = np.array((4, 5, 6))
  a = np.array(point_a)
  b = np.array(point_b)
  dist = np.linalg.norm(a-b)
  # print(dist)
  return dist

# -------------------------- xxx ------------------------------------------------------ 


# MAIN PROGRAM ************************************************************************




def street_endpoints(filepath):

    # Step 1) Read map image and find center point

    # filepath = Root_directory_name+'/'+filename_map
    print("Filepath is ",filepath)
    map_img = cv2.imread(filepath)
    center = (int(map_img.shape[1]/2), int(map_img.shape[0]/2)+14)


    # -------------------------- xxx ------------------------------------------------------ 

    # Step 2) Detect Roads using Threshold: White color

    img = map_img
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # White color
    low_white = np.array([0, 0, 255])
    high_white = np.array([255, 255, 255])

    white_mask = cv2.inRange(hsv_img, low_white, high_white)
    white = cv2.bitwise_and(img, img, mask=white_mask)

    print("Roads Detected")

    # -------------------------- xxx ------------------------------------------------------ 

    # Step 3) Find straight lines using HoughLinesP

    img = white
    # Convert the img to grayscale
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)  
    # Apply edge detection method on the image
    edges = cv2.Canny(gray,100,200,apertureSize = 3)
      
    # This returns an array of r and theta values
    # lines = cv2.HoughLines(edges,1,np.pi/180, 200)
    minLineLength = 30
    maxLineGap = 14
    lines = cv2.HoughLinesP(edges,1,np.pi/180,15,minLineLength=minLineLength,maxLineGap=maxLineGap)

    print("Lines Detected")
    # -------------------------- xxx ------------------------------------------------------ 

    # Step 4) Find nearest road endpoints:

    nearby_lines_index = []
    point = center
    for x in range(0,len(lines)):
      for x1,y1,x2,y2 in lines[x]:
        # print("Line no. ",x," has distance ",perp_dist(point, [x1,y1], [x2,y2]))
        if ((perp_dist(point, [x1,y1], [x2,y2]))<10.0 and (dist2points(point,[x1,y1])<80 or dist2points(point, [x2,y2])<80)):
            # print("Line no. ",x," has neaby distance ",perp_dist(point, [x1,y1], [x2,y2]))
            nearby_lines_index.append(x)

    nearest_distances = []
    # x_counterindex = 0
    for x in nearby_lines_index:
      x1 = lines[x][0][0]
      y1 = lines[x][0][1]
      x2 = lines[x][0][2]
      y2 = lines[x][0][3]
      print("Line no.",x,"has nearby distance ",perp_dist(point, [x1,y1], [x2,y2])) 
      nearest_distances.append(perp_dist(point, [x1,y1], [x2,y2]))   
      # x_counterindex +=1

    def argmin(lst):
      return lst.index(min(lst))

    max_dist_x_index = argmin(nearest_distances)
    max_dist_x = nearby_lines_index[max_dist_x_index]
    print("This is the nearest line number ",max_dist_x )



    x1 = lines[max_dist_x][0][0]
    y1 = lines[max_dist_x][0][1]
    x2 = lines[max_dist_x][0][2]
    y2 = lines[max_dist_x][0][3]

    print("Nearest Line Found")
    
    # -------------------------- xxx ------------------------------------------------------ 

    # Step 5) Get the bbox -> final bbox coodinates

    bbox2 = bbox([x1,y1,x2,y2])
   
    finalbbox = origin_adjusted_bbox(bbox2,(-120,-123))

    print("Finished")
    return finalbbox

# finalbbox2 = street_endpoints(filepath)
# print("Final BBox coordinates are: ", finalbbox2)

