#driver.py

import sys
from pyke import knowledge_engine
from pyke import krb_traceback

engine = knowledge_engine.engine(__file__)

#fc_goal = goal.compile('facts.how_related($place1, $place2, $relationship)')

def fc_test():
    engine.reset()
    try:
        engine.activate('fc_file')
    except:
        krb_traceback.print_exc()
        sys.exit(1)