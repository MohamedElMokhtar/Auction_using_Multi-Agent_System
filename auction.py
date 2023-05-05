import asyncio
import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template
import time
import random

bidders = ["buyer1@yax.im", "buyer2@yax.im", "buyer3@yax.im", "buyer4@yax.im"]

start_price = random.randint(10, 100)

start = time.time()

reserve_price = random.randint(start_price+100, 350)

current_bid = start_price

continueBidding = 0

winner = ""

print("\nthe start price is :" + str(start_price))
print("the reserve price is :" + str(reserve_price) + "\n")


class Seller(Agent):
    class StartAuction(CyclicBehaviour):

        def __init__(self):
            super().__init__()
            self.round = 1

        async def run(self):

            global continueBidding

            temporary = current_bid

            if (time.time() - start) > 120:
                print("\nSeller : the time of the auction process has ended !\n")
                print("object sold to " + winner +
                      " with the price : " + str(current_bid) + "\n")
                self.kill()
            else:
                print("\n--------- Round " + str(self.round) + " ---------\n")
                print("Seller : current bid is " + str(current_bid) + "\n")

                for jid in bidders:
                    msg = Message(to=jid)
                    msg.set_metadata("performative", "inform")
                    msg.body = str(temporary)
                    await self.send(msg)
                    # print("Bid sent to " + jid)

                await asyncio.sleep(10)

                if continueBidding == -4:
                    print("\nNo biddings")
                    if current_bid >= reserve_price:
                        print("object sold to " + winner +
                              " with the price : " + str(current_bid) + "\n")
                    else:
                        print(
                            "\nObject not sold because the reserve price is not reached\n")
                    self.kill()
                else:
                    continueBidding = 0
                    self.round += 1

        async def on_end(self):
            await self.agent.stop()

    async def setup(self):
        global start
        start = time.time()
        startTime = datetime.datetime.now().strftime("%H:%M")
        print("\nThe auction has started at " + str(startTime) + " ! ")
        b = self.StartAuction()
        self.add_behaviour(b)


class Buyer(Agent):
    class RecvBehav(CyclicBehaviour):

        def __init__(self, id):
            super().__init__()
            self.id = id

        async def run(self):

            # print(self.id + "Now recieving !")
            global current_bid
            global reserve_price
            global continueBidding
            global winner

            # wait for a message for 60 seconds
            msg = await self.receive(timeout=30)
            if msg:
                x = int(msg.body)
                bid = random.randint(0, 1)
                if bid == 1 and winner != self.id:
                    amount = random.randint(1, 100)
                    price = x + amount

                    print(self.id + " has offered : " + str(price))
                    if price > current_bid:
                        current_bid = price
                        winner = self.id
                else:
                    continueBidding -= 1
            else:
                print(self.id + " has disconnected !")
                self.kill()

        async def on_end(self):
            await self.agent.stop()

    async def setup(self):
        idd = str(self.jid)
        print("buyer " + idd + " is connected !")
        b = self.RecvBehav(idd)
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)


if __name__ == "__main__":
    buyer1 = Buyer("buyer1@yax.im", "buyer1")
    buyer2 = Buyer("buyer2@yax.im", "buyer2")
    buyer3 = Buyer("buyer3@yax.im", "buyer3")
    buyer4 = Buyer("buyer4@yax.im", "buyer4")
    # buyer5 = Buyer("buyer5@jabber.fr", "buyer5")
    # buyer6 = Buyer("buyer6@jabber.fr", "buyer6")
    seller = Seller("seller@yax.im", "seller")

    future1 = buyer1.start()
    future1.wait()  # wait for receiver agent to be prepared.

    future2 = buyer2.start()
    future2.wait()  # wait for receiver agent to be prepared.

    future3 = buyer3.start()
    future3.wait()  # wait for receiver agent to be prepared.

    future4 = buyer4.start()
    future4.wait()  # wait for receiver agent to be prepared.

    # future5 = buyer5.start()
    # future5.wait()  # wait for receiver agent to be prepared.

    # future6 = buyer6.start()
    # future6.wait()  # wait for receiver agent to be prepared.

    seller.start()

    while buyer1.is_alive() or buyer2.is_alive() or buyer3.is_alive() or buyer4.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            seller.stop()
            buyer1.stop()
            buyer2.stop()
            buyer3.stop()
            buyer4.stop()
            # buyer5.stop()
            # buyer6.stop()
            break
    print("\nAuction finished\n")
