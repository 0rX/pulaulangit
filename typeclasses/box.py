# pulaulangit/typeclasses/box.py

from typeclasses.objects import Object

class Box(Object):
	def at_object_creation(self):
		self.db.desc = "Peti mati untuk korban perasaan"