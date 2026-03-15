import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os

STICKER_FOLDER = r"C:\Users\arman\OneDrive\Desktop\Project Amrin\PhototBooth\Stickers"

cap = cv2.VideoCapture(0)

current_filter = "normal"
captured_image = None
currentSticker = None
sticker_refs = []

def applyFilter(frame):

    if current_filter == "gray":
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    elif current_filter == "blur":
        frame = cv2.GaussianBlur(frame,(15,15),0)

    elif current_filter == "cartoon":

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray,5)

        edges = cv2.adaptiveThreshold(
            blur,255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,9,9)

        color = cv2.bilateralFilter(frame,9,250,250)

        frame = cv2.bitwise_and(color,color,mask=edges)

    return frame

def cropSticker(img):

    img = img.convert("RGBA")

    alpha = img.split()[-1]

    bbox = alpha.getbbox()

    if bbox:
        img = img.crop(bbox)

    return img


def updateCamera():

    ret, frame = cap.read()

    if ret:

        frame = cv2.flip(frame,1)
        frame = applyFilter(frame)

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)

        img = img.resize((400,300))

        imgtk = ImageTk.PhotoImage(img)

        cameraLabel.imgtk = imgtk
        cameraLabel.configure(image=imgtk)

    cameraLabel.after(15,updateCamera)

def capturePhoto():

    global captured_image

    ret, frame = cap.read()

    if ret:

        frame = cv2.flip(frame,1)
        frame = applyFilter(frame)

        captured_image = frame

        showPhoto()

def showPhoto():

    photoCanvas.delete("all")

    img = cv2.cvtColor(captured_image, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)

    img.thumbnail((400,500))

    imgtk = ImageTk.PhotoImage(img)

    photoCanvas.create_image(200,250,image=imgtk)

    photoCanvas.image = imgtk

def chooseSticker(path):

    global currentSticker

    img = Image.open(path)

    img = cropSticker(img) 

    currentSticker = img

def addSticker(event):

    global currentSticker

    if currentSticker is None:
        return

    sticker = currentSticker.resize((80,80))

    imgtk = ImageTk.PhotoImage(sticker)

    photoCanvas.create_image(event.x,event.y,image=imgtk)

    sticker_refs.append(imgtk)

def saveImage():

    if captured_image is not None:
        cv2.imwrite("photobooth_result.png",captured_image)

root = tk.Tk()
root.title("💖 Cute Photobooth")
root.geometry("900x650")
root.configure(bg="#ffd6e8")


# LEFT SIDE
leftFrame = tk.Frame(root,bg="#ffd6e8")
leftFrame.pack(side="left",padx=20,pady=20)


cameraLabel = tk.Label(leftFrame)
cameraLabel.pack()


def setFilter(f):
    global current_filter
    current_filter = f


filterFrame = tk.Frame(leftFrame,bg="#ffd6e8")
filterFrame.pack(pady=10)

tk.Button(filterFrame,text="Normal",command=lambda:setFilter("normal")).pack(side="left",padx=5)
tk.Button(filterFrame,text="Gray",command=lambda:setFilter("gray")).pack(side="left",padx=5)
tk.Button(filterFrame,text="Blur",command=lambda:setFilter("blur")).pack(side="left",padx=5)
tk.Button(filterFrame,text="Cartoon",command=lambda:setFilter("cartoon")).pack(side="left",padx=5)


captureBtn = tk.Button(
    leftFrame,
    text="💗 Capture",
    font=("Arial",14),
    bg="#ff8fcf",
    command=capturePhoto
)

captureBtn.pack(pady=10)

rightFrame = tk.Frame(root,bg="#ffd6e8")
rightFrame.pack(side="right",padx=20,pady=20)


photoCanvas = tk.Canvas(
    rightFrame,
    width=400,
    height=500,
    bg="white"
)

photoCanvas.pack()

photoCanvas.bind("<Button-1>",addSticker)

stickerFrame = tk.Frame(rightFrame,bg="#ffd6e8")
stickerFrame.pack(pady=10)

for file in os.listdir(STICKER_FOLDER):

    path = os.path.join(STICKER_FOLDER,file)

    img = Image.open(path)

    img = cropSticker(img) 

    img = img.resize((40,40))

    imgtk = ImageTk.PhotoImage(img)

    btn = tk.Button(
        stickerFrame,
        image=imgtk,
        bg="#ffb3d9",
        command=lambda p=path:chooseSticker(p)
    )

    btn.image = imgtk
    btn.pack(side="left",padx=5)


saveBtn = tk.Button(
    rightFrame,
    text="💾 Download",
    bg="#ff6fb5",
    fg="white",
    font=("Arial",12),
    command=saveImage
)

saveBtn.pack(pady=10)


updateCamera()

root.mainloop()