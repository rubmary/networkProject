import xmlrpclib

messages = [ "1. Lista de libros",
			 "2. Solicitar libros" ]


class Client:
	def __init__(self, central = "http://localhost:8000", client = "c"):
		self.proxy  = xmlrpclib.ServerProxy(central)
		self.proxy.registerClient(client)

	def requestBook(self):
		book = raw_input("Escriba el nombre del libro: ")
		servers = self.proxy.requestBook("rubmary", book)
		print("El libro esta disponible en los servidores")
		print(servers)
		return servers

	def getBooks(self):
		serversBooks = self.proxy.serversBooks()
		servers      = self.proxy.getServers()
		for i in range(len(servers)):
			server = servers[i]
			books  = serversBooks[i]
			print("Servidor: " + server)
			if (len(books) == 0):
				print("No hay libros en el servidor")
			else:
				for book in books:
					print("\t" + book)
			print

	def run(self):
		while (True):
			print("Elija un opcion: ")
			for message in messages:
				print(message)
			option = raw_input()
			if ( not (option == '1' or option == '2')):
				print("Opcion invalida")
				continue
			if  (option == '1'):
				self.getBooks()
			elif(option == '2'):
				servers = self.requestBook()

				
if __name__ == '__main__':
	client = Client()
	client.run()