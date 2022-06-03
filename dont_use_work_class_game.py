import random


class GameExtraWord:
	text_rules = "Задание игры: Найди лишнее слово"
	url_picRules = open('snippet.jpg', 'rb')

	def __init__(self, file_name = 'set_of_words.txt'):
		load_possible_texts = self.load_tasks_from_file(file_name)  # загружаем все возможные тексты и создаем список словарей
		# print(load_possible_texts)
		if load_possible_texts:
			self.all_possibile_texts = load_possible_texts
			self.used_texts = []  # сюда добавим использованные текста
			self.rating = 0  # сюда добавим заработанные очки игрока
			self.game_finish = False
			self.word_extra = ''
			self.actual_shuffled_list = []
			self.get_shuffled_to_give_user()


	def load_tasks_from_file(self, file_name):
		texts_to_output = []
		with open(file_name, 'r', encoding = 'utf-8') as f:
			for line in f:
				union_dict = {}

				united_list = (line.split("\\"))

				right_words = united_list[0]
				wrong_words = united_list[1]

				list_of_right_words = right_words.split()
				# print(f'правильные слова: {list_of_right_words}')

				list_of_wrong_words = wrong_words.split()
				# print(f'неправильное слов: {list_of_wrong_words}')

				union_dict['right'] = list_of_right_words
				union_dict['wrong'] = list_of_wrong_words
				texts_to_output.append(union_dict.copy())

		return texts_to_output

	def get_clear_list(self):
		list_to_output = []  # те наборы, которые можно использовать
		for item in self.all_possibile_texts:
			if item not in self.used_texts:
				list_to_output.append(item)
		if list_to_output:
			return list_to_output
		else:
			return None

	def get_random_text_dict(self):
		got_clear_list = self.get_clear_list()

		if got_clear_list:
			random_dict = random.choice(got_clear_list)
			self.used_texts.append(random_dict)
			return random_dict
		else:
			return None

	def get_shuffled_to_give_user(self):
		random_dict = self.get_random_text_dict()

		if random_dict:
			extra_word = random_dict['wrong'][0]

			# print(extra_word, "extra_word")
			# print(type(extra_word))
			right_word = random_dict['right']

			new_list = right_word.copy()
			new_list.append(extra_word)

			random.shuffle(new_list)



			self.word_extra = extra_word
			self.actual_shuffled_list = new_list

		else:
			self.word_extra = ''
			self.actual_shuffled_list = [] # если ничего не пришло, ставим в переменную ничего


	def result_of_round(self, player_choice):
		result = ''

		if player_choice == self.word_extra:
			self.rating += 100
			result = 'Ответ верный'
		else:
			if self.rating >= 50:
				self.rating -= 50
			result = 'Ответ не верный'

		self.get_shuffled_to_give_user()

		if self.rating >= 300:
			self.game_finish = True
			return  f""" {player_choice}  {result}. Очки: {self.rating} ! Игра окончена: вы победили"""

		if not self.actual_shuffled_list:
			return f""" {player_choice}  {result}. Очки: {self.rating} ! Игра окончена: больше нет раундов"""

		return f""" {player_choice}  {result}. Очки: {self.rating}"""


# game_extra_word = GameExtraWord()
# for i in range(1, 10):
#
# 	print(game_extra_word.actual_shuffled_list, 'перемешанный список сейчас показывается')
# 	print(game_extra_word.word_extra, 'лишнее слово')
# 	print(game_extra_word.used_texts, 'список использованных')
# 	print(game_extra_word.result_of_round('d'))
	# print(game_extra_word.result_of_round(game_extra_word.word_extra))



