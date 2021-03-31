import time
import struct
import sys, glob # for listing serial ports

try:
    import serial
except ImportError:
    print('Import error', 'Please install pyserial.')
    raise

connection = None

TEXTWIDTH = 40 # window width, in characters
TEXTHEIGHT = 16 # window height, in lines

VELOCITYCHANGE = 200
ROTATIONCHANGE = 300


class IRobot:
    
    callbackKeyLastDriveCommand = ''

    def myfunc(self):
        print('text')

    def sendCommandASCII(self, command):
        cmd = ""
        for v in command.split():
            cmd += chr(int(v))

        self.sendCommandRaw(cmd)
        
    def drive(self, velocity, rotation):
         
        print('my velocity'+str(velocity)) #  200 forward  -200 back
        print('my rotatio'+str(rotation))    #0 straight --300 r  ,  300 l
            # compute left and right wheel velocities
        vr = velocity + (rotation/2)
        vl = velocity - (rotation/2)

            # create drive command
        cmd = struct.pack(">Bhh", 145, vr, vl)
        if cmd != self.callbackKeyLastDriveCommand:
            self.sendCommandRaw(cmd)
            self.callbackKeyLastDriveCommand = cmd


    # sendCommandRaw takes a string interpreted as a byte array
    def sendCommandRaw(self, command):
        global connection

        try:
            if connection is not None:
                connection.write(command)
            else:
                print('Not connected!', 'Not connected to a robot!')
        except serial.SerialException:
            print('Uh-oh', "Lost connection to the robot!")
            connection = None

        print ' '.join([ str(ord(c)) for c in command ])


    # getDecodedBytes returns a n-byte value decoded using a format string.
    # Whether it blocks is based on how the connection was set up.
    def getDecodedBytes(self, n, fmt):
        global connection
        
        try:
            return struct.unpack(fmt, connection.read(n))[0]
        except serial.SerialException:
            print("Lost connection")
            connection = None
            return None
        except struct.error:
            print("Got unexpected data from serial port.")
            return None

    # get8Unsigned returns an 8-bit unsigned value.
    def get8Unsigned(self):
        return getDecodedBytes(1, "B")

    # get8Signed returns an 8-bit signed value.
    def get8Signed(self):
        return getDecodedBytes(1, "b")

    # get16Unsigned returns a 16-bit unsigned value.
    def get16Unsigned(self):
        return getDecodedBytes(2, ">H")

    # get16Signed returns a 16-bit signed value.
    def get16Signed(self):
        return getDecodedBytes(2, ">h")


    def connect(self,port):
        global connection

        if connection is not None:
            print('Oops', "You're already connected!")
            return

        if port is not None:
            print("Trying " + str(port) + "... ")
            try:
                connection = serial.Serial(port, baudrate=115200, timeout=1)
                print('Connected', "Connection succeeded!")
            except:
                print('Failed', "Sorry, couldn't connect to " + str(port))

    
    def getSerialPorts(self):
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        print(result)
        return result    


# p1 = IRobot()
# p1.getSerialPorts()
# p1.connect('/dev/tty.usbserial-DN027Y2O')
# p1.sendCommandASCII('128')
# p1.sendCommandASCII('131')
# p1.sendCommandASCII('140 3 1 64 16 141 3')
# p1.drive(-200, 0)  #foward,
# time.sleep(1)
# p1.drive(0, -30)  #turn right,
# time.sleep(1)
# drive(-200, 0) #backwardard,
# p1.drive(0,0) 