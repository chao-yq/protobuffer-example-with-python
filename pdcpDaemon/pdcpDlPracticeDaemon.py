from time import sleep

from pdcpDaemon.buffer_pb2 import stored
from pdcpDaemon.pdcp_pb2 import pdcp, manageInfo

# def init(pdcp):
#     pdcp.received_PDCP_SN = 0
#     pdcp.Last_Submitted_PDCP_RX_SN = 0
#     #pdcp.Reordering_Window = 64
#     pdcp.Next_PDCP_RX_SN = 1
#     pdcp.COUNT.RX_HFN = 0
#     pdcp.COUNT.PDCP_SN = pdcp.received_PDCP_SN
#     #pdcp.Maximum_PDCP_SN = 127


def hasReceived(received_PDCP_SN):
    if received_PDCP_SN in buffer.sn:
        return True
    else:
        return False


def process(received_PDCP_SN):
    discard = False
    pduEntity = pdcpEntity.pdu.add()

    def decipher(RX_HFN, SN):
        pduEntity.RX_HFN = RX_HFN
        pduEntity.PDCP_SN = SN
        print("decipher:")
        print(pduEntity.PDCP_SN)
        print(pduEntity.RX_HFN)

    # pduEntity.RX_HFN = manageInfo.RX_HFN

    if (received_PDCP_SN - manage.Last_Submitted_PDCP_RX_SN > manage.Reordering_Window) or \
            (0 <= (manage.Last_Submitted_PDCP_RX_SN - received_PDCP_SN) < manage.Reordering_Window):
        if received_PDCP_SN > manage.Next_PDCP_RX_SN:
            print(
                "decipher the PDCP PDU as specified in the subclause 5.6, using COUNT based on RX_HFN - 1 and the "
                "received PDCP SN")
            decipher(manage.RX_HFN - 1, received_PDCP_SN)
        else:
            print(
                "decipher the PDCP PDU as specified in the subclause 5.6, using COUNT based on RX_HFN and the "
                "received PDCP SN;")
            decipher(manage.RX_HFN, received_PDCP_SN)
        print("discard at mission 1", pduEntity.PDCP_SN)
        discard = True
    elif manage.Next_PDCP_RX_SN - received_PDCP_SN > manage.Reordering_Window:
        manage.RX_HFN += 1
        manage.Next_PDCP_RX_SN = received_PDCP_SN + 1
        print("use COUNT based on RX_HFN and the received PDCP SN for deciphering the PDCP PDU;")
        decipher(manage.RX_HFN, received_PDCP_SN)
    elif received_PDCP_SN - manage.Next_PDCP_RX_SN >= manage.Reordering_Window:
        print("use COUNT based on RX_HFN – 1 and the received PDCP SN for deciphering the PDCP PDU; ")
        decipher(manage.RX_HFN - 1, received_PDCP_SN)
    # else if received PDCP SN >= Next_PDCP_RX_SN:
    elif received_PDCP_SN >= manage.Next_PDCP_RX_SN:
        print("use COUNT based on RX_HFN and the received PDCP SN for deciphering the PDCP PDU")
        decipher(manage.RX_HFN, received_PDCP_SN)
        manage.Next_PDCP_RX_SN = received_PDCP_SN + 1
        if manage.Next_PDCP_RX_SN > manage.Maximum_PDCP_SN:
            print("received sn reached the max number, set Next_PDCP_RX_SN to 0 and start a new round ~")
            manage.Next_PDCP_RX_SN = 0
            manage.RX_HFN += 1
    elif received_PDCP_SN < manage.Next_PDCP_RX_SN:
        print("use COUNT based on RX_HFN and the received PDCP SN for deciphering the PDCP PDU;")
        decipher(manage.RX_HFN, received_PDCP_SN)
    else:
        print("missed in condition 1 ")
    if not discard:
        if hasReceived(received_PDCP_SN):
            print("discard at mission 2:")
            print(pduEntity)
            discard = True
        else:
            print("store the PDCP SDU")
            buffer.bufferSize += 1
            buffer.sn.append(received_PDCP_SN)
            print("buffer:",
                  buffer)
        # print(discard)
        if not lower_re_establish:  # the PDCP PDU received by PDCP is not due to the re-establishment of lower layers
            print("deliver to upper layers in ascending order of the associated COUNT value")
            manage.Last_Submitted_PDCP_RX_SN = received_PDCP_SN
            global lower_re_establish
            lower_re_establish = False
        elif (received_PDCP_SN == manage.Last_Submitted_PDCP_RX_SN + 1) or \
                (received_PDCP_SN == manage.Last_Submitted_PDCP_RX_SN - manage.Maximum_PDCP_SN):
            # received PDCP SN = Last_Submitted_PDCP_RX_SN + 1 or received PDCP SN = Last_Submitted_PDCP_RX_SN –
            # Maximum_PDCP_SN
            # { -	deliver to upper layers in ascending order of the associated COUNT value: -	all stored PDCP SDU(s)
            # with consecutively associated COUNT value(s) starting from the COUNT value associated with the received
            # PDCP SDU; -	set Last_Submitted_PDCP_RX_SN to the PDCP SN of the last PDCP SDU delivered to upper
            # layers.}
            print(" TBD~ ")
    # print("discard value:", discard)


# init
lower_re_establish = False
storedBuffer = stored()
buffer = storedBuffer.buffer
buffer.bufferSize = 0
# buffer.sn.append(1)
print(buffer)

manage = manageInfo()
manage.Reordering_Window = 64
manage.Maximum_PDCP_SN = 127
manage.RX_HFN = 0
manage.Last_Submitted_PDCP_RX_SN = 0
manage.Next_PDCP_RX_SN = -1
print(manage)
pdcpEntity = pdcp()

# Start procedure
while True:
    print("input SN or Y for auto input: ")
    # pdcp.pdu.append(int(input()))
    # process(pdcp.received_PDCP_SN)
    value = input()
    if str(value) == "Y":
        for i in range(1, 127):
            process(i)
        print(manage)
    elif str(value) == "S":
        exit()
    elif value == "buffer":
        print(buffer)
    elif str(value) == "R":
        lower_re_establish = True;
    elif value.isdigit():
        if 0 < int(value) < 2147483647:
            process(int(value))
            print(manage)
            sleep(1)
        else:
            print("input int value out of range! ")
    else:
        print("invalid input")
    # print("buffer: ", buffer)
