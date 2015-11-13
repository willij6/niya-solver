#!/usr/bin/python3

from tkinter import *
import random
import threading
import analyzer









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

        


excla = canv.create_text(5*cell + cell//2, 1*cell + cell//2, text="!",font=("Arial",20))

def set_who(who):
    if(who == -1):
        canv.coords(excla,5*cell+cell//2,1*cell+cell//2)
    else:
        canv.coords(excla,5*cell+cell//2,4*cell+cell//2)


siberia = (-100,-100)
motion_steps = 5




class PieceWrapper:
    '''Manage the business with two copies of each piece'''
    def __init__(self,lower,upper):
        self.inverted = False
        self.lower = lower
        self.upper = upper
        self.loc = lower.get_coords()

    def get_loc(self):
        return self.loc

    def set_loc(self,loc,inverted):
        self.loc = loc
        if(inverted):
            self.upper.set_coords(loc)
        else:
            self.lower.set_coords(loc)
        if(inverted != self.inverted):
            if(self.inverted):
                self.upper.set_coords(siberia)
            else:
                self.lower.set_coords(siberia)
            self.inverted = inverted

    


class DragManager:
    def __init__(self,state_manager,pieces):
        self.state_manager = state_manager
        state_manager.register(self.update)
        lowers = []
        for i in range(len(pieces)):
            lowers.append(pieces[i].create(state_manager.piece_location(i)))
        uppers = [p.create(siberia) for p in pieces]
        self.wrappers = [PieceWrapper(lowers[i],uppers[i]) for
                         i in range(len(pieces))]
        
        self.held = [False for p in pieces]
        self.move_lists = [[] for p in pieces]

        self.active_timer = False

        for i in range(len(pieces)):
            self.bindIth(i,lowers[i])




        
    def update(self,dirty):
        for i in dirty:
            if(self.held[i]):
                continue
            self.move_lists[i] = []
            (dest1,dest2) = self.state_manager.piece_location(i)
            (start1,start2) = self.wrappers[i].get_loc()
            # print("Moving from (%d,%d) to (%d,%d)" % (start1,start2,dest1,dest2))
            delta1 = (start1 - dest1)/motion_steps
            delta2 = (start2 - dest2)/motion_steps
            for j in range(motion_steps):
                self.move_lists[i].append((dest1,dest2))
                dest1 += delta1
                dest2 += delta2
        if(not self.active_timer):
            self.time_call()
            
    def time_call(self):
        any = False
        for i in range(len(self.wrappers)):
            if(len(self.move_lists[i]) == 0):
                continue
            c = self.move_lists[i].pop()
            if(len(self.move_lists[i]) == 0):
                self.wrappers[i].set_loc(c,False)
            else:
                any = True
                self.wrappers[i].set_loc(c,True)
        if(any):
            self.active_timer = True
            root.after(20,self.time_call)
        else:
            self.active_timer = False


    def bindIth(self,index,lower):
        '''Create three closures and bind them to the mouse buttons'''
        offset = None
        def mouseDown(event):
            nonlocal offset
            if(self.state_manager.disabled(index)):
                # print("Denied!")
                self.held[index] = False
            else:
                self.held[index] = True
                (cx,cy) = self.wrappers[index].get_loc()
                self.wrappers[index].set_loc((cx,cy),True)
                offset = (cx-event.x,cy-event.y)

        def mouseMove(event):
            if(self.held[index]):
                self.wrappers[index].set_loc(
                    (event.x+offset[0],event.y+offset[1]),True)

        def mouseUp(event):
            if(not self.held[index]):
                return
            self.held[index] = False
            (cx,cy) = (event.x+offset[0],event.y+offset[1])
            self.state_manager.try_move(index,(cx,cy))

        def doubleClick(event):
            if(not self.held[index]):
                self.state_manager.try_activate(index)
            else:
                print("Oh, this is awkward!")
                    

        for q in [lower]: # in [lower,upper]
            q.bind("<Button-1>",mouseDown)
            q.bind("<B1-Motion>",mouseMove)
            q.bind("<ButtonRelease-1>",mouseUp)
            q.bind("<Double-Button-1>",doubleClick)
            q.bind("<Button-3>",doubleClick)



cell = 50


# 
def slot_coordinate(loc):
    return tuple([x*cell+cell//2 for x in loc])


class StateManager:

    
    def __init__(self,pieces):
        self.names = [p.name for p in pieces]
        self.homes = [p.home for p in pieces]
        self.locs = [None for p in pieces]
        self.in_slot = [None for p in pieces]
        for i in range(len(self.names)):
            self.send_home(i)
        self.corrupted = set()

        self.editing = True
        self.who = -1
        self.listeners = set()


        self.stack = []

        # todo: remember state


    def send_home(self,index):
        (i,j) = self.homes[index]
        if i >= 6:
            self.locs[index] = slot_coordinate((i,j))
            self.in_slot[index] = False
        else:
            self.locs[index] = (i,j)
            self.in_slot[index] = True
            

    def register(self,listener):
        self.listeners.add(listener)


    def piece_location(self,index):
        if(self.in_slot[index]):
            return slot_coordinate(self.locs[index])
        return self.locs[index]

    def disabled(self,index):
        if(self.editing):
            return False
        # so, we're playing a game
        # the piece is disabled unlesss it's a disk belonging to current player
        # also, it can't be on the board
        if(self.in_slot[index]):
            (i,j) = self.locs[index]
            if(1 <= i and i <= 4 and 1 <= j and j <= 4):
                return True
        return self.names[index] != (-1,self.who)
    
    def clear_slot(self,slot,toZeroZero = False):
        for i in range(len(self.names)):
            if(self.in_slot[i] and self.locs[i] == slot):
                self.corrupted.add(i)
                if(toZeroZero):
                    self.in_slot[i] = True
                    self.locs[i] = (0,0)
                else:
                    self.send_home(i)

    def notify(self):
        for ell in self.listeners:
            ell(self.corrupted)
        self.corrupted = set()

    def record(self):
        data = (tuple(self.locs),tuple(self.in_slot),self.editing,self.who)
        if(len(self.stack) > 0 and self.stack[-1] == data):
            return
        self.stack.append(data)
        # print("After push, stack is " + str(self.stack))

    def pop(self):
        # print("Before pop, stack is " + str(self.stack))
        (ell,i_s,ed,wh) = self.stack.pop()
        self.locs = list(ell)
        self.in_slot = list(i_s)
        self.editing = ed
        self.who = wh
        
        

    def try_move(self,index,loc):
        self.record()
        success = self.try_move_inner(index,loc)

        self.corrupted.add(index)
        self.misc_update()
        self.notify()
        # TODO:
        # store the state and process it, if success is true!

    # return whether or not we accepted the move!!!
    # if return value is false, then state should not have changed
    def try_move_inner(self,index,loc):
        i = loc[0]//cell
        j = loc[1]//cell
        name = self.names[index]
        if(0 <= i and i < 6 and 0 <= j and j < 6):
            # always allow a piece to return home
            if((i,j) == self.homes[index]):
                self.send_home(index)
                return True
            if(self.editing):
                success = False
                if((i,j) == (0,0) and name[0] != -1):
                    success = True
                elif(1 <= i and i <= 4 and 1 <= j and j <= 4):
                    success = True
                if(success):
                    self.clear_slot((i,j))
                    self.in_slot[index] = True
                    self.locs[index] = (i,j)
                    return True
                return False
            else:
                # in game mode
                if(name != (-1,self.who)):
                    return False
                if(i < 1 or i > 4 or j < 1 or j > 4):
                    return False
                # TODO: check legality of the move
                self.clear_slot((0,0))
                self.clear_slot((i,j),toZeroZero = True)
                self.in_slot[index] = True
                self.locs[index] = (i,j)
                self.who = -self.who
                set_who(self.who)
                return True
        else:
            if(self.editing):
                (x,y) = loc
                x = max(6*cell+cell//2,x)
                x = min(12*cell-cell//2,x)
                y = max(0+cell//2,y)
                y = min(6*cell-cell//2,y)
                self.in_slot[index] = False
                self.locs[index] = (x,y)
                return True
            return False # don't move pieces during game mode

    def try_activate(self,index):
        return # TODO


    def clear_board(self,event):
        if(self.editing):
            self.record()
            for i in range(len(self.names)):
                self.corrupted.add(i)
                self.send_home(i)
            self.misc_update()
            self.notify()

    def randomize(self,event):
        if(not self.editing):
            return
        self.record()
        dests = []
        for i in range(1,5):
            for j in range(1,5):
                dests.append((i,j))
        random.shuffle(dests)
        for i in range(len(self.names)):
            name = self.names[i]
            if name[0] == -1:
                self.corrupted.add(i)
                self.send_home(i)
            else:
                self.corrupted.add(i)
                self.in_slot[i] = True
                self.locs[i] = dests[name[0]*4+name[1]]
        self.misc_update()
        self.notify()

    def toggle(self,event):
        self.record()
        self.editing = not self.editing
        self.misc_update()

    def toggle_who(self,event):
        if(self.editing):
            self.record()
            self.who = -self.who
            self.misc_update()

    # TODO: redo
    
    def undo(self,event):
        if(len(self.stack) > 0):
            self.pop()
            self.misc_update()
            for i in range(len(self.names)):
                self.corrupted.add(i)
            self.notify()


    def misc_update(self):
        set_who(self.who)
        if(self.editing):
            canv.config(bg="gray")
        else:
            canv.config(bg="white")
        self.process_board()


    def process_board(self):
        global serial
        serial += 1
        prev = None
        board = [None for i in range(16)]
        for i in range(len(self.names)):
            if(self.in_slot[i]):
                (x,y) = self.locs[i]
                if (x,y) == (0,0):
                    prev = self.names[i]
                elif 1 <= x and x <= 4 and 1 <= y and y <= 4:
                    board[analyzer.code(y-1,x-1)] = self.names[i]
        if(None in board):
            status.config(text="Incomplete Position")
            return
        if self.editing:
            status.config(text="Complete Position")
        else:
            status.config(text="Thinking")
            threading.Thread(target=for_real,args=(board,prev,self.who)).start()
        # TODO: directly analyze the position, see if anyone won
        # also do some other stuff like indicate legal moves
            


serial = 0        
                
def for_real(board,prev,who):
    my_serial = serial
    local_who = who
    (move,score) = analyzer.bestMoveAndScore(board,local_who,prev,16)
    if(serial == my_serial):
        current = "Red" if local_who == -1 else "Black"
        winner = "Red" if score[0] == -1 else "Black"
        margin = score[1] if score[0] == 1 else -score[1]
        outcome = "%s wins by %d points." % (winner,margin)
        if(move == None):
            explanation = "%s must forfeit!" % current
        elif(analyzer.score(board)[0] != 0):
            explanation = "%s has already won!" % winner
        else:
            explanation = "An optimal move is at (%d,%d)." % (move//4+1,move%4+1)

        status.config(text=outcome + "  " + explanation)
        # TODO: show the optimal move on the map



class DiskGenerator:
    def __init__(self,who):
        self.color = "red" if who == -1 else "black"
        self.name = (-1,who)
        self.home = (5,0) if who == -1 else (5,5)
        

    def create(self,loc):
        return Disk(loc,self.color)

class PieceGenerator:
    def __init__(self,poem,plant):
        self.poem = poem
        self.plant = plant
        self.name = (poem,plant)
        self.home = (poem+7,plant+1)

    def create(self,loc):
        return Piece(loc,self.poem,self.plant)



def coord_conv(x,y):
    r = cell//2-6
    return (x-r,y-r,x+r,y+r)
    

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




pieces = ([DiskGenerator(-1) for i in range(20)] +
          [DiskGenerator(1) for i in range(20)])
for i in range(4):
    for j in range(4):
        pieces.append(PieceGenerator(i,j))
sm = StateManager(pieces)
dm = DragManager(sm,pieces)


root.bind("<Escape>",sm.clear_board)
root.bind("<space>",sm.randomize)
root.bind("w",sm.toggle_who)
root.bind("t",sm.toggle)
root.bind("z",sm.undo)
root.mainloop()
