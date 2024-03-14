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
            self.node.connect(self.default_host, int(line.split()[0]))
            self.num_nodes += 1
    
    def do_list(self, line):
        """List the blockchain"""
        print("blockchain : ", self.chain)

    def do_add(self, line):
        """Usage: add [from] [to] [amount]\nAdd transaction to blockchain"""
        self.nextBlock = {"d": line, "y": 1, "n": 0}   
        if self.node:
            self.node.send_data("0 " + line + " " + str(self.node.coins))
            time.sleep(10)

    def do_next(self, line): print(self.nextBlock)

    def check(self):
        while True:
            time.sleep(5)
            if self.node:
                while self.node.latest != []:
                    print(self.node.latest)
                    data = self.node.latest.pop().split()
                    if data[0] == "0":
                        print("Requesting " + data + " to the blockchain")
                        self.nextBlock = {"d": data[1], "y": 0, "n": 0}
                        if (data[2] >= data[3]): 
                            print("This transaction is invalid")
                            self.no()
                        else: self.yes()
                    if data[0] == "1" and self.nextBlock:
                        if (data[1] == "y"): self.nextBlock["y"] += 1
                        else: self.nextBlock["n"] += 1
                        self.n = {"d": data[1], "y": 0, "n": 0}
                if self.nextBlock:
                    if (self.nextBlock["y"] > self.nextBlock["n"]): 
                        self.chain.append(self.nextBlock["d"])
                        self.nextBlock = None
                
    def yes(self, line):
        if self.nextBlock:
            self.nextBlock["y"] += 1
            self.node.send_data("1 y")
    
    def no(self, line):
        if self.nextBlock:
            self.nextBlock["n"] += 1 
            self.node.send_data("1 n")


    # def do_check(self, line):
    #     """Check for any pending additions to the chain"""
    #     # print(self.node.latest)
    #     if self.node.latest:
    #         print("found pending")

    def do_hello(self, line):
        """Print a greeting."""
        print(line)
        print("Hello, World!")

    def do_quit(self, line):
        """Exit the CLI."""
        return True

if __name__ == '__main__':
    blockchainCli().cmdloop()