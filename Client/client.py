import xmlrpclib

messages = [ "1. Lista de libros",
			 "2. Solicitar libros" ]


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

	def printBooks(server, serversBooks):
		for i in range(len(servers)):
			server = servers[i]
			books  = serverBooks[i]
			print("Servidor: " + server)
			if (len(books) == 0):
				print("No hay libros en el servidor")
			else:
				for book in books:
					print("\t" + book)

	def run(self):
		while (True):
			print("Elija un opcion: ")
			for message in messages:
				print(message)
			print()
			if ( not (option == '1' or option == '2')):
				print("Opcion invalida")
				continue
			if (option == '1')
				serverBooks = self.proxy.serversBooks()
				servers     = self.proxy.getServers()
				printBooks(server, serverBooks)
				

				
if __name__ == '__main__':
	client = Client()
	client.run()