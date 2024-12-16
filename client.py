import socket
import pickle
import time

HOST = '127.0.0.1' 
PORT = 65432        


def connect_to_server(host, port, retries=5, delay=2):
    for attempt in range(retries):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            return client_socket
        except (BlockingIOError, ConnectionRefusedError) as e:
            print(f"Tentativa {attempt + 1}/{retries}: Conexão falhou. Re-tentando em {delay} segundos...")
            time.sleep(delay)
    raise ConnectionError(f"Não foi possível conectar ao servidor após {retries} tentativas.")


def calculate_route_cost(route, dist_matrix):
    """Calcula o custo de uma rota."""
    cost = sum(dist_matrix[route[i]][route[i + 1]] for i in range(len(route) - 1))
    cost += dist_matrix[route[-1]][route[0]]  # Fechamento do ciclo
    return cost


def main():
    DIST_MATRIX = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0]
    ]

    try:
        client_socket = connect_to_server(HOST, PORT)
        with client_socket:

            data = client_socket.recv(4096)
            routes = pickle.loads(data)  # Deserializa as rotas recebidas
            print(f"Rotas recebidas do servidor: {routes}")

            results = [(route, calculate_route_cost(route, DIST_MATRIX)) for route in routes]

            client_socket.sendall(pickle.dumps(results))
            print(f"Resultados enviados ao servidor: {results}")

    except ConnectionError as e:
        print(f"Erro: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


if __name__ == "__main__":
    main()
