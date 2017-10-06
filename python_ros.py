import rosbag
import sys

bagfile = sys.argv[1]  # bagfile name

print("bagfile: {}".format(bagfile))
print("num args: {}".format(len(sys.argv)))

num_topics = len(sys.argv) - 2

print("num topics: {}".format(num_topics))

topics = []
for i in range(0, num_topics):
	topic = sys.argv[i + 2]
	topics.append(topic)

print("topics: {}".format(topics))
# print(type(topics))

bag = rosbag.Bag(bagfile)

for topic, msg, t in bag.read_messages(topics=topics):
	print("message: {}".format(msg))

bag.close()


# class PyBags(object):
# 	"""
# 	rosbag python api class.
# 	streamlining data analysis of bagfiles.
# 	"""

# 	def __init__(self, bagfile):
# 		self.bagfile = bagfile
# 		self.bag = rosbag.Bag(self.bagfile)

# 		print("bagfile: {}".format(self.bagfile))


# 	def loop_topics(self, topics):
# 		print("looping topics: {}".format(topics))
# 		# for topic, msg, t in bag.read_messages(topics=['vel', 'fix']):
# 		for topic, msg, t in self.bag.read_messages(topics):
# 			print("message: {}".format(msg))

# 		print("closing bagfile")

# 	def close_bag(self):
# 		self.bag.close()
# 		print("bag closed..")