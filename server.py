#!/usr/bin/env python

# WS server example

import random
import time
import asyncio
import websockets
import netifaces as ni



ni.ifaddresses('en0')
ip = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']
print(ip)


count = 0
my_message =""
async def consumer(message):
  global count
  global my_message
  print(f"Received message: {message}")

  if message == "button thing":
    count = count + 1
    print(f"button pushes: {count}")
    my_message = "button pushed" + ": " + str(count)

async def producer():
  global my_message
  if my_message:
    message = my_message
    my_message = ""
  else:
    message = str(random.randint(1200, 11000))
    await asyncio.sleep(2) # sleep for 100 miliseconds before returning message, to give other functions time.
  return message

async def consumer_handler(websocket, path):
    async for message in websocket:
        await consumer(message)

async def producer_handler(websocket, path):
  while True:
    message = await producer()
    await websocket.send(message)

async def handler(websocket, path):
    consumer_task = asyncio.ensure_future(
        consumer_handler(websocket, path))
    producer_task = asyncio.ensure_future(
        producer_handler(websocket, path))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()

start_server = websockets.serve(handler, "192.168.178.28", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
