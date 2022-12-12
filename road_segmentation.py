#With dilated image , number of iterations=1
#If using skeletanization, number of iterations =3
# Road region extraction using Thresholding

import cv2
# import matplotlib.pyplot as plt
import numpy as np
# import time
# image_BGR = cv2.imread(r'D:\MWS\original_dataset\no_marker\MicrosoftTeams-image (7).png')
# image_BGR = cv2.imread(r'D:\MWS\original_dataset\no_marker\churchRoad - Copy.png')
# # image_BGR = cv2.imread(r'D:\MWS\original_dataset\no_marker\AlbanyParkImage.png')
# image_BGR = cv2.imread(r'D:\MWS\original_dataset\no_marker\albanyPark_17jan.png')

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


def road_segmenation_func(image_filename):
    image_BGR = cv2.imread(image_filename)
    image =cv2.cvtColor(image_BGR, cv2.COLOR_BGR2RGB)
    Manual=1
    # image_g = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # im_thresh = cv2.threshold(image_g, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


    center_coordinate_y = int(image_BGR.shape[0]/2)+20

    center_coordinate_x = int(image_BGR.shape[1]/2)

    # print("Image Shape:", image.shape, "Point of interest: ",center_coordinate_y, center_coordinate_x)

    # plt.imshow(image)
    # plt.show()

    #Convert the img to HSV and threshold to extract road region

    hsv_image = cv2.cvtColor(image_BGR, cv2.COLOR_BGR2HSV)

    # Grey colour road
    low_greybou = np.array([0, 0, 255])
    high_greybou = np.array([255, 255, 255])
    grey_mask = cv2.inRange(hsv_image, low_greybou, high_greybou)

    greybou = cv2.cvtColor(cv2.bitwise_and(image_BGR, image_BGR, mask=grey_mask), cv2.COLOR_HSV2RGB)

    grey_image = cv2.cvtColor(greybou, cv2.COLOR_RGB2GRAY)
    thresh = cv2.threshold(grey_image, 10, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # dilated=thresh
    # dilated = cv2.dilate(thresh, None, iterations= 3)#6,7,8 Original images 
    dilated = cv2.dilate(thresh, None, iterations= 7)
    # dilated = cv2.threshold(dilated, 10, 255, cv2.THRESH_BINARY)[1]
    # plt.imshow(dilated, cmap="gray")
    # plt.show()
    # Alternative skeletonization 
    def skeletonize(img):
        element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
        done = False
        size = np.size(img)
        skel = np.zeros(img.shape,np.uint8)
        while( not done):
            eroded = cv2.erode(img,element)
            temp = cv2.dilate(eroded,element)
            temp = cv2.subtract(img,temp)
            skel = cv2.bitwise_or(skel,temp)
            img = eroded.copy()

            zeros = size - cv2.countNonZero(img)
            if zeros==size:
                done = True
        return skel
    # dilated = cv2.threshold(dilated, 128, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)
    skel = skeletonize(dilated)

    # plt.imshow(skel, cmap="gray")
    # plt.show()

    ####IF skeletonization not used, substitute edges=dilated
    def FindPoint(x1, y1, x2,
                  y2, x, y) :
        # function returns true if the point(x,y) lies within the rectangular region (x1,y1,x2,y2)
        if (x > x1-5 and x < x2+5 and
            y > y1-5 and y < y2+5) :
            return True
        else :
            return False
    # Apply edge detection method on the image
    edges = skel#dilated
    mask = np.zeros(edges.shape, dtype="uint8")
    output = cv2.connectedComponentsWithStats(edges)
    (numLabels, labels, stats, centroids) = output
    output = image.copy()
    counter=0
    # print("Min and max area:", stats[:, cv2.CC_STAT_AREA].min(), stats[:, cv2.CC_STAT_AREA].max())
    for i in range(1, numLabels):
        # if this is the first component then we examine the
        # *background* (typically we would just ignore this
        # component in our loop)
        if i == 0:
            text = "examining component {}/{} (background)".format(
                i + 1, numLabels)
        # otherwise, we are examining an actual connected component
        else:
            text = "examining component {}/{}".format( i + 1, numLabels)
        # print a status message update for the current connected
        # component
    # 	print("[INFO] {}".format(text))
        # extract the connected component statistics and centroid for
        # the current label
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        (cX, cY) = centroids[i]
        if FindPoint(x,y,x+w,y+h, center_coordinate_x, center_coordinate_y):#and stats[i, cv2.CC_STAT_AREA] <= 1747:
                cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 5)
    #         	print(labels[i], stats[i], centroids[i])
                Manual=0
                counter+=1
                componentMask = (labels == i).astype("uint8") * 255
                mask = cv2.bitwise_or(mask, componentMask)
                # print(stats[i, cv2.CC_STAT_AREA])
        
        
    if Manual==0:
        cv2.circle(output, (center_coordinate_x, center_coordinate_y), 20, 2)
        # plt.imshow(output)
        # plt.show()
        # plt.imshow(mask, cmap='gray')
        # plt.show()
        # print(np.sum(mask==0))

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        result = cv2.dilate(mask, kernel)

        contours,hierarchy = cv2.findContours(result, 1, 2)
        # cnt = contours[0]
        markers = np.ones(image.shape, dtype=np.int32)*255
        for i in range(len(contours)):
            # print(i)
            cv2.drawContours(image, contours,0,(0,0,255), -1)
        # fig, ax = plt.subplots(figsize=(7, 7))
        # ax.imshow(image)

        # ax.axis([0, img.shape[1], img.shape[0], 0])
        # print(len(contours[0]))
        # plt.show()
        # Find Bounding Rectangle
        rect = cv2.minAreaRect(contours[0])
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        temp=[]
        for b in box:
            temp =  temp+[[b[0],b[1]]]

        cv2.drawContours(image,[box],0,(255,0,0),2)
        # fig, ax = plt.subplots(figsize=(7, 7))
        # ax.imshow(image)
        # plt.show()
        finalbbox = origin_adjusted_bbox(temp,(-120,-123))
        return finalbbox
    else:
        print("Error Message: Need to do manually")
        return None
#####################

# image_BGR = cv2.imread(r'D:\MWS\original_dataset\no_marker\MicrosoftTeams-image (7).png')
# image_BGR = cv2.imread(r'D:\MWS\original_dataset\no_marker\churchRoad - Copy.png')
# # image_BGR = cv2.imread(r'D:\MWS\original_dataset\no_marker\AlbanyParkImage.png')
# image_BGR = cv2.imread(r'D:\MWS\original_dataset\no_marker\albanyPark_17jan.png')
# road_bounding_box = road_segmenation_func(r'D:\MWS\original_dataset\no_marker\AlbanyParkImage.png')
# road_bounding_box = road_segmenation_func(r'D:\MWS\original_dataset\no_marker\AlbanyParkImage.png')
# remove_lines(r'D:\MWS\original_dataset\no_marker\churchRoad - Copy.png')
# t1 = time.time()

# total_n = t1-t0
# print("The segmented road boundary:", road_bounding_box)
# print(". It took", total_n, " seconds to run the code:")