import cmd, threading, time
from peer import Peer

"""
Define protocol

0 a 1 - send a 1 coin
1 y/n - vote yes or no

"""
default_money = 10

class BadblockchainCli(cmd.Cmd):
    prompt = ">>> "
    intro = "hi welcome to this blockchain network :D\nPlease type help for a list of commands"
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
        """Usage: connect [port1] [port2] ... [portn] \nConnect to node/s on port/s"""
        if self.node:
            for p in line.split():
                self.node.connect(self.default_host, int(p))
                self.num_nodes += 1
    
    def do_list(self, line):
        """List the blockchain"""
        print(f"{self.node.port} blockchain : ", self.chain)

    def do_send(self, line):
        """Usage: send [port] [amount]\nSend $amount to node on port """
        data = ["0", self.node.port]
        data.extend(line.split())
        if self.node:
            # if sender has enough coins to make a valid transaction
            if int(data[-1]) <= int(self.getBalance(str(self.node.port))):
                self.nextBlock = {"d": data[1:], "y": 1, "n": 0}   
                if self.node:
                    self.node.send_data(" ".join(str(x) for x in data))
                    time.sleep(10) # give 
            else: print("Not enough funds")
    """
    TODO: Finish this function that traverses the blockchain  
    and returns how many coins a user/port has

    Remember the format each entry in the blockchain has 
    [ [a, b, 2], [b, c, 2], [a, c, 3] ]

    Would illustrate the following events in order:
        a sends b 2 coins
        b sends c 2 coins
        a sends c 3 coins

    Assume each user starts with default_money (10) coins

    """
    def getBalance(self, user):
        balance = default_money
	pass 

    """
    Function that runs in the background checking for 
    incoming messages to this node. 
    """
    def check(self):
        while True:
            time.sleep(5) # run every 5s to not overload pc
            if self.node:
                while self.node.latest != []:
                    data = self.node.latest.pop().split()
                    if data[0] == "0":
                        print(f"Requesting transaction {data[1:]} to be added blockchain")
                        user = data[1]
                        sender_amount = int(data[3])
                        sender_balance = self.getBalance(user)
                        print(f"{user} has {sender_balance} coins")
                        self.nextBlock = {"d": data[1:], "y": 1, "n": 0}
                        
                        # if amount is greater than the number of coins 
                        # the sender has, mark the transaction as invalid

                        if (sender_amount > sender_balance): 
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
                        self.chain.append(self.nextBlock["d"])
                        self.nextBlock = None
                
    """Function to Vote Yes on the current request"""
    def yes(self):
        if self.nextBlock:
            self.nextBlock["y"] += 1
            self.node.send_data("1 y")

    """Function to Vote No on the current request"""
    def no(self):
        if self.nextBlock:
            self.nextBlock["n"] += 1 
            self.node.send_data("1 n")
    
    def do_numNodes(self, line):
        """Print the number of nodes on this network"""
        print(f"number of nodes: {self.num_nodes}")

    def do_quit(self, line):
        """Exit the CLI."""
        return True

if __name__ == '__main__':
    BadblockchainCli().cmdloop()
