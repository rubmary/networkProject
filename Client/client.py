import xmlrpclib
from os import remove

messages = [ "1. Lista de libros",
			 "2. Solicitar libros" ]


class Client:
	def __init__(self, central = "http://localhost:8000", client = "c"):
		self.proxy  = xmlrpclib.ServerProxy(central)
		self.proxy.registerClient(client)

	def downloadBook(self, book):
		servers = self.proxy.requestBook("rubmary", book)
		if (servers):
			print("El libro esta disponible en los servidores.")
			print(servers)
			# Manejar posible caida.
			downloadServer = xmlrpclib.ServerProxy(servers[0])
			size = downloadServer.bookSize(book)
			print(size)
			path = "Libros Descargados/" + book + ".pdf"
			downloadFile = open(path,'wb')
			successfulDownload = True
			nServers = len(servers)
			chunkSize = size/nServers
			totalTries = 0
			triesPerServer = 0
			i = 0
			actualChunck = 1
			while(actualChunck <= nServers):
				try:
					if (totalTries < nServers * 2):
						if (triesPerServer < 3):
							downloadServer = xmlrpclib.ServerProxy(servers[i])
							binary = downloadServer.transferData(book, chunkSize, actualChunck, actualChunck==nServers)
							print(len(binary.data))
							downloadFile.write(binary.data)
							actualChunck = actualChunck + 1
						else:
							totalTries = totalTries + 1
							print("No se logro establecer conexion con el servidor de descarga " + servers[i])
						i = (i + 1) % nServers
						triesPerServer = 0
					else:
						successfulDownload = False
				except:
					triesPerServer = triesPerServer + 1
					#wait(1)
			downloadFile.close()
			if (successfulDownload):
				print("Descarga exitosa.")
			else:
				remove(path)		
				print("No se logro establecer conexion con ningun servidor de descarga.")
				print("Descarga fallida.")		
		else:
			print("El libro no esta disponible en ningun servidores.")

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
				book = raw_input("Escriba el nombre del libro: ")
				# Ejecutar esto en un hilo.
				servers = self.downloadBook(book)

				
if __name__ == '__main__':
	client = Client()
	client.run()