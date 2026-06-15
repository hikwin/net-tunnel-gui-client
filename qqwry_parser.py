import struct
import socket
import os

class QQWry:
    """
    Pure Python parser for the qqwry.dat (Chunzhen IP) database.
    Does not require any external library dependencies.
    """
    def __init__(self, db_path):
        self.db_path = db_path
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")
            
        with open(db_path, 'rb') as f:
            self.data = f.read()
            
        if len(self.data) < 8:
            raise ValueError("Invalid qqwry.dat database: file too small.")
            
        # First 8 bytes are the headers:
        # 4 bytes: Offset of the first index record
        # 4 bytes: Offset of the last index record
        self.start_index, self.end_index = struct.unpack('<II', self.data[:8])
        self.index_count = (self.end_index - self.start_index) // 7 + 1

    def ip_to_int(self, ip_str):
        """Convert IPv4 string to 32-bit integer."""
        try:
            return struct.unpack('!I', socket.inet_aton(ip_str.strip()))[0]
        except Exception:
            return None

    def _read_offset(self, offset):
        """Read 3 bytes offset and return it as a 32-bit integer."""
        b = self.data[offset:offset+3]
        if len(b) < 3:
            return 0
        return struct.unpack('<I', b + b'\x00')[0]

    def _read_string(self, offset):
        """Read a null-terminated string from offset, resolving redirection if any."""
        if offset == 0:
            return ""
            
        flag = self.data[offset]
        if flag == 1 or flag == 2:
            redir = self._read_offset(offset + 1)
            return self._read_string(redir)
            
        res = bytearray()
        while True:
            b = self.data[offset]
            if b == 0:
                break
            res.append(b)
            offset += 1
            if offset >= len(self.data):
                break
        return res.decode('gbk', errors='replace').strip()

    def _read_area(self, offset):
        """Read area information, which is a redirected or immediate string."""
        if offset == 0:
            return ""
            
        flag = self.data[offset]
        if flag == 1 or flag == 2:
            redir = self._read_offset(offset + 1)
            if redir == 0:
                return ""
            return self._read_string(redir)
            
        res = bytearray()
        while True:
            b = self.data[offset]
            if b == 0:
                break
            res.append(b)
            offset += 1
            if offset >= len(self.data):
                break
        return res.decode('gbk', errors='replace').strip()

    def lookup(self, ip_str):
        """
        Look up the location of an IP address.
        Returns (country, area) or None.
        """
        ip = self.ip_to_int(ip_str)
        if ip is None:
            return None

        # Binary search on index records
        low = 0
        high = self.index_count - 1
        
        while low <= high:
            mid = (low + high) // 2
            offset = self.start_index + mid * 7
            
            # Read start IP of the range (4 bytes)
            start_ip = struct.unpack('<I', self.data[offset:offset+4])[0]
            
            if ip < start_ip:
                high = mid - 1
            else:
                # Read 3 bytes offset to the location record
                record_offset = self._read_offset(offset + 4)
                
                # The first 4 bytes of the location record is the end IP of the range
                if record_offset + 4 > len(self.data):
                    break
                end_ip = struct.unpack('<I', self.data[record_offset:record_offset+4])[0]
                
                if ip <= end_ip:
                    # Found! Resolve country and area
                    return self._parse_location(record_offset + 4)
                else:
                    low = mid + 1
                    
        return None

    def _parse_location(self, offset):
        """Resolve country and area from the location record offset."""
        flag = self.data[offset]
        
        if flag == 1:
            # Country and area are both redirected
            redir = self._read_offset(offset + 1)
            return self._parse_location(redir)
        elif flag == 2:
            # Country is redirected, area starts after the redirect offset (offset + 4)
            redir = self._read_offset(offset + 1)
            country = self._read_string(redir)
            area = self._read_area(offset + 4)
            return country, area
        else:
            # Country is written directly, area starts after country string (null-terminated)
            country = self._read_string(offset)
            # Find the end of country string (null byte)
            # We encode the parsed country string to gbk to calculate its length in bytes
            country_bytes_len = len(country.encode('gbk', errors='replace'))
            area = self._read_area(offset + country_bytes_len + 1)
            return country, area

    def get_version(self):
        """
        Get the database version info.
        In qqwry.dat, the last index entry records a special redirect to the version text.
        """
        try:
            offset = self.end_index
            record_offset = self._read_offset(offset + 4)
            country, area = self._parse_location(record_offset + 4)
            # Typically returns something like "纯真网络" and "2026年XX月XX日IP数据"
            return f"{country} {area}".strip()
        except Exception:
            return "Unknown version"
