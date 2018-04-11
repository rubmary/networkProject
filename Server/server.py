#!/usr/bin/env python
from __future__ import print_function
import threading
import time
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
nameFile = "availableBooks.txt"


def checkBook(book):
	# HACER HILOS PROBABLEMENTE
	print("checking book in server")
	for b in server.books:
		if (b == book):
			return True
	return False

def transferData(book):
	# HACER HILOS PROBABLEMENTE
	time.sleep(3)

def booksList():
	return server.books

class DownloadServer(threading.Thread):
	def run(self):
		server  = SimpleXMLRPCServer(("localhost", 8121))
		server.register_function(checkBook,    "checkBook")
		server.register_function(transferData, "transferData")
		server.serve_forever()


class Server:
	def __init__(self, central = "http://localhost:8000", server = "http://localhost:8121"):
		self.proxy  = xmlrpclib.ServerProxy(central)
		self.proxy.registerServer(server)
		self.downloadServer = DownloadServer()
		self.downloadServer.start()
		file = open(nameFile, 'r')
		books = file.readlines()
		self.books = [b.strip() for b in books]

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