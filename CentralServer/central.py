#!/usr/bin/env python
from __future__ import print_function
import threading
import time
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from ast import *


'''
Archivo que tiene las implementaciones de las clases principales utilizadas por el servidor central
y la clase correspondiente.
'''

nameFile = 'statistics.txt'
messages = [ "1. Libros solicitados por servidor de descarga.",
			 "2. Numero de clientes atendidos por servidor de descarga.",
			 "3. Servidores de descarga que se han caido." ]


'''
Metodo que dado un cliente lo registra en el servidor central

client: cliente que se registrara en el servidor.
'''
def registerClient(client):
	clients.append(client)
	return "ok"

'''
Metodo que dado un servidor de descarga lo registra en el servidor central

server: servidor que sera registrado en el servidor
'''
def registerServer(server):
	servers.append(server)
	return "ok"

'''
Metodo que retorna todos los libros de los servidores asociados al central
'''
def serversBooks():
	print("Client is in serversBooks")
	allBooks = []
	for server in servers:
		try:
			proxy = xmlrpclib.ServerProxy(server)
			books = proxy.booksList()
			allBooks.append(books)
		except:
			allBooks.append([])
	return allBooks

'''
Metodo que retorna todos los servidores conectados en el central
'''
def getServers():
	return servers

'''
Clase que actualiza las estadisticas del servidor central al ser llamada remotamente desde
algun servidor de descarga.

option: opcion a actualizar
server: servidor que actualiza la opcion
book: nombre del libro
'''
# Tipos de updates:
# 0 -> Se solicitud un libro a un servidor
# 1 -> Un servidor atendio a un cliente
# 2 -> Se callo un servidor
def updateStatistics(option, server, book = ""):
	# REGION CRITICA
	file = open(nameFile, 'r')
	statistics    = file.readlines()
	serverBooks   = literal_eval(statistics[0])
	serverClients = literal_eval(statistics[1])
	downServers   = literal_eval(statistics[2])
	file.close()
	if (option == 0):
		if (not server in serverBooks):
			serverBooks[server] = {}
		if (not book in serverBooks[server]):
			serverBooks[server][book] = 0
		serverBooks[server][book] = serverBooks[server][book] + 1
		if not (server in serverClients):
			serverClients[server] = 0
		serverClients[server] = serverClients[server] + 1
	else:
		if not (server in downServers):
			downServers[server] = 0
		downServers[server] = downServers[server] + 1
	file = open(nameFile, 'w')
	file.write(str(serverBooks)   + '\n')
	file.write(str(serverClients) + '\n')
	file.write(str(downServers)   + '\n')
	file.close()
	return "ACK"

'''
Metodo para hacer la solicitud de un libro, al hacer la solicitud el servidor central busca
todas las ocurrencias del mismo en los servidores de descarga y retorna una lista al cliente
con los servidores disponibles.

clientName: cliente que solicita el libro
book: nombre del libro
'''
def requestBook(clientName, book):
	# CREO QUE TENEMOS QUE PONER ESTO EN UN HILO PARA QUE SEA CONCURRENTE
	print("Client: " + str(clientName) + " is resquesting a book")
	availableServers = []
	for server in servers:
		try:
			proxy = xmlrpclib.ServerProxy(server)
			print(proxy)
			if (proxy.checkBook(book)):
				availableServers.append(server)
		except:
			continue
	return availableServers

'''
Clase de servidor central encargada de escuchar las peticiones y registrar sus funciones
para ser invocadas. 
'''
class CentralServer(threading.Thread):
	def run(self):
		server  = SimpleXMLRPCServer(("localhost", 8000))
		server.register_function(registerClient,   "registerClient")
		server.register_function(registerServer,   "registerServer")
		server.register_function(requestBook,      "requestBook")
		server.register_function(updateStatistics, "updateStatistics")
		server.register_function(getServers,       "getServers")
		server.register_function(serversBooks,     "serversBooks")
		server.serve_forever()

'''
Clase que se encarga de llevar la linea de comandos del servidor central.
'''
class Summary():
	'''
	Metodo para mostrar las estadisticas del servidor dada una opcion.

	option: opcion seleccionada.
	'''
	def showStatistics(self, option):
		file = open(nameFile, 'r')
		statistics  = file.readlines()
		data = literal_eval(statistics[int(option)-1])
		if (option == '1'):
			for server in data:
				print(server + ":")
				for book in data[server]:
					print("\t" + book + ": " + str(data[server][book]))
		else:
			for server in data:
				print(server + ": " + str(data[server]))
		print()
		file.close()

	'''
	Metodo principal para la interaccion con el servidor central.
	'''
	def run(self):
		while (True):
			print("Elija un opcion: ")
			for message in messages:
				print(message)
			print()
			option = raw_input()
			if (not (option == '1' or option == '2' or option == '3')):
				print("Opcion invalida")
				continue
			self.showStatistics(option)

if __name__ == '__main__':
	summary = Summary()
	clients = []
	servers = []
	centralServer = CentralServer(name = "server")
	centralServer.start()
	summary.run()
