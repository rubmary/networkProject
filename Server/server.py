#!/usr/bin/env python
from __future__ import print_function
import threading
import time
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from ast import *

nameFile = "availableBooks.txt"
nameFileStatics = "statistics.txt"
messages = [ "1. Libros en descarga",
			 "2. Libros descargados",
			 "3. Estadisticas de clientes" ]

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

def updateStatistics(option, name):
	# REGION CRITICA
	file = open(nameFileStatics, 'r')
	statistics = file.readlines()
	books      = literal_eval(statistics[0])
	clients    = literal_eval(statistics[1])
	file.close()
	if (option == 0):
		if not (name in books):
			books[name] = 0
		books[name] = books[name] + 1
	else:
		if not (name in clients):
			clients[name] = 0
		clients[name] = clients[name] + 1
	file = open(nameFileStatics, 'w')
	file.write(str(books)   + '\n')
	file.write(str(clients) + '\n')
	file.close()

class DownloadServer(threading.Thread):
	def run(self):
		server  = SimpleXMLRPCServer(("localhost", 8121))
		server.register_function(checkBook,    "checkBook")
		server.register_function(transferData, "transferData")
		server.register_function(booksList,    "booksList")
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

	# Muestra las estadisticas segun la opcion elegida
	def showStatistics(self, option):
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
				print("No se todavia :(")
			else:
				self.showStatistics(option)

if __name__ == '__main__':
	server = Server()
	server.run()