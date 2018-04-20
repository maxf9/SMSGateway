#!/usr/bin/env python3
from argparser import ArgParser
from network import TCPServer
from smpp import SMPPApplication
from sms_client import SMSClient

def main():	
	ip_address, port, serial_port, system_id = ArgParser().parse_arguments()
	smpp = SMPPApplication(system_id, SMSClient(serial_port))
	TCPServer(ip_address, port, application=smpp).start()

if __name__ == "__main__":
	main()