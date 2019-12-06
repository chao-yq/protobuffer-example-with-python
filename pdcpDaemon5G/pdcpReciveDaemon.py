from time import sleep

import self

from pdcpDaemon5G.pdcp_pb2 import pdcp, COUNT, pdu, stored


def hasReceivedBefore(RCVD_COUNT):
    for sdu in RecivedBuffer.sdu:
        if sdu.RCVD_COUNT == RCVD_COUNT:
            return True
    return False


def deliverAll(RX_DELIV):
    # -	all stored PDCP SDU(s) with consecutively associated COUNT value(s) starting from COUNT = RX_DELIV; update
    # RX_DELIV to the COUNT value of the first PDCP SDU which has not been delivered to upper layers, with COUNT
    # value > RX_DELIV;
    # print(StoredBuffer.ListFields())
    for sdu in StoredBuffer.sdu:
        if Count(sdu.RCVD_COUNT) == RX_DELIV:
            deliver(RX_DELIV)
            RX_DELIV.SN += 1
    pdcpEntity.state.RX_DELIV.SN = RX_DELIV.SN
    pdcpEntity.state.RX_DELIV.HFN = RX_DELIV.HFN
    if RX_DELIV.SN >= pdcpEntity.state.Window_Size:
        pdcpEntity.state.RX_DELIV.SN = 1
        pdcpEntity.state.RX_DELIV.HFN += 1

    # pdcpEntity.state.RX_DELIV.MergeFrom(RX_DELIV)
    pass


def deliver(RX_DELIV):
    for sdu in StoredBuffer.sdu:
        if sdu.RCVD_COUNT == RX_DELIV:
            StoredBuffer.sdu.remove(sdu)
            # print("delivered")


# test1 = COUNT()
# test1 = C()
#
# test1.HFN = 1
# test1.SN = 4
# test = COUNT()
# test.SN = 3
# test.HFN = 1
# print(test1 < test)

class Count:
    def __init__(self, count):
        self.SN = count.SN
        self.HFN = count.HFN

    def __lt__(self, dst):
        if self.HFN < dst.HFN:
            return True
        elif self.HFN == dst.HFN:
            return self.SN < dst.SN
        else:
            return False

    def __le__(self, other):
        return (self < other) or (self == other)

    def __eq__(self, other):
        return (self.HFN == other.HFN) and (self.SN == other.SN)

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        if self.HFN >= other.HFN:
            return True
        elif self.HFN == other.HFN:
            return self.SN >= other.SN
        else:
            return False

    def __add__(self, other):
        self.SN = self.SN + other


def process(RCVD_SN):
    pdcpEntity.state.SN = RCVD_SN
    RX_DELIV = pdcpEntity.state.RX_DELIV
    Window_Size = pdcpEntity.state.Window_Size
    RCVD_COUNT = COUNT()
    RCVD_COUNT.SN = RCVD_SN
    pduEntity = pdu()
    discard = False

    # RX_NEXT = pdcpEntity.state.RX_NEXT
    # if RCVD_SN < SN(RX_DELIV) – Window_Size:
    if RCVD_SN < RX_DELIV.SN - Window_Size:
        RCVD_COUNT.HFN = RX_DELIV.HFN + 1
        pdcpEntity.state.HFN += 1
    elif RCVD_SN >= RX_DELIV.SN + Window_Size:
        RCVD_COUNT.HFN = RX_DELIV.HFN - 1
    else:
        RCVD_COUNT.HFN = RX_DELIV.HFN
    # print("RCVD_COUNT = [RCVD_HFN, RCVD_SN]: [", RCVD_COUNT.HFN, ",", RCVD_COUNT.SN, "]")
    # pduEntity.RCVD_COUNT = RCVD_COUNT
    # recived.MergeFrom(pduEntity)
    print("perform deciphering and integrity verification of the PDCP Data PDU using COUNT:  [", RCVD_COUNT.HFN, ",",
          RCVD_COUNT.SN, "]")
    # if integrity verification fails:
    if not verification:
        print("indicate the integrity verification failure to upper layer;")
        print("discard the PDCP Data PDU;")
        discard = True
    # if RCVD_COUNT < RX_DELIV; or if the PDCP Data PDU with COUNT = RCVD_COUNT has been received before:
    # print((RCVD_COUNT < RX_DELIV))!!!!!!!!!!!!!!!!!!!!!!!!
    # using to compare
    # print("test:", (RCVD_COUNT < RX_DELIV))
    # print("test:", RCVD_COUNT)
    # print("RCVD_COUNT) < RX_DELIV:", (Count(RCVD_COUNT) < RX_DELIV))
    # print("hasReceivedBefore:", hasReceivedBefore(RCVD_COUNT))
    if (Count(RCVD_COUNT) < RX_DELIV) or hasReceivedBefore(RCVD_COUNT):
        discard = True
        print("discard the PDCP Data PDU DUE to dup recived ")
    if not hasReceivedBefore(RCVD_COUNT):
        pduEntity.RCVD_COUNT.MergeFrom(RCVD_COUNT)
        RecivedBuffer.sdu.append(pduEntity)
        RecivedBuffer.bufferSize += 1
        # print("RBuffer:", RecivedBuffer)
    if not discard:
        # -	store the resulting PDCP SDU in the reception buffer;
        StoredBuffer.sdu.append(pduEntity)
        StoredBuffer.bufferSize += 1
        if Count(RCVD_COUNT) >= pdcpEntity.state.RX_NEXT:
            # update RX_NEXT to RCVD_COUNT + 1
            pdcpEntity.state.RX_NEXT.SN = RCVD_COUNT.SN + 1
            pdcpEntity.state.RX_NEXT.HFN = RCVD_COUNT.HFN
            if pdcpEntity.state.RX_NEXT.SN >= pdcpEntity.state.Window_Size:
                pdcpEntity.state.RX_NEXT.SN = 1
                pdcpEntity.state.RX_NEXT.HFN += 1
                pdcpEntity.state.HFN += 1
        # if outOfOrderDelivery is configured:
        if outOfOrderDelivery:
            print("deliver the resulting PDCP SDU to upper layers:")
            deliver(RCVD_COUNT)
            # print(pduEntity)
        if Count(RCVD_COUNT) == pdcpEntity.state.RX_DELIV:
            print(
                "deliver to upper layers in ascending order of the associated COUNT value after performing header "
                "decompression, if not decompressed before;")
            deliverAll(RX_DELIV)
        if (pdcpEntity.state.t_Reordering != 0) and (Count(RX_DELIV) >= pdcpEntity.state.RX_REORD):
            # stop and reset t-Reordering.
            print("stop and reset t-Reordering.")
            pdcpEntity.state.t_Reordering = 0
        if (pdcpEntity.state.t_Reordering == 0) and (Count(RX_DELIV) < pdcpEntity.state.RX_NEXT):
            pdcpEntity.state.RX_REORD.MergeFrom(pdcpEntity.state.RX_NEXT)
            # start t-Reordering
            print("start t-Reordering   TBD!")


