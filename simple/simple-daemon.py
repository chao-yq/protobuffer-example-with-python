
import simple.simple_pb2 as simple_pb2

simpleMessage = simple_pb2.SimpleMessage()
simpleMessage.id = 123
simpleMessage.is_simple = True
simpleMessage.name = "This is a simpleMessage"
simpleMessage.sample_list.append(1)
print(simpleMessage)
