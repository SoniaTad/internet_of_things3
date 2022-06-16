# Worksheet3  of IOT 

## Table of content 
* *Introduction*
* *Installation*
* *Tasks*
    + Task 1
    + Task 2
    + Task 3

## Introduction :
This final IOT  worksheet , we focus on the user datagram protocol known as  UDP
The worksheet consists of 3 Tasks 
The  programming language used is python 
As all Tasks are linked to each other there is only one python file for this worksheet **main.py**
The first thing to do would be making sure everything is correctly set up on the device that is going to be used .

## Installation :
As explained in worksheet 2 part one and two ,a remote server **csctcloud.uwe.ac.uk** was used  ,Accessing the remote server requires installing   Azure CLI and SSH Keys  .Visual studio code needs to be installed on the device and configured for remote development to enable the user to connect to the server as it represents the environment the code will be running on, for this particular part a UWE email was used to connect.
It’s useful to know that the steps and commands to run might differ depending on the OS of the device, just like any other editor could be used instead of VS .
## Tasks:
### Task 1 : Implementing a basic client 
For this task ,websockets was first imported as connection to the remote server was  created using the port **5678** ,then two functions were implemented one to receive the packet from the UDP server **rec_packet()**  and the other one to decode the packet **output()** function , the base64 package had to also be imported for that . Once the packet received ,it's header had to be converted to bytes 
```
async def rec_packet(websocket):
    packet = await websocket.recv()
    print('Base64 : ',packet)
    return base64.b64decode(packet)
#this function receives the packet then convert each sequence of the header into int  
async def output(websocket):
    packet=await rec_packet(websocket)
    print("the server sent : ",packet)
    print('Decoded Packet :')
    Source_port=int.from_bytes(packet[0:2],'little')
    print('Source Port :',Source_port)
    Des_port=int.from_bytes(packet[2:4],'little')
    print('Dest Port : ',Des_port)

```
### Task 2: calculating the checksum 
The second task's goal was to create a function **compute_checksum** that would calculate the checksum to compare with the one received in the packet to determine if the packet has been corrupted or not .
This function will first take the source and destination ports as integers and the playload as a bytearray , the first thing to take into consideration would be setting the checksum as 0 as it's meant to be calculated , then calculate the length from the playload's length , and convert everything to bytes using python's __to_bytes__. 
The next step would be summing all the bytes to create the packet and checking if the number of bytes in the payload isn't an odd number , to finally perform  ones complemet 
The function **compute_checksum** will then return the checksum computed as an int 
This function was first implemented inside the **output** function but then was changed to an independent one as it will be called more than once .

The function is called inside the **output** function here 
```
#Task 2
    #calculating the checksum by calling the compute_checksum function 
    calc_check=compute_checksum(Source_port,Des_port,Payload)
    #comparing checksums after calculating it
    if calc_check==checksum:
        print('valid checksum')
    else:
        print('invalid checksum')

```
### Task 3 : Sending a packet 

The **send_packet** as seen below calls the Task 2 function **compute_checksum** to compute the checksum before it construct the packet , encode it and finally send it over   
```
async def send_packet(websocket,Source_port,Des_port,payload):
    #converting integers to bytes 
    New_Source_port = Source_port.to_bytes(2,'little')  
    New_Des_port = Des_port.to_bytes(2,'little')
    # getting the length from the payload 
    length=8 + len(payload)
    New_Length = length.to_bytes(2,'little')
    #calling the compute_checksum function to calculate the checksum before sending it
    checksum=compute_checksum(Source_port,Des_port,payload)
    # checksum converted to bytes
    New_checksum=checksum.to_bytes(2,'little')
    
    #constructing the packet to be sent (header+ playload)
    Packet=New_Source_port+ New_Des_port + New_Length + New_checksum + payload
    print('Packet',Packet)
    packet = base64.b64encode(Packet)
    # sending the packet
    await websocket.send(packet)

```
This Task also requires to add an additional infinite while loop that would  have the client send a valued UDP packet to the server, with the payloa __d'1111__, and wait to receive the time back, and then sleeping for 1 sec and repeating right after , this last part would also require importing time for it to work correctly .
When running the **main.py** file one of the many outputs is this one here below where it prints out the values and the **exact time** and checks that the **checksum is valid**

```
Packet b'\x00\x00\x1e\x02\x0c\x00\x9bs1111'
Base64 :  b'HgIAABAALf0xMzowNTo0Mg=='
the server sent :  b'\x1e\x02\x00\x00\x10\x00-\xfd13:05:42'
Decoded Packet :
Source Port : 542
Dest Port :  0
Data Length :  16
Checksum :  64813
payload :  13:05:42
valid checksum
```





