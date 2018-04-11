#!/usr/bin/env python
from __future__ import print_function
import threading
import time
from xmlrpclib import ServerProxy, Binary
from SimpleXMLRPCServer import SimpleXMLRPCServer
from os import stat,walk

nameFile = "availableBooks.txt"

def uploadBookList():
	books = []
	for root,dir,file in walk("Libros"):
		for f in file:
			books.append(f.split('.')[0])
	return books

def checkBook(book):
	# HACER HILOS PROBABLEMENTE
	print("checking book in server")
	for b in server.books:
		if (b == book):
			return True
	return False

def bookSize(book):
	path = "Libros/" + book + ".pdf"
	print(path)
	return stat(path).st_size

def transferData(book, chunkSize, actualChunk, isLast):
	# HACER HILOS PROBABLEMENTE
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

def booksList():
	return server.books

class DownloadServer(threading.Thread):
	def run(self):
		server  = SimpleXMLRPCServer(("localhost", 8121))
		server.register_function(checkBook,    "checkBook")
		server.register_function(transferData, "transferData")
		server.register_function(booksList,    "booksList")
		server.register_function(bookSize,     "bookSize")
		server.serve_forever()

class Server:
	def __init__(self, central = "http://localhost:8000", server = "http://localhost:8121"):
		self.proxy  = ServerProxy(central)
		self.proxy.registerServer(server)
		self.downloadServer = DownloadServer()
		self.downloadServer.start()
		self.books = uploadBookList()

	def printBooks(self):
		print("Los libros disponibles son: ")
		for book in self.books:
			print(book)

	def run(self):
		while (True):
			print ("Ingrese una opcion")
			option = raw_input()
			print(option)
			if (option == "1"):
				self.printBooks()


if __name__ == '__main__':
	server = Server()
	server.run()