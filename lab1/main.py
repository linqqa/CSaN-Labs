import socket
import sys
import time

MAX_HOPS = 30
TRIES_PER_HOP = 3
DEST_PORT = 33434
TIMEOUT = 2

def traceroute_udp(host):
    try:
        dest_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print("Unable to resolve hostname.")
        sys.exit(1)

    print(f"traceroute to {host} ({dest_ip}), {MAX_HOPS} hops max")

    for ttl in range(1, MAX_HOPS + 1):
        print(f"{ttl:<2}", end=" ")
        got_reply = False

        for attempt in range(TRIES_PER_HOP):
            send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            send_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

            recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            recv_sock.settimeout(TIMEOUT)
            recv_sock.bind(("", DEST_PORT))

            try:
                start_time = time.time()
                send_sock.sendto(b'', (dest_ip, DEST_PORT))
                _, addr = recv_sock.recvfrom(512)
                elapsed = (time.time() - start_time) * 1000

                if not got_reply:
                    print(f"{addr[0]:<15}", end=" ")
                    got_reply = True
                print(f"{elapsed:.2f} ms", end="  ")

                if addr[0] == dest_ip:
                    send_sock.close()
                    recv_sock.close()
                    break 

            except socket.timeout:
                print("*", end="  ")
            finally:
                send_sock.close()
                recv_sock.close()

        print()
        if got_reply and addr[0] == dest_ip:
            break

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: sudo python3 mytraceroute.py <host>")
        sys.exit(1)

    traceroute_udp(sys.argv[1])
