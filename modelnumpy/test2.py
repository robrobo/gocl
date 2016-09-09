import math
from PIL import Image, ImageDraw
from tkinter import *
from PIL import Image, ImageTk
import time

class HexagonGenerator(object):
  """Returns a hexagon generator for hexagons of the specified size."""
  def __init__(self, edgeLength):
    self.edgeLength = edgeLength
    self.offsetX = 0
    self.offsetY = edgeLength/2
    

  def __call__(self, row, col):
    if row % 2 == 0:
        x = self.offsetX 
    else:
        x = self.offsetX + self.edgeLength * math.sqrt(3) /2
    y = self.offsetY 
    x += self.edgeLength * col * math.sqrt(3)
    y += self.edgeLength * 1.5 * row

        
        
        
    ret = []
    for angle in range(-30, 330, 60):
      x += math.cos(math.radians(angle)) * self.edgeLength
      y += math.sin(math.radians(angle)) * self.edgeLength
      ret.append((x,y))
    return ret 

def main():
  image = Image.new('RGB', (250, 250), 'white')
  draw = ImageDraw.Draw(image)
  hexagon_generator = HexagonGenerator(20)
  hexagon = hexagon_generator(0, 0)
  draw.polygon(hexagon, outline='black', fill='red')
  hexagon = hexagon_generator(0, 1)
  draw.polygon(hexagon, outline='black', fill='blue')
  hexagon = hexagon_generator(1, 0)
  draw.polygon(hexagon, outline='black', fill='black')
  hexagon = hexagon_generator(1, 1)
  draw.polygon(hexagon, outline='black', fill='yellow')
  hexagon = hexagon_generator(2, 0)
  draw.polygon(hexagon, outline='black', fill='green')
  hexagon = hexagon_generator(2, 1)
  draw.polygon(hexagon, outline='black', fill='white')
  image.show()

def main2():
  root = Tk()
  root.geometry('500x400')
  canvas = Canvas(root, width=500, height=500)
  canvas.pack()
  pilImage = Image.new('RGB', (500, 500), 'white')
  draw = ImageDraw.Draw(pilImage)
  hexagon_generator = HexagonGenerator(20)
  hexagon = hexagon_generator(0, 0)
  draw.polygon(hexagon, outline='black', fill='red')
  hexagon = hexagon_generator(0, 1)
  draw.polygon(hexagon, outline='black', fill='blue')
  hexagon = hexagon_generator(1, 0)
  draw.polygon(hexagon, outline='black', fill='black')
  hexagon = hexagon_generator(1, 1)
  draw.polygon(hexagon, outline='black', fill='yellow')
  hexagon = hexagon_generator(2, 0)
  draw.polygon(hexagon, outline='black', fill='green')
  hexagon = hexagon_generator(2, 1)
  draw.polygon(hexagon, outline='black', fill='white')
  image = ImageTk.PhotoImage(pilImage)
  imagesprite = canvas.create_image(250,250,image=image)
  #root.mainloop()
  time.sleep(2)
  hexagon = hexagon_generator(2, 1)
  draw.polygon(hexagon, outline='black', fill='purple')
  image = ImageTk.PhotoImage(pilImage)
  imagesprite = canvas.create_image(250,250,image=image)
  root.mainloop()

if __name__ == '__main__':
    main2()

