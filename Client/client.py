from xmlrpclib import ServerProxy
from os import remove
from time import sleep
from thread import start_new_thread
from multiprocessing import Pool
from sys import exit
import socket


centralServerDir = "http://159.90.9.10:9513"
messages = [ "1. Listar libros.",
			 "2. Solicitar libro." ]


def transferData(params):
	server         = params[0] 
	clientName     = params[1]
	book           = params[2]
	chunkSize      = params[3]
	actualChunck   = params[4]
	last           = params[5]
	central        = params[6]
	triesPerServer = 0
	downloadServer = ServerProxy(server)
	while(triesPerServer < 3):
		try:
			binary = downloadServer.transferData(clientName, book, chunkSize, actualChunck, last)
			downloadServer.updateStatistics(0,clientName, book)
			downloadServer.updateStatistics(1,clientName, book)
			return binary.data
		except:
			triesPerServer = triesPerServer + 1
			sleep(1)
	try:
		proxy = ServerProxy(centralServerDir)
		proxy.updateStatistics(2,downloadServer)
	except:
		pass
	print("No se logro establecer conexion con el servidor de descarga " + server + ".")
	return False


class Client:
	def __init__(self, central = centralServerDir,):
		name = raw_input("Ingrese su nombre: ")
		name = name + "-159.90.9.14"
		self.clientName = name
		try:
			self.proxy = ServerProxy(central)
			self.proxy.registerClient(self.clientName)
		except:
			print("No se logro establecer conexion con el servidor central.")
			exit()

	def downloadBook(self, book):
		try:
			servers = self.proxy.requestBook(self.clientName, book)
		except:
			print("No se logro establecer conexion con el servidor central.")

		if (not servers):
			print(book + " no esta disponible en ningun servidor.")
		else:		
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
			fileChunks = [[] for i in range(nServers)]
			actualChuncks = [i + 1 for i in range(nServers)]
			while (totalTries < 5):
				try:
					servers = self.proxy.requestBook(self.clientName, book)
				except:
					totalTries = totalTries + 1
					continue

				if (not servers):
					totalTries = totalTries + 1
					continue

				params = [ [ servers[i], 
						 self.clientName,
						 book,
						 chunkSize,
						 actualChuncks[i],
						 actualChuncks[i] == nServers,
						 centralServerDir ] 
						for i in range(min(len(servers), len(actualChuncks))) ]
				
				p = Pool(5)
				results = p.map(transferData, params)
				for i in range(len(actualChuncks)):
					fileChunks[actualChuncks[i]-1] = results[i]
				
				actualChuncks = [ i + 1 for i in range(len(servers)) if results[i] == False]				
				if (not actualChuncks):
					break

				

				
			for data in fileChunks:
					downloadFile.write(data)
			downloadFile.close()
			if (successfulDownload):
				print("Descarga exitosa de " + book + ".")
			else:
				remove(path)		
				print("No se logro establecer conexion con ningun servidor de descarga.")
				print("Descarga fallida de " + book + ".")

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
				start_new_thread(self.downloadBook,(book,))

if __name__ == '__main__':
	client = Client()
	client.run()
