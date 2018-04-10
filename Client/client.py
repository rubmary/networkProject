import xmlrpclib


class Client:
	def __init__(self, central = "http://localhost:8000", client = "c"):
		self.proxy  = xmlrpclib.ServerProxy(central)
		self.proxy.registerClient(client)

	def requestBook(self):
		print("Solicitando libro")
		book = raw_input()
		servers = self.proxy.requestBook("rubmary", book)
		print("El libro esta disponible en los servidores")
		print(servers)

	def run(self):
		while (True):
			print("Escriba una opcion")
			option = raw_input()
			if (option == "book"):
				self.requestBook()
				
if __name__ == '__main__':
	client = Client()
	client.run()