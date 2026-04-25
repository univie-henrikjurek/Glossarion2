import struct
import os
from typing import BinaryIO
from .utils import logger


class StarDictLoader:
    IFO_MAGIC = b"-starDict-"
    
    def __init__(self, data_path: str = "/data"):
        self.data_path = data_path
        self.logger = logger
        self.index: dict[str, list[tuple[int, int]] = {}
        self.synonyms: dict[str, str] = {}
        self._loaded = False

    def load(self, dictionary_name: str) -> bool:
        if self._loaded:
            return True
        
        ifo_path = os.path.join(self.data_path, dictionary_name, f"{dictionary_name}.ifo")
        idx_path = os.path.join(self.data_path, dictionary_name, f"{dictionary_name}.idx")
        dict_path = os.path.join(self.data_path, dictionary_name, f"{dictionary_name}.dict.dz")
        
        if not os.path.exists(ifo_path):
            self.logger.warning(f"Dictionary IFO file not found: {ifo_path}")
            return False
        
        try:
            with open(ifo_path, 'rb') as f:
                if not self._read_ifo(f):
                    return False
            
            if os.path.exists(idx_path):
                self._load_idx(idx_path)
            
            self._loaded = True
            self.logger.info(f"Loaded dictionary: {dictionary_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load dictionary: {e}")
            return False

    def _read_ifo(self, f: BinaryIO) -> bool:
        magic = f.read(10)
        if magic != self.IFO_MAGIC:
            self.logger.error("Invalid StarDict IFO magic")
            return False
        return True

    def _load_idx(self, idx_path: str) -> None:
        with open(idx_path, 'rb') as f:
            while True:
                data = f.read(12)
                if len(data) < 12:
                    break
                
                offset, word_count = struct.unpack(">II", data[:8])
                
                word_data = bytearray()
                while True:
                    b = f.read(1)
                    if b == b'\x00':
                        break
                    word_data.extend(b)
                
                word = word_data.decode('utf-8', errors='ignore')
                
                if word not in self.index:
                    self.index[word] = []
                self.index[word].append((offset, word_count))

    def lookup(self, term: str) -> list[dict]:
        term_lower = term.lower()
        results = []
        
        if term_lower in self.index:
            results.append({
                "term": term,
                "translation": f"[From index: {term}]",
                "match_type": "exact"
            })
        
        for idx_term in self.index:
            if term_lower in idx_term.lower():
                results.append({
                    "term": idx_term,
                    "translation": f"[Contains: {idx_term}]",
                    "match_type": "contains"
                })
                if len(results) >= 10:
                    break
        
        return results

    def load_all(self) -> None:
        if not os.path.exists(self.data_path):
            self.logger.warning(f"Data path does not exist: {self.data_path}")
            return
        
        for item in os.listdir(self.data_path):
            item_path = os.path.join(self.data_path, item)
            if os.path.isdir(item_path):
                ifo_file = os.path.join(item_path, f"{item}.ifo")
                if os.path.exists(ifo_file):
                    self.load(item)


def create_stardict_loader(data_path: str = "/data") -> StarDictLoader:
    loader = StarDictLoader(data_path)
    loader.load_all()
    return loader