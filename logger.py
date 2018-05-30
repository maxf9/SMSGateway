from time import strftime

class Logger:

	@staticmethod
	def info(log):
		print(strftime("(%d.%m.%Y) %Hh:%Mm:%Ss") + "\033[92m INFO \033[0m" + log)

	@staticmethod
	def warning(log):
		print(strftime("(%d.%m.%Y) %Hh:%Mm:%Ss") + "\033[93m WARNING \033[0m" + log)

	@staticmethod
	def error(log):
		print(strftime("(%d.%m.%Y) %Hh:%Mm:%Ss") + "\033[1;31m ERROR \033[1;m" + log)