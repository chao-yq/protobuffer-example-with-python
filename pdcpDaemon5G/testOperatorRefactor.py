from pdcpDaemon5G.buffer_pb2 import stored
from pdcpDaemon5G.pdcp_pb2 import pdcp, COUNT


class test:
    def __lt__(left, other):
        return left.SN < other.SN

    left = COUNT()
    right = COUNT()
    left.SN = 1
    left.HFN = 1
    right.SN = 2
    right.HFN = 1
    print(left < right)
