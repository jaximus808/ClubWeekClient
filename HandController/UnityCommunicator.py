from packet import packet
import struct;

class UnityCommunicator():

    def __init__(self,udpIP, InPort, outPort,Hands, targetServer,targetPort,enableCom=True, supressWarnings=True):
        import socket;
        
        self.hand = Hands;

        self.targetServer = targetServer; 

        self.targetPort = targetPort; 

        self.packetHandler = {
            0:self.SetClientId,
            1:self.PingHandle,
            10: self.FleetServerEnded
        }

        self.udpIP = udpIP;
        self.udpSendPort = InPort;
        self.udpRcvPort = outPort;
        self.enableCom = enableCom;
        self.suppressWarnings = supressWarnings
        self.isDataReceived = False;
        self.dataRx = None; 

        self.disconnected = False; 

        self.udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # internet protocol, udp (DGRAM) socket
        self.udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allows the address/port to be reused immediately instead of it being stuck in the TIME_WAIT state waiting for late packets to arrive.
        self.udpSock.bind((udpIP, outPort))

        if enableCom:
            import threading;
            self.outPortThread = threading.Thread(target=self.ReadUdpThreadFunc, daemon=True);
            self.outPortThread.start();
    
    def FleetServerEnded(self, _packet):
        print("MEOW")
        self.hand.connected = False; 
        self.hand.clientId = -1;
        #self.disconnected = True;

    def SetClientId(self, _packet):
        self.hand.clientId = _packet.ReadInt();
        self.hand.connected = True; 
        print("Connected with id: " + str(self.hand.clientId) )

    def PingHandle(self, _packet):
        bytepacket = bytearray(struct.pack("i",1));
        bytepacket += bytearray(struct.pack("i",self.hand.clientId));
        bytepacket += bytearray(struct.pack("i",3));
        bytepacket += bytearray(struct.pack("?",False));
        self.SendData(bytepacket); 

    def PacketHandler(self, _packet):
        packetType = _packet.ReadInt()
        self.packetHandler[packetType](_packet);

    def __del__(self):
        self.CloseSocket();

    def CloseSocket(self):
        self.udpSock.close();

    def SendData(self, data):
        #packetData = bytearray(data.handDetect);
        #need to change this to actually send to ip
        self.udpSock.sendto(data, (self.targetServer,self.targetPort));

    def ReceiveData(self):
        """
        Should not be called by user
        Function BLOCKS until data is returned from C#. It then attempts to convert it to string and returns on successful conversion.
        An warning/error is raised if:
            - Warning: Not connected to C# application yet. Warning can be suppressed by setting suppressWarning=True in constructor
            - Error: If data receiving procedure or conversion to string goes wrong
            - Error: If user attempts to use this without enabling RX
        :return: returns None on failure or the received string on success
        """
        if not self.enableCom: # if RX is not enabled, raise error
            raise ValueError("Attempting to receive data without enabling this setting. Ensure this is enabled from the constructor")

        data = None
        try:
            data, _ = self.udpSock.recvfrom(1024)
            data = packet(data);
            self.PacketHandler(data); 
        except WindowsError as e:
            if e.winerror == 10054: # An error occurs if you try to receive before connecting to other application
                if not self.suppressWarnings:
                    print("Are You connected to the other application? Connect to it!")
                else:
                    pass
            else:
                raise ValueError("Unexpected Error. Are you sure that the received data can be converted to a string")

        return data

    def ReadUdpThreadFunc(self): # Should be called from thread
        """
        This function should be called from a thread [Done automatically via constructor]
                (import threading -> e.g. udpReceiveThread = threading.Thread(target=self.ReadUdpNonBlocking, daemon=True))
        This function keeps looping through the BLOCKING ReceiveData function and sets self.dataRX when data is received and sets received flag
        This function runs in the background and updates class variables to read data later
        """

        self.isDataReceived = False # Initially nothing received

        while True:
            data = self.ReceiveData()  # Blocks (in thread) until data is returned (OR MAYBE UNTIL SOME TIMEOUT AS WELL)
            self.dataRX = data # Populate AFTER new data is received
            self.isDataReceived = True
            # When it reaches here, data received is available

    def ReadReceivedData(self):
        """
        This is the function that should be used to read received data
        Checks if data has been received SINCE LAST CALL, if so it returns the received string and sets flag to False (to avoid re-reading received data)
        data is None if nothing has been received
        :return:
        """

        data = None

        if self.isDataReceived: # if data has been received
            self.isDataReceived = False
            data = self.dataRX
            print("cockssss")
            self.dataRX = None # Empty receive buffer

        return data

