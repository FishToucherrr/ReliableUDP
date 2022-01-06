import sys
import getopt

import Checksum
import BasicSender
import socket
import base64

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.wanted=0
        self.buf_len=0
        self.end=0
        self.packets=[]
        self.sack_mode=sackMode
        if sackMode:
            raise NotImplementedError #remove this line when you implement SACK
    
    def get_ack(self,response_packet):
        pieces = response_packet.split('|')
        ack=int(pieces[1])
        return ack
    
    def send_window(self):
        for packet in self.packets:
            # print("sent: %s" % packet)
            self.send(packet)
            
        
    
    def push_packet(self,packet):
        if self.buf_len<5:
            self.packets.append(packet)
            self.buf_len+=1
        else:
            self.packets.pop(0)
            self.packets.append(packet)
    # Main sending loop.
    def start(self):
        # raise NotImplementedError
        seqno = 0
        msg_type='start'
        msg=""

        # print("start test")
        packet = self.make_packet(msg_type,seqno,msg)
        while True:
            self.send(packet)
            c=self.receive(0.5)
            if c:
                break
        
        seqno=1
        while True:
            for i in range(5):
                msg_type='data'
                msg=self.infile.read(500)
                if msg==b"":
                    self.end=1
                    break
                msg=msg.decode('latin-1')
                
                packet = self.make_packet(msg_type,seqno,msg)
                self.push_packet(packet)
                seqno+=1

            success=0
            while True:
                if len(self.packets)==0:
                    break
                self.send_window()
                
                while True:
                    response = self.receive(0.5)
                    if response :
                        response = response.decode()
                        if self.get_ack(response) == seqno:
                            success=1
                            break
                    else:
                        break
    
                if success:
                    
                    break
            
            if self.end:
                break
        self.infile.close()

        msg_type='end'
        msg=""


        packet = self.make_packet(msg_type,seqno,msg)
        while True:
            self.send(packet)
            c=self.receive(0.5)
            if c:
                break
        

    def handle_timeout(self):
        pass

    def handle_new_ack(self, ack):
        pass

    def handle_dup_ack(self, ack):
        pass

    def log(self, msg):
        if self.debug:
            print(msg)


'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print("RUDP Sender")
        print("-f FILE | --file=FILE The file to transfer; if empty reads from STDIN")
        print("-p PORT | --port=PORT The destination port, defaults to 33122")
        print("-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost")
        print("-d | --debug Print debug messages")
        print("-h | --help Print this usage message")
        print("-k | --sack Enable selective acknowledgement mode")

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest, port, filename, debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
