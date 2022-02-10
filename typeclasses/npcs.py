from typeclasses.characters import Character
import random

class NPC(Character):
	"""
	An NPC typeclass which extends the character class.
	"""
	def at_char_entered(self, character):
		"""
		A simple is_aggressive check.
		Can be expanded upon later.
		"""
		reply = random.choice([f"Sudah bertahun tahun aku melihat kotak rahasia itu bersandar di pohon besar. Tak ada seorangpun yang pernah menemukan kuncinya.",f"{character.name}, Apa kamu sudah menemukan petunjuk untuk keluar dari tempat ini ?","Apa yang kau cari ?!",f"Selamat datang {character.name}.",f"Hari yang sangat indah. Bukankan begitu {character.name}?"])
		if self.db.is_aggressive:
			self.execute_cmd(f"say HAHAHAHA. {character.name}!! Aku akan |rmembunuhmu|n!!")
		else:
			self.execute_cmd("say "+reply)
