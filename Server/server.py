#!/usr/bin/env python
from __future__ import print_function
import threading
import time
from xmlrpclib import ServerProxy, Binary
from SimpleXMLRPCServer import SimpleXMLRPCServer,SimpleXMLRPCRequestHandler
import SocketServer
from os import stat,walk
from ast import literal_eval
from sys import exit

'''
Archivo que implementa la clase servidor de descarga, encargado de proporcionar los
metodos utilizados para descargar un libro y solicitar sus datos.
'''
class AsyncXMLRPCServer(SocketServer.ThreadingMixIn,SimpleXMLRPCServer): pass

centralServerDir = "http://localhost:8000"
serverDir = "http://localhost:8121"
nameFileStatics = "statistics.txt"
messages = [ "1. Libros en descarga.",
			 "2. Libros descargados.",
			 "3. Estadisticas de clientes." ]
currentDownloads = {}

'''
Metodo utilizado para cargar la lista de libros en el directorio y notificar al servidor central. 
'''
def uploadBookList():
	books = []
	for root,dir,file in walk("Libros"):
		for f in file:
			books.append(f.split('.')[0])
	return books

'''
Metodo para revisar si un libro existe en el servidor.

book: libro a revisar.
'''
def checkBook(book):
	print("checking book in server")
	for b in server.books:
		if (b == book):
			return True
	return False

'''
Metodo que retorna el tam de un libro en el servidor.

book: libro a revisar.
'''
def bookSize(book):
	path = "Libros/" + book + ".pdf"
	print(path)
	return stat(path).st_size

'''
Metodo que se encarga de transferir data entre un cliente, un libro y un trozo del mismo especificado
por los parametros chunkSize y actualChunk

client: cliente al que se transferiran los archivos
book: libro a transferir
chunkSize: tamanho del bloque a transferir
actualChunk: bloque por el cual va la descarga
isLast: booleano para saber si es el ultimo bloque.
'''
def transferData(client, book, chunkSize, actualChunk, isLast):
	if (not client in currentDownloads):
		currentDownloads[client] = []
	currentDownloads[client].append(book)	
	print("Transfiriendo data...")
	path = "Libros/" + book + ".pdf"
	file = open(path, "rb")
	file.read(chunkSize * (actualChunk - 1))
	if (isLast):
		f = file.read()
	else:
		f = file.read(chunkSize)
	file.close()
	return Binary(f)


'''
Metodo que retorna la lista de libros del servidor
'''
def booksList():
	return server.books

'''
Metodo para actualizar las estadisticas del servidor 

option: estadistica que se actualizara
clientName: cliente que realizo la solicitud
bookName: libro que descargo el cliente
'''
def updateStatistics(option, clientName, bookName):
	file = open(nameFileStatics, 'r')
	statistics = file.readlines()
	books      = literal_eval(statistics[0])
	clients    = literal_eval(statistics[1])
	file.close()
	if (option == 0):
		currentDownloads[clientName].remove(bookName)
		if (not currentDownloads[clientName]):
			del currentDownloads[clientName]
		if not (bookName in books):
			books[bookName] = 0
		books[bookName] = books[bookName] + 1
		try:
			centralServer = ServerProxy(centralServerDir)
			centralServer.updateStatistics(0, serverDir, bookName)
		except:
			print("No se logro establecer conexion con el servidor central.")
	else:
		if not (clientName in clients):
			clients[clientName] = 0
		clients[clientName] = clients[clientName] + 1
	file = open(nameFileStatics, 'w')
	file.write(str(books)   + '\n')
	file.write(str(clients) + '\n')
	file.close()
	return "ACK"


'''
Clase principal de servidor de descarga la cual asocia los metodos necesarios en el servidor central
el cual se encarga de convertirlos en XML y tenerlos disponibles para el cliente.
'''
class DownloadServer(threading.Thread):
	def run(self):
		server = AsyncXMLRPCServer(("localhost", 8121), SimpleXMLRPCRequestHandler)
		server.register_function(checkBook,    "checkBook")
		server.register_function(transferData, "transferData")
		server.register_function(booksList,    "booksList")
		server.register_function(bookSize,     "bookSize")
		server.register_function(updateStatistics, "updateStatistics")
		server.serve_forever()

'''
Clase servidor, inicia la conexion con el servidor central en el constructor, carga la clase de libros
y se queda escuchando solicitudes del cliente.
'''
class Server:
	def __init__(self, central = centralServerDir, server = serverDir):
		try:
			self.proxy = ServerProxy(centralServerDir)
			self.proxy.registerServer(serverDir)
			self.downloadServer = DownloadServer()
			self.downloadServer.start()
			self.books = uploadBookList()
		except:
			print("No se logro establecer conexion con el servidor central.")
			exit()

	'''
	Metodo que imprime la lista de liibros que tiene el servidor
	'''
	def printBooks(self):
		print("Los libros disponibles son: ")
		for book in self.books:
			print(book)

	'''
	Metodo que muestra las estadisticas segun la opcion elegida

	option: opcion elegida del cliente
	'''
	def showStatistics(self, option):
		if (option == '1'):
			for client in currentDownloads:
				print(client)
				for book in currentDownloads[client]:
					print("\t" + book)
		else:
			file = open(nameFileStatics, 'r')
			statistics  = file.readlines()
			data = literal_eval(statistics[int(option)-2])
			elements = [(data[name], name) for name in data]
			elements.sort(reverse = True)
			x = 1
			for val, name in elements:
				print(str(x) + ". " + name + ": " + str(val))
				x = x+1
			print()
			file.close()

	'''
	Metodo principal para correr el servidor y mostrar las opciones en el terminal
	'''
	def run(self):
		while (True):
			print("Elija un opcion: ")
			for message in messages:
				print(message)
			print()
			option = raw_input()
			if ( not (option == '1' or option == '2' or option == '3')):
				print("Opcion invalida")
				continue
			if  (option == '1'):
				self.showStatistics(option)
			else:
				self.showStatistics(option)

if __name__ == '__main__':
	server = Server()
	server.run()