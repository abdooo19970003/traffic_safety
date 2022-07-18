import cv2
import time
import math
import numpy as np

limit = 80          # km/hour 


file = open('H://graduated project//speed//speedRecord.txt','w')
file.write("ID \t  SPEED \n ------ \t ------ \n")
file.close()


class EuclideanDistTracker:
    def __init__(self):
        #  store the center positions of the objects 
        self.center_points = {}

        self.id_count = 0
        # self.start = 0
        # self.stop = 0
        self.et = 0
        self.s1 = np.zeros((1,1000))
        self.s2 = np.zeros((1,1000))
        self.s = np.zeros((1,1000))
        self.f = np.zeros(1000)
        self.capf = np.zeros(1000)
        self.count = 0
        self.exceeded = 0
        
    def update(self, object_rect):
        object_bbs_ids = []

        # get center point of new object 
        for rect in object_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2
            
            # check if object is detected already 
            same_object_detected = False
            
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])
                
                if dist < 70 :
                    self.center_points[id] = (cx, cy)
                    object_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                    
                    # START TIMER
                    if (y >= 410 and y <= 430) :
                        self.s1[0, id] = time.time()
                    
                    # STOP TIMER & FIND DIFFERENCE33
                    if y >= 235 and y <= 255:
                        self.s2[0, id] = time.time()
                        self.s[0,id] = self.s2[0, id] - self.s1[0, id]
                        
                    # CAPTURE FLAGE
                    if y < 235 :
                        self.f[id] = 1
                    
            # new object detection 
            if same_object_detected is False:
                self.center_points[self.id_count] = (cx, cy)
                object_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1
                self.s[0, self.id_count] = 0
                self.s1[0, self.id_count] = 0
                self.s2[0, self.id_count] = 0
        
        
        # assign new ID to object
        new_center_points = {}
        for obj_bb_id in object_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center
        
        self.center_points = new_center_points.copy()
        return object_bbs_ids
    
    
    # Speed Function
    def getspeed(self, id):
        if self.s[0, id] != 0:
            s = 75.05 / self.s[0, id]
        else:
            s = 0

        return int(s)
    
    # save vehicle DATA 
    def capture(self, img, x, y, h, w, sp, id):
        if self.capf[id] == 0 :
            self.capf[id] =1
            self.f[id] = 0
            crop_img = img[y-5:y + h+5, x-5 : x + w+5]
            n = str(id) + "_SPEED_" + str(sp)
            file = 'H://graduated project//speed//captured//'+ n +'.jpg'
            cv2.imwrite(file, crop_img) 
            self.count += 1
            filet = open('H://graduated project//speed//speedRecord.txt','a')
            if sp > limit:
                file2 = 'H://graduated project//speed//exceeded//' + n + '.jpg'
                cv2.imwrite(file2, crop_img)
                filet.write(str(id) + ' \t' + str(sp) + '<---exceeded\n')
                self.exceeded += 1
            else:
                filet.write(str(id) + ' \t' + str(sp) + '\n')
            filet.close()
    
    
    # speed limit
    def limit(self):
        return(limit)
    
    # text file summary
    def end(self):
        file = open('H://graduated project//speed//speedRecord.txt','a')
        file.write('\n --------------------\n')
        file.write('--------------------\n')
        file.write('SUMMARY\n')
        file.write('--------------------\n')
        file.write('Total Vehicles : \t ' + str(self.count) + '\n')
        file.write('Exceeded speed limit :\t' + str(self.exceeded) + '\n')
        file.close()

