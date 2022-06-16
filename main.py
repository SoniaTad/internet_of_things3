import websockets
import asyncio
import base64
import struct
import time

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

#this function receives the packet then uses the base64 package to decode it 
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
    Length=int.from_bytes(packet[4:6],'little')
    print('Data Length : ',Length)
    checksum=int.from_bytes(packet[6:8],'little')
    print('Checksum : ',checksum)
    payload = packet[8:(Length+8)].decode("utf-8")  
    print('payload : ',payload)
    Payload=packet[8:(Length+8)]

    #Task 2
    #calculating the checksum by calling the compute_checksum function 
    calc_check=compute_checksum(Source_port,Des_port,Payload)
    #comparing checksums after calculating it
    if calc_check==checksum:
        print('valid checksum')
    else:
        print('invalid checksum')



def compute_checksum(Source_port,Des_port,payload):
    #the checksum needs to be set as 0
    checksum=0
    #calculating the length from the payload
    Length=8 + len(payload)
    #converting the int to bytes
    New_Source_port = Source_port.to_bytes(2,'little')     
    New_Des_port = Des_port.to_bytes(2,'little')         
    New_Length = Length.to_bytes(2,'little') 
                
    New_checksum = checksum.to_bytes(2,'little') 
    
    
    # creating the packet by summing all of the header and payload
    sum= New_Source_port + New_Des_port + New_Length + New_checksum + payload
    
    # checking if len(sum) is odd if so adding a O 
    if (len(sum) % 2) != 0:
        sum += struct.pack("!B",0) 
    
    # looping through the packet  2 bytes at a time
    for i in range( 0, len(sum), 2 ):
        # append the value to the checksum 
        checksum += (sum[i] << 8) + (sum[i + 1])

    # perform ones complement
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum = ~checksum & 0xFFFF
    return checksum

       
async def main():
    #connecting to the server using port 5612
    uri = "ws://localhost:5612"
    async with websockets.connect(uri) as websocket:
        await output(websocket)
        while True:
            await send_packet(websocket, 0, 542, b'1111')
            await output(websocket)
            time.sleep(1)
        
        
if __name__ == "__main__":
    asyncio.run(main())
    

   
    