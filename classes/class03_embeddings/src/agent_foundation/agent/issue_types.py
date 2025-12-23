from __future__ import annotations
from enum import Enum

class IssueType(str, Enum):
    VPN = "vpn"
    MESSENGER = "messenger"
    NETWORK = "network"
    UNKNOWN = "unknown"
