from tkinter import *
import random
import threading
import niya_solver









root = Tk()
root.title("Niya Oracle")
root.resizable(width=False,height=False)
canv = Canvas(root)
status = Label(root,text="Status Line", relief=SUNKEN)
canv.grid(row=0,column=0,sticky="NEWS")
status.grid(row=1,column=0,sticky="NEWS")
root.rowconfigure(0,weight=1)
root.rowconfigure(1,weight=0)
root.columnconfigure(0,weight=1)










# alright, let's get drawing!
cell=50

canv.config(height=cell*6,width=cell*12,bg="gray")
background_boxes = {}
for i in range(1,5):
    for j in range(1,5):
        background_boxes[(i,j)] = canv.create_rectangle(i*cell+1,j*cell+1,
                                                        (i+1)*cell-1,
                                                        (j+1)*cell-1,
                                                        fill="orange")

        



def coord_conv(x,y):
    r = cell//2-6
    return (x-r,y-r,x+r,y+r)



def simpler_coord(i,j):
    return (i*cell+cell//2,j*cell+cell//2)


        
class Disk:
    def __init__(self,loc,fill=None):
        if(fill):
            self.oval = canv.create_oval(*(coord_conv(*loc)),fill=fill)
        else:
            self.oval = canv.create_oval(*(coord_conv(*loc)))
        self.loc = loc

    def get_coords(self):
        return self.loc

    # def get_id(self):
    #     return self.oval
    
    def set_coords(self,loc):
        self.loc = loc
        canv.coords(self.oval,*(coord_conv(*loc)))

    def bind(self,event_name,handler):
        canv.tag_bind(self.oval,event_name,handler)




class LetterDisk:
    def __init__(self,loc,fill,letter='A'):
        self.oval = canv.create_oval(*(coord_conv(*loc)),fill=fill)
        self.text = canv.create_text(*loc,text=letter,font=("Times",16))
        self.loc = loc

    def get_coords(self):
        return self.loc

    # def get_id(self):
    #     return self.oval

    def set_coords(self,loc):
        self.loc = loc
        canv.coords(self.oval,*(coord_conv(*loc)))
        canv.coords(self.text,*loc)

    def bind(self,event_name,handler):
        canv.tag_bind(self.oval,event_name,handler)
        canv.tag_bind(self.text,event_name,handler)


class Piece:
    def __init__(self,loc,poem,plant):
        converted = coord_conv(*loc)
        nw = (converted[0],converted[1])
        se = (converted[2],converted[3])
        color = ['yellow','red','white','gray'][poem]
        poem = ['sun','tanzaku','bird','cloud'][poem]
        plant = ['maple','cherry','pine','iris'][plant]
        self.box = canv.create_rectangle(*converted,fill=color)
        self.poem = canv.create_text(*se,text=poem,anchor='se',font=('Times','9'))
        self.plant = canv.create_text(*nw,text=plant,anchor='nw',font=('Times','9'))
        self.loc = loc

    def get_coords(self):
        return self.loc

    def set_coords(self,loc):
        self.loc = loc
        converted = coord_conv(*loc)
        nw = (converted[0],converted[1])
        se = (converted[2],converted[3])
        canv.coords(self.box,*converted)
        canv.coords(self.poem,*se)
        canv.coords(self.plant,*nw)

    def bind(self,event_name,handler):
        for id in [self.box, self.plant, self.poem]:
            canv.tag_bind(id,event_name,handler)

        

colors = ["orange","black","white","purple","red","green","blue",
                         "yellow","cyan","magenta","gray"]
letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
random.shuffle(colors)
random.shuffle(letters)

combos = [(i%4,i//4) for i in range(16)]
random.shuffle(combos)


siberia = (-200,-200)




    
motion_steps = 2
class ClickHandler:
    def __init__(self,under,cover,behavior):
        self.under = under
        self.cover = cover
        self.behavior = behavior

        self.state = 0 # 0 neutral, 1 dragging, 2, flying

        self.offset = None # during dragging, it's the offset
        self.move_list = None # during flying, it's the list of locations
        

    def mouseDown(self,event):
        self.state = 1
        (cx,cy) = self.under.get_coords()
        self.cover.set_coords((cx,cy))
        self.under.set_coords(siberia)
        self.offset = (cx-event.x,cy-event.y)
        

    def mouseMove(self,event):
        if(self.state != 1):
            return
        self.cover.set_coords((event.x+self.offset[0],event.y+self.offset[1]))

        
    def mouseUp(self,event):
        (c1,c2) = (event.x + self.offset[0],event.y + self.offset[1])
        (dest1,dest2) = self.behavior((c1,c2))
        delta1 = (c1 - dest1)/motion_steps
        delta2 = (c2 - dest2)/motion_steps
        self.move_list = []
        
        for i in range(motion_steps):
            self.move_list.append((dest1,dest2))
            dest1+=delta1
            dest2+=delta2
        self.state = 2
        self.time_callback()

    def time_callback(self):
        if(self.state != 2):
            return
        c = self.move_list.pop()
        if(len(self.move_list) == 0):
            self.state = 0
            self.cover.set_coords(siberia)
            self.under.set_coords(c)
        else:
            self.cover.set_coords(c)
            root.after(20,self.time_callback)
            


def default_behave(loc):
    (c1,c2) = loc
    i = c1//cell
    j = c2//cell
    if(i >= 7):
        dest1 = max(c1,7.5*cell)
        dest2 = max(c2,0.5*cell)
    else:
        dest1 = ((c1+0)//cell)*cell+cell//2
        dest2 = ((c2+0)//cell)*cell+cell//2

    return (dest1,dest2)



unders = []
covers = []
homes = []
names = []
board_inhabitants = {}
who = -1



for i in range(20):
    unders.append(Disk(simpler_coord(5,0),fill="red"))
    homes.append(simpler_coord(5,0))
    names.append((-1,-1))
    unders.append(Disk(simpler_coord(5,5),fill="black"))
    homes.append(simpler_coord(5,5))
    names.append((-1,1))

for i in range(16):
    poem = i%4
    plant=i//4
    unders.append(Piece(simpler_coord(poem+7,plant+1),poem,plant))
    homes.append(simpler_coord(poem+7,plant+1))
    names.append((plant,poem))


move_marker = LetterDisk(simpler_coord(4,0),'lightgreen','Go')

def move_marker_behave(loc):
    global who
    (x,y) = loc
    if(y < 3*cell):
        who = -1
        handle_game()
        return simpler_coord(4,0)
    else:
        who = 1
        handle_game()
        return simpler_coord(4,5)



for i in range(20):
    covers.append(Disk(siberia,fill="red"))
    covers.append(Disk(siberia,fill="black"))
for i in range(16):
    poem = i%4
    plant=i//4
    covers.append(Piece(siberia,poem,plant))

over_move_marker = LetterDisk(siberia,'lightgreen','Go')


class behave_generator:
    def __init__(self,index):
        self.index = index

    def behave(self,loc):
        global who
        which = None
        for key in board_inhabitants:
            if(board_inhabitants[key] == self.index):
                which = key
        if(which):
            del board_inhabitants[which]
            
        (x,y) = loc
        i = x//cell
        j = y//cell
        # print("Hm (%d,%d)" % (i,j))
        if(i == 0 and j == 0 and names[self.index][0] != -1):
            if((i,j) in board_inhabitants):
                displaced = board_inhabitants[(i,j)]
                co = homes[displaced]
                # print("Sending piece %d to (%d,%d)" % (displaced,*co))
                unders[displaced].set_coords(co)
            board_inhabitants[(i,j)] = self.index
            return simpler_coord(i,j)
        if(1 <= i and i <= 4 and 1 <= j and j <= 4):
            if((i,j) in board_inhabitants):
                displaced = board_inhabitants[(i,j)]
                if(names[self.index] == (-1,who) and names[displaced][0] != -1):
                    if((0,0) in board_inhabitants):
                        displaced2 = board_inhabitants[(0,0)]
                        co = homes[displaced2]
                        unders[displaced2].set_coords(co)
                    unders[displaced].set_coords(simpler_coord(0,0))
                    board_inhabitants[(0,0)] = displaced
                    who = -who
                    if(who == 1):
                        move_marker.set_coords(simpler_coord(4,5))
                    else:
                        move_marker.set_coords(simpler_coord(4,0))
                else:
                    unders[displaced].set_coords(homes[displaced])
            board_inhabitants[(i,j)] = self.index
            return simpler_coord(i,j)
        x = max(5.5*cell,x)
        y = max(0,y)
        x = min(12*cell,x)
        y = min(6*cell,y)
        # if(x >= cell//2 and x <= 5.5*cell and y >= 0.5*cell and y <= 5.5*cell):
        #     print("slide")
        #     i = x//cell
        #     j = y//cell
        #     return simpler_coord(i,j)
        return (x,y)

    def wrap(self,loc):
        print("Before:")
        print(board_inhabitants)
        retval = self.behave(loc)
        print("After:")
        print(board_inhabitants)
        handle_game()
        return retval




for i in range(len(unders)):
    handle = ClickHandler(unders[i],covers[i],behave_generator(i).wrap)
    unders[i].bind("<Button-1>",handle.mouseDown)
    unders[i].bind("<B1-Motion>",handle.mouseMove)
    unders[i].bind("<ButtonRelease-1>",handle.mouseUp)    

mmhandle = ClickHandler(move_marker,over_move_marker,move_marker_behave)
move_marker.bind("<Button-1>",mmhandle.mouseDown)
move_marker.bind("<B1-Motion>",mmhandle.mouseMove)
move_marker.bind("<ButtonRelease-1>",mmhandle.mouseUp)    


serial = 0
    
def handle_game():
    global serial
    serial += 1
    for i in range(16):
        x = i//4 + 1
        y = i%4 + 1
        if (x,y) not in board_inhabitants:
            status.config(text="Incomplete Position")
            return
    board = []
    for i in range(16):
        x = i//4 + 1
        y = i%4 + 1
        board.append(names[board_inhabitants[(x,y)]])
    status.config(text="Thinking")
    threading.Thread(target=for_real,args=(board,)).start()

def for_real(board):
    my_serial = serial
    prev = None
    if((0,0) in board_inhabitants):
        prev = names[board_inhabitants[(0,0)]]
        if(prev[0] == -1):
            prev = None
    local_who = who
    (move,score) = niya_solver.bestMoveAndScore(board,local_who,prev,16)
    if(serial == my_serial):
        current = "Red" if local_who == -1 else "Black"
        winner = "Red" if score[0] == -1 else "Black"
        margin = score[1] if score[0] == 1 else -score[1]
        outcome = "%s wins by %d points." % (winner,margin)
        if(move == None):
            explanation = "%s must forfeit!" % current
        elif(niya_solver.score(board)[0] != 0):
            explanation = "%s has already won!" % winner
        else:
            explanation = "An optimal move is at (%d,%d)." % (move//4+1,move%4+1)

        status.config(text=outcome + "  " + explanation)
                                                

root.mainloop()
