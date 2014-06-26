from __future__ import print_function
#===============================================================================
# import argparse
# import glob
# import os
# import random
#===============================================================================
import json
import re
import os
import glob
from subprocess import check_call


d = {"lat": 42.3581, 
    "long": -71.0636, 
    "sent": "In the North End, try <v>La Summa</v>, <v>Cantina Italiana</v>, <v>Massimino's</v> or <v>Pizzeria Regina</v>.", 
    "venueName": "Cantina Italiana"}

target = d["venueName"]
sent = d["sent"]

venues = re.findall('<v>(.+?)</v>', sent)
#print(venues)

sent = re.sub('<..?>','',sent)
for v in venues:
    if v != target:
        sent = re.sub(v, '', sent)
print(sent)
         
