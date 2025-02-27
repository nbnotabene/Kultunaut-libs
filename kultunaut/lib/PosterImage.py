import io
import math
import sys
import numpy as np
from PIL import Image
import requests, os

class PosterImage:

   def __init__(self, path,url):
      self.PATH = path
      self.url=url
      self.posterPath=f"{self.PATH}/poster.jpg"
      self.posterMini=f"{self.PATH}/posterMini.jpg"

      if self.savePoster():
         #im = Image.open('/home/nb/proj/bio_sqlite/out/17356648/poster.jpg')
         self.__JPEGSaveWithTargetSize()
      #else posterimage exists!

   def savePoster(self):
      rval=True      
      if not os.path.isfile(self.posterPath):
         response = requests.get(self.url)
         if response.status_code == 200:
            with open(self.posterPath, 'wb') as f:
               f.write(response.content)              
         else:
            rval=False
      else: #Poster File Exists
         if os.path.isfile(self.posterMini):
            rval=False
      return rval
   

   def __JPEGSaveWithTargetSize(self):
      """Save the image as JPEG with the given name at best quality that makes less than "target" bytes"""
      # Min and Max quality
      im=Image.open(self.posterPath)
      target=100000

      newtarget = target
      while newtarget<target*20:
         Qmin, Qmax = 25, 90   
         # Highest acceptable quality found
         Qacc = -1
         while Qmin <= Qmax:
            m = math.floor((Qmin + Qmax) / 2)

            # Encode into memory and get size
            buffer = io.BytesIO()
            im.save(buffer, format="JPEG", quality=m)
            s = buffer.getbuffer().nbytes

            if s <= newtarget:
               Qacc = m
               Qmin = m + 1
            elif s > newtarget:
               Qmax = m - 1

         # Write to disk at the defined quality
         if Qacc > -1:
            im.save(self.posterMini, format="JPEG", quality=Qacc)
            return True
         else:
            newtarget = newtarget+target
            #print("ERROR: No acceptble quality factor found", file=sys.stderr)

      print("ERROR: No acceptble quality factor found", file=sys.stderr)

if __name__ == '__main__':
   pass
   
   
   # Save at best quality under 100,000 bytes
   #JPEGSaveWithTargetSize(im, "/home/nb/proj/bio_sqlite/out/17356648/result.jpg", 100000)
