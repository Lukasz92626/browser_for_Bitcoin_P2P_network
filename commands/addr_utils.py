from ipaddress import ip_address, IPv6Address

NODE_NETWORK = 1


def normalize_ip(ip):
    addr = ip_address(ip)
    if isinstance(addr, IPv6Address) and addr.ipv4_mapped:
        return str(addr.ipv4_mapped)
    return str(addr)


def is_sensible_addr(addr):
    ip = ip_address(addr.ip)
    port = addr.port

    services = int(addr.services, 16)

    if port != 8333:
        return False

    if ip.is_private or ip.is_loopback or ip.is_unspecified or ip.is_multicast:
        return False

    if str(ip) in ("0.0.0.0", "0.0.0.255"):
        return False

    if not (services & NODE_NETWORK):
        return False

    return True


def print_addr(addr):
    ip = normalize_ip(addr.ip)
    proto = "IPv6" if ":" in ip else "IPv4"

    print(f"[ADDR] {ip}:{addr.port} ({proto})")
