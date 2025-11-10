import sys
import asyncio

from Connection import Connection
from Game import Game

async def main():
    ip, port, status = sys.argv[1:4]

    conn = Connection(status)
    server = await conn.start_server(ip, port)
    print(f"Сервер запущен на {ip}:{port}, статус: {status}")


    if status == 'host':
        client_amount = sys.argv[4]

        game = Game('host', 2, conn)
        await game.start()

    elif status == 'client':
        ip_to, port_to = sys.argv[4:6]
        await conn.connect(ip_to, port_to)

        game = Game('client', None, conn)
        await game.start()

        
    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
    finally:
        server.close()
        await server.wait_closed()
        

if __name__ == "__main__":
    asyncio.run(main())
