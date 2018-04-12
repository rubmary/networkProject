from xmlrpclib import ServerProxy
from os import remove
from time import sleep
from thread import start_new_thread

centralServerDir = "http://localhost:8000"
messages = [ "1. Listar libros.",
			 "2. Solicitar libro." ]

class Client:
	def __init__(self, central = centralServerDir, name = "c"):
		self.clientName = name
		self.proxy = ServerProxy(central)
		self.proxy.registerClient(self.clientName)

	def downloadBook(self, book):
		servers = self.proxy.requestBook("rubmary", book)
		if (servers):
			print(book + " esta disponible en los servidores.")
			nServers = len(servers)
			successfulDownload = True
			totalTries = 0
			triesPerServer = 0
			i = 0
			while(successfulDownload):
				try:
					if (totalTries < nServers):
						if (triesPerServer < 2):
							downloadServer = ServerProxy(servers[i])
							size = downloadServer.bookSize(book)
							break
						else:
							totalTries = totalTries + 1
							try:
								self.proxy.updateStatistics(2,servers[i])
							except:
								print("No se logro establecer conexion con el servidor central.")
							print("No se logro establecer conexion con el servidor de descarga " + servers[i] + ".")
						i = (i + 1) % nServers
						triesPerServer = 0
					else:
						successfulDownload = False
				except:
					triesPerServer = triesPerServer + 1
					sleep(3)
			path = "Libros Descargados/" + book + ".pdf"
			downloadFile = open(path,'wb')
			chunkSize = size/nServers
			totalTries = 0
			triesPerServer = 0
			i = 0
			actualChunck = 1
			while(actualChunck <= nServers and successfulDownload):
				try:
					if (totalTries < nServers):
						if (triesPerServer < 3):
							downloadServer = ServerProxy(servers[i])
							binary = downloadServer.transferData(self. clientName, book, chunkSize, actualChunck, actualChunck==nServers)
							downloadFile.write(binary.data)
							downloadServer.updateStatistics(0,self.clientName, book)
							downloadServer.updateStatistics(1,self.clientName, book)
							actualChunck = actualChunck + 1
						else:
							totalTries = totalTries + 1
							try:
								self.proxy.updateStatistics(2,servers[i])
							except:
								print("No se logro establecer conexion con el servidor central.")
							print("No se logro establecer conexion con el servidor de descarga " + servers[i] + ".")
						i = (i + 1) % nServers
						triesPerServer = 0
					else:
						successfulDownload = False
				except:
					triesPerServer = triesPerServer + 1
					sleep(1)
			downloadFile.close()
			if (successfulDownload):
				print("Descarga exitosa de " + book + ".")
			else:
				remove(path)		
				print("No se logro establecer conexion con ningun servidor de descarga.")
				print("Descarga fallida de " + book + ".")		
		else:
			print(book + " no esta disponible en ningun servidor.")

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
				start_new_thread(self.downloadBook,(book,))

if __name__ == '__main__':
	client = Client()
	client.run()