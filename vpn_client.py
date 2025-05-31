import os, socket, struct
from cryptography.fernet import Fernet
from pytun import TunTapDevice, IFF_TUN, IFF_NO_PI

# Replace with actual key when deploying
key = b'your-encryption-key-here'
cipher = Fernet(key)

# create TUN device
tun = TunTapDevice(flags=IFF_TUN | IFF_NO_PI)
tun.addr = '10.8.0.2'
tun.dstaddr = '10.8.0.1'
tun.netmask = '255.255.255.0'
tun.mtu = 1500
tun.up()

print(f'[+] TUN interface {tun.name} configured.')

# Set route so all traffic goes through TUN
os.system(f'sudo ip route add default dev {tun.name} table 100')
os.system(f'sudo ip rule add from {tun.addr} table 100')

# Connect to VPN server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('your.server.ip.here', 5555))  # Replace with actual IP when deploying
print('[+] Connected to VPN server')

# Main loop
try:
    while True:
        data = tun.read(tun.mtu)
        encrypted = cipher.encrypt(data)
        sock.sendall(struct.pack("!H", len(encrypted)) + encrypted)

        # Receive reply
        header = sock.recv(2)
        if not header:
            break
        length = struct.unpack("!H", header)[0]
        response = sock.recv(length)
        decrypted = cipher.decrypt(response)
        tun.write(decrypted)

except KeyboardInterrupt:
    print('[*] Closing connection...')
finally:
    sock.close()
    tun.down()
    os.system(f'sudo ip rule del from {tun.addr} table 100')