# Actions when a t-Reordering expires
def tExpires():
    pass


# Actions when the value of t-Reordering is reconfigured
def tReConfigured(timer):
    pass


def initPdcp():
    pdcpSNSize = 7
    pdcpEntity.state.HFN = 1
    pdcpEntity.state.SN = 1
    pdcpEntity.state.RX_NEXT.SN = pdcpEntity.state.SN + 1
    pdcpEntity.state.RX_NEXT.HFN = pdcpEntity.state.HFN
    pdcpEntity.state.RX_DELIV.SN = pdcpEntity.state.SN
    pdcpEntity.state.RX_DELIV.HFN = pdcpEntity.state.HFN
    pdcpEntity.state.RX_REORD.SN = pdcpEntity.state.SN
    pdcpEntity.state.RX_REORD.HFN = pdcpEntity.state.HFN
    pdcpEntity.state.t_Reordering = pdcpEntity.state.SN
    pdcpEntity.state.Window_Size = 2 ** pdcpSNSize - 1
    # print(pdcpEntity.state.Window_Size)
    # print(pdcpEntity)


# start
verification = True
outOfOrderDelivery = False
# init PDCP
pdcpEntity = pdcp()
initPdcp()
# print(pdcpEntity)

# init buffer
RecivedBuffer = stored()
RecivedBuffer.bufferSize = 0
StoredBuffer = stored()
StoredBuffer.bufferSize = 0

# test code
# pduExample = pdcpEntity.pdu.add()
# pduExample.RCVD_COUNT.SN = 1
# pduExample.RCVD_COUNT.HFN =1
# RCVD_COUNT = [pduExample.RCVD_COUNT.RCVD_SN, pduExample.RCVD_COUNT.RCVD_HFN]
# print(pduExample)
# print(RCVD_COUNT)
while True:
    print("input SN or Y for auto input: ")
    # pdcp.pdu.append(int(input()))
    # process(pdcp.received_PDCP_SN)
    value = input()
    if str(value) == "Y":
        for i in range(1, pdcpEntity.state.Window_Size):
            process(i)
    elif str(value) == "S":
        break
    elif value == "buffer":
        print(RecivedBuffer)
    elif value == "print":
        # print("RecivedBuffer: ", RecivedBuffer)
        print("StoredBuffer : ", StoredBuffer)
        print("pdcpEntity: ", pdcpEntity)
    elif str(value) == "R":
        lower_re_establish = True
    elif value.isdigit():
        if 0 < int(value) < 2147483647:
            process(int(value))
            sleep(1)
        else:
            print("input int value out of range! ")
    else:
        print("invalid input")
# print(RecivedBuffer)
