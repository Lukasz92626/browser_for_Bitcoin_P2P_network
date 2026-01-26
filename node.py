class Node:
    def __init__(self, host_v4: str | None = None, host_v6: str | None = None, port: int = 8333):
        self.host_v4 = host_v4
        self.host_v6 = host_v6
        self.port = port

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            host_v4=data.get("HOST_V4"),
            host_v6=data.get("HOST_V6"),
            port=int(data.get("PORT", 8333))
        )

    def to_dict(self) -> dict:
        return {
            "HOST_V4": self.host_v4,
            "HOST_V6": self.host_v6,
            "PORT": str(self.port)
        }

    def __str__(self):
        return f"Node(IPv4={self.host_v4}, IPv6={self.host_v6}, Port={self.port})"
