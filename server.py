import socket
import pickle
import threading
import itertools

HOST = '127.0.0.1'
PORT = 65432

DIST_MATRIX = [
    [0, 10, 15, 20],
    [10, 0, 35, 25],
    [15, 35, 0, 30],
    [20, 25, 30, 0]
]

clients_results = []  
lock = threading.Lock() 


def handle_client(client_socket, client_address, routes):
    global clients_results
    try:
        print(f"Conectado a {client_address}")

        client_socket.sendall(pickle.dumps(routes))
        
        data = client_socket.recv(4096)
        results = pickle.loads(data)  # Lista de tuplas (rota, custo)
        print(f"Resultados recebidos de {client_address}: {results}")
        
        with lock:
            clients_results.extend(results)
    except Exception as e:
        print(f"Erro ao processar dados de {client_address}: {e}")
    finally:
        client_socket.close()


def calculate_best_route():
    """Calcula a melhor rota com base nos resultados recebidos."""
    if not clients_results:
        return None, float('inf')
    return min(clients_results, key=lambda x: x[1])


def main():
    global clients_results
    print(f"Servidor ouvindo em {HOST}:{PORT}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    cities = list(range(len(DIST_MATRIX)))
    all_routes = list(itertools.permutations(cities))

    threads = []
    try:
        while len(threads) < 2:  # Aceitar exatamente dois clientes
            client_socket, client_address = server_socket.accept()
            print(f"Cliente conectado: {client_address}")
            
            routes_per_client = len(all_routes) // 2
            start_index = len(threads) * routes_per_client
            end_index = start_index + routes_per_client
            routes_to_send = all_routes[start_index:end_index]

            thread = threading.Thread(target=handle_client, args=(client_socket, client_address, routes_to_send))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        best_route, best_cost = calculate_best_route()
        print(f"Melhor rota: {best_route} com custo: {best_cost}")

    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
