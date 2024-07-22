class CAN_Msg:
	def __init__(self, isStd: bool, id: hex, outputCount: int, outputNames: list, outputValues: list):
		self.isStd = isStd
		self.id = id
		self.outputCount = outputCount
		self.outputNames = outputNames
		self.outputValues = outputValues
		
		self.seperators = ["q7g1y", "$sdf*", "&1dfg", "^sdf#", "LjIfT"]

	def GenerateMessage(self):
		msg = self.seperators[0] + str(self.isStd) + self.seperators[0] + str(self.id) + self.seperators[1] + str(self.outputCount) + self.seperators[2] + "".join(str(i)+self.seperators[3] for i in self.outputNames) + self.seperators[3] + "".join(str(j)+self.seperators[4] for j in self.outputValues) + self.seperators[4]
		return msg

message = CAN_Msg(isStd=1, id=0x16, outputCount=2, outputNames=["ali", "veli"], outputValues=["753", "911"])
msg = message.GenerateMessage()
print(msg)
