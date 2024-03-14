import cmd, threading, time
from peer import Peer

"""
Define protocol

0 a - request a
1 y/n - vote yes or no

"""

class blockchainCli(cmd.Cmd):
    prompt = ">>> "
    intro = "hi welcome"
    default_host = "0.0.0.0"

    nextBlock = None
    chain = []

    node = None
    num_nodes = 0    

    def do_init(self, line):
        """Usage: init [port] \nStart a node on port"""
        self.node = Peer(self.default_host, int(line.split()[0]))
        self.node.start()
        threading.Thread(target=self.check).start()
        self.num_nodes += 1

    def do_connect(self, line):
        """Usage: connect [port] \nConnect to node on port"""
        if self.node:
            for p in line.split():
                self.node.connect(self.default_host, int(p))
                self.num_nodes += 1
    
    def do_list(self, line):
        """List the blockchain"""
        print("blockchain : ", self.chain)

    def do_send(self, line):
        """Usage: send [to] [amount]\nSend [to] some $"""
        data = ["0", self.node.port]
        data.extend(line.split())
        data.append(self.node.coins)
        self.nextBlock = {"d": data[1:], "y": 1, "n": 0}   
        if self.node:
            self.node.send_data(" ".join(str(x) for x in data))
            self.node.coins -= int(data[-1])
            time.sleep(10)

    def do_next(self, line): print(self.nextBlock)

    """
    TODO: change this function so that you are able to add invalid transactions
    (don't overthink this read the comments)
    """
    def check(self):
        while True:
            time.sleep(5)
            if self.node:
                while self.node.latest != []:
                    # print(self.node.latest)
                    data = self.node.latest.pop().split()
                    if data[0] == "0":
                        print(f"Requesting transaction {data[1:4]} to be added blockchain")
                        print(f"{data[1]} has {data[4]} coins")
                        self.nextBlock = {"d": data[1:], "y": 0, "n": 0}
                        
                        # if amount is greater than the number of coins 
                        # the sender has, mark the transaction as invalid
                        if (data[3] > data[4]): 
                            print("This transaction is invalid. Voting No")
                            self.no() # vote no
                        else: 
                            print("This transaction is valid. Voting Yes")
                            self.yes() # vote yes

                    if data[0] == "1" and self.nextBlock:
                        if (data[1] == "y"): self.nextBlock["y"] += 1
                        else: self.nextBlock["n"] += 1
                        self.n = {"d": data[1:], "y": 0, "n": 0}
                if self.nextBlock:
                    if (self.nextBlock["y"] > self.nextBlock["n"]): 
                        self.chain.append(self.nextBlock["d"][:-1])
                        self.nextBlock = None
                
    def yes(self):
        if self.nextBlock:
            self.nextBlock["y"] += 1
            self.node.send_data("1 y")
    
    def no(self):
        if self.nextBlock:
            self.nextBlock["n"] += 1 
            self.node.send_data("1 n")


    def do_hello(self, line):
        """Print a greeting."""
        print(line)
        print("Hello, World!")

    def do_quit(self, line):
        """Exit the CLI."""
        return True

if __name__ == '__main__':
    blockchainCli().cmdloop()