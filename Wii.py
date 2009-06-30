__all__ = []

from common import *
from formats import *
from banner import *
from title import *
from disc import *
from image import *
from archive import *
from export import *
from compression import *
from nand import *

if (__name__ == "__main__"):
	Crypto()
	TMD()
	Ticket()
	
	#insert non-dependant check code here
	
	print ("\nAll Wii.py components loaded sucessfully!\n")
