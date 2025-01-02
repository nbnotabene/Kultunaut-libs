#from kultunaut.lib import jsoncache
from kultunaut.lib import kultDBInput

def kultToDB():
  # insert kultInput
  # From Kultunaut - called from cronjob?
  kultDBInput.kultToDB()  
  
if __name__ == "__main__":
  #kultDBInput.cacheToDB()
  kultDBInput.kultToDB()
