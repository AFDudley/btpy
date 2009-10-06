ELEMENTS = E, F, I, W = ("Earth", "Fire", "Ice", "Wind")

ORTH = {E: (F, I), #Earth is orthogonal to Fire and Ice

F: (E, W),  #Fire  is orthogonal to Earth and Wind
I: (E, W),  #Ice   is orthogonal to Earth and Wind
W: (F, I),}  #Wind  is orthogonal to Fire and Ice
OPP = {E: W, W: E, #Earth and Wind are opposites                                                      
F: I, I: F} #Fire and Ice are opposites   

COMP = {E:0, F:0, I:0, W:0}
