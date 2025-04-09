#from kultunaut.lib.MariaDBInterface import MariaDBInterface
#from dotenv import dotenv_values
#conf = {**dotenv_values(".env"),**dotenv_values(".env.secret")}
##from kultunaut.lib import lib
#
#ROOTDIR = f"{conf['ROOTDIR']}"    #/home/nb/repos/kultunaut/kultunaut-libs"
#WEBROOT = f"{ROOTDIR}/{conf['WEBROOT']}"
#TEMPLATES = f"{ROOTDIR}/{conf['TEMPLATES']}"
#
#db = MariaDBInterface()
from kultunaut.lib.MariaDBInterface import MariaDBInterface
import subprocess
import time

def test_mariadb_connection():
    """
    Tests the connection to a MariaDB server. If the connection fails,
    it attempts to restart the MariaDB service on Ubuntu.
    """
    #try:
    mydb = MariaDBInterface()
    if mydb.testConn:
      print("MariaDB connection successful!")
      mydb.__del__()
      return True
      #except:
    else:
          print("Error connecting to MariaDB")
          print("Attempting to restart MariaDB server...")
          if restart_mariadb_service():
            print("MariaDB server restarted. Retrying connection...")
            mydb = MariaDBInterface()
            if mydb.testConn:
                print("MariaDB connection successful after restart!")
                mydb.close()
                return True
            else:
                print("Error connecting to MariaDB after restart")
                return False
          else:
            print("Failed to restart MariaDB server.")
            return False



def restart_mariadb_service():
    """
    Attempts to restart the MariaDB service on Ubuntu using systemctl.

    Returns:
        bool: True if the restart command was executed successfully, False otherwise.
    """
    try:
        # Use subprocess to run the systemctl command
        process = subprocess.Popen(["sudo", "systemctl", "restart", "mariadb"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=15)  # Add a timeout to prevent indefinite blocking

        if process.returncode == 0:
            print("MariaDB service restart initiated successfully.")
            time.sleep(5)  # Give the server some time to restart
            return True
        else:
            print(f"Error restarting MariaDB service (return code: {process.returncode}):")
            print(f"Stdout: {stdout.decode()}")
            print(f"Stderr: {stderr.decode()}")
            return False
    except FileNotFoundError:
        print("Error: systemctl command not found. This script is designed for systems using systemd.")
        return False
    except subprocess.TimeoutExpired:
        print("Error: Restarting MariaDB service timed out.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while restarting MariaDB: {e}")
        return False
      
if __name__ == "__main__":
  test_mariadb_connection()
  #if restart_mariadb_service():
  #  print("MariaDB restarted with success")