from zeep import Client

wsdl = "https://servayto.madrid.es/MTPAR_WSINFO/InfoParking?wsdl"

client = Client(wsdl=wsdl)

for service in client.wsdl.services.values():
    for port in service.ports.values():
        operations = sorted(port.binding._operations.values(), key=lambda x: x.name)

        for operation in operations:
            print(operation.name)