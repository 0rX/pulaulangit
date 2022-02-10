from typeclasses.characters import Character

class Monster(Character):
	"""
	A Monster typeclass which extends the character class.
	"""
	def at_char_entered(self, character):
		"""
		A simple is_aggressive check.
		Can be expanded upon later.
		"""
		if self.db.is_aggressive:
			self.execute_cmd(f"say AAARRGH!! AKU AKAN MEMAKANMU HIDUP-HIDUP !!!")
		else:
			self.execute_cmd(f"say Hmmm! Apa yang kau cari di sini manusia haram ?!")

	def weapon_check(self, barang):
		if barang != self.db.weakness.lower():
			return False
		else:
			return True

	def at_cmd_getok(self, character, barang):
		"""
		A simple event checker.
		Call this when monster kena getok.
		"""
		if self.weapon_check(barang) == True:
			self.execute_cmd(f'Say AAAAAA!!! Ini ambil kuncinya brengsek!!')
			self.execute_cmd(f'drop kunci emas')
			self.execute_cmd(f'flee')
		else:
			self.execute_cmd(f'{barang} itu tidak akan mempan terhadapku!!')
	def at_cmd_tembak(self, character, barang):
		"""
		A simple event checker.
		Call this when monster kena getok.
		"""
		if self.weapon_check(barang) == True:
			self.execute_cmd(f"Say Aku akan mengingat dendam ini se-umur hidupku {character.name}!!!")
			self.execute_cmd(f"drop kristal dimensi")
			self.execute_cmd(f"flee")
		else:
			self.execute_cmd(f'{barang} itu tidak akan mempan terhadapku!!')



