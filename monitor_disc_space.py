import paramiko, smtplib, os, sys
import smtplib,argparse  
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Class to monitor disc space
class MonitorDiscSpace:

    # Initialize the class
    def __init__(self, args):
        if args["ssh_host"]!=None:
            self.ssh_host=args["ssh_host"]
        else:
            self.ssh_host="your host"
        if args["ssh_port"]!=None:
            self.ssh_port=args["ssh_port"]
        else:
            self.ssh_port=22
        if args["ssh_username"]!=None:
            self.ssh_username=args["ssh_username"]
        else:
            self.ssh_username="your username"
        if args["ssh_password"]!=None:
            self.ssh_password=args["ssh_password"]
        else:
            self.ssh_password="your ssh password"
        if args["check_percentage"]!=None:
            self.check_percentage=args["check_percentage"]
        else:
            self.check_percentage=90
        if args["email"]!=None:
            self.email_user=args["email"]
        else:
            self.email_user= "your email"
        if args["password"]!=None:
            self.user_password=args["password"]
        else:
            self.user_password="your password"
        if args["recipient"]!=None:
            self.recipient=args["recipient"]
        else:
            self.recipient="recipient email"
            
        self.total_percentage = 0
        self.size=0
        self.total_size = 0
        self.avilable_size = 0
        self.total_avilable_size = 0
        self.connection = paramiko.SSHClient()
        self.connection.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connection.connect(self.ssh_host, self.ssh_port, self.ssh_username, self.ssh_password,look_for_keys=True, disabled_algorithms={'keys': ['rsa-sha2-256', 'rsa-sha2-512']})
        self.stdin, self.stdout, self.Stderr = self.connection.exec_command("df -h")
        self.output = self.stdout.read().decode()
        self.connection.close()

    # Convert the size to gigabytes
    def conv_KB_to_GB(self):
            gigabyte = 1.0/1073741824
            convert_gb = gigabyte * float(self.size)
            return convert_gb

    # Convert the size to gigabytes
    def conv_MB_to_GB(self):
            gigabyte = 1.0/1024
            convert_gb = gigabyte * float(self.size)
            return convert_gb

    # Convert the size to gigabytes
    def conv_TB_to_GB(self):
            gigabyte = 1024
            convert_gb = gigabyte * float(self.size)
            return convert_gb
    
    # Convert the size to gigabytes
    def conv_PB_to_GB(self):
            gigabyte = 1048576
            convert_gb = gigabyte * float(self.size)
            return convert_gb

    # Get the total percentage of disc space used
    def check_disc_space(self):
        myresult=True
        for line in self.output.splitlines():
            if "Filesystem" in line or "Size" in line or "Use" in line or "Mounted" in line:
                continue
            try:
                NewPercentage = int(line.split()[4].strip("%"))
                self.total_percentage += NewPercentage
            except:      
                raise Exception("Error: Unable to get the percentage of disc space used")
            finally:
                if NewPercentage >= self.check_percentage:
                    myresult=False
        return [myresult,"{}%".format(self.total_percentage)]   
    
        return [myresult,"{}%".format(self.total_percentage)] 

    # Get the total Size of disc space Allocated
    def get_total_size(self):    
        for line in self.output.splitlines():
                AllocatedSize = (line.split()[1]) 
                if "Filesystem" in line or "Size" in line or "Use" in line or "Mounted" in line:
                    continue
                elif "G" in AllocatedSize:
                    self.size = AllocatedSize.strip("G")
                    self.total_size+= float(self.size)
                elif "M"  in AllocatedSize:
                    self.size = float(AllocatedSize.strip("M"))
                    self.total_size+= self.conv_MB_to_GB()
                elif "K"  in AllocatedSize:
                    self.size = float(AllocatedSize.strip("K"))
                    self.total_size+= self.conv_KB_to_GB()

        return "{}GB".format(self.total_size)

    # Get the total Size of disc space Avilable
    def get_total_avilable_size(self):    
        for line in self.output.splitlines():
                AvilableSize = (line.split()[3]) 
                if "Filesystem" in line or "Size" in line or "Use" in line or "Mounted" in line:
                    continue
                elif "G" in AvilableSize:
                    self.avilable_size = AvilableSize.strip("G")
                    self.total_avilable_size+= float(self.avilable_size)
                elif "M"  in AvilableSize:
                    self.avilable_size = float(AvilableSize.strip("M"))
                    self.total_avilable_size+= self.conv_MB_to_GB()
                elif "K"  in AvilableSize:
                    self.avilable_size = float(AvilableSize.strip("K"))
                    self.total_avilable_size+= self.conv_KB_to_GB()

        return "{}GB".format(self.total_avilable_size) 

    # Print Mounted on  
    def print_mounted_on(self):
        for line in self.output.splitlines():
            if "Filesystem" in line or "Size" in line or "Use" in line or "Mounted" in line:
                continue
            else:
                print(line.split()[5])

    # Print File System
    def print_all_file_system(self):
        for line in self.output.splitlines():
            if "Filesystem" in line or "Size" in line or "Use" in line or "Mounted" in line:
                continue
            else:
                print(line.split()[0])

    # Send email to the user
    def send_email(self):
        self.Message = MIMEMultipart()
        self.Message["From"] = self.recipient
        self.Message["To"] = self.email_user
        self.Message["Subject"] = "Disc Space Alert"
        self.Message.attach(MIMEText(self.output, "plain"))
        self.Server = smtplib.SMTP("smtp.gmail.com", 587)
        self.Server.starttls()
        self.Server.login(self.email_user, self.user_password)
        self.Server.sendmail(self.email_user, self.recipient, self.Message.as_string())
        self.Server.quit()

    def close_connection(self):
        self.Connection.close()

if __name__ == "__main__":
    MyArgs = argparse.ArgumentParser()
    MyArgs.add_argument("--ssh_host", help="SSH Host")
    MyArgs.add_argument("--ssh_port", help="SSH Port")
    MyArgs.add_argument("--ssh_username", help="SSH UserName")
    MyArgs.add_argument("--ssh_password",help="SSH Password")
    MyArgs.add_argument("--check_percentage", help="Check Percentage")
    MyArgs.add_argument("--email", help="Email Address")
    MyArgs.add_argument("--recipient", help="Recipient Email Address")
    MyArgs.add_argument("--password", help="Password")
    
    Myobject = MonitorDiscSpace(dict((MyArgs.parse_args()._get_kwargs())))
    mysize = Myobject.get_total_size()
    AvilableSize = Myobject.get_total_avilable_size()
    
    print("Total Allocated Size : {}".format(mysize))
    print("Total Avilable Size : {}".format(AvilableSize))
    result=Myobject.check_disc_space()
    print("Total Percentage Used : {}".format(result[1]))
    if result[0]:
        print("Disc space is OK")
    else:
        Myobject.send_email()
        print("Disc space is full")

# Usage
# python3 MonitorDiscSpace.py --ssh_host 192.168.1.1 --ssh_port 22 --ssh_username root --ssh_password password --check_percentage 80 --email --password --recipient
# or
# python3 MonitorDiscSpace.py
# you need to enter the following details under the else statement at the top of the script 
# Enter SSH Host :
# Enter SSH Port :
# Enter SSH Username :
# Enter SSH Password :
# Enter Check Percentage :
# Enter Email Address :
# Enter Password :
# Enter Recipient Email Address :
 