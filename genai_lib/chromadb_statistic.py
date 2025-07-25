#!/usr/bin/env python3
"""
ChromaDB Statistics Module
==========================
Modul zur Erstellung detaillierter Statistiken für ChromaDB-Collections.
Stellt direkt einsetzbare Funktionen für die Analyse bereit.
"""

import chromadb
import os
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple, Union
import json
from datetime import datetime

# --- Datenklassen für Statistiken ---
class CollectionStats:
    """Datenklasse für Collection-Statistiken."""
    def __init__(self, name: str, chunk_count: int, document_count: int, source_stats: Dict[str, int], 
                 metadata_keys: List[str], avg_chunk_size: float = 0.0):
        self.name = name
        self.chunk_count = chunk_count           # Anzahl der Chunks (Einträge in ChromaDB)
        self.document_count = document_count     # Anzahl der ursprünglichen Dokumente/Dateien
        self.source_stats = source_stats         # Chunks pro Quelldatei
        self.metadata_keys = metadata_keys       # Verfügbare Metadaten-Felder
        self.avg_chunk_size = avg_chunk_size     # Durchschnittliche Chunk-Größe in Zeichen
    
    def get_chunks_per_document(self) -> float:
        """Berechnet durchschnittliche Chunks pro Dokument."""
        return self.chunk_count / self.document_count if self.document_count > 0 else 0.0
    
    def get_source_list(self) -> List[str]:
        """Gibt Liste aller Quelldateien zurück."""
        return list(self.source_stats.keys())
    
    def get_largest_source(self) -> Tuple[str, int]:
        """Gibt die Quelle mit den meisten Chunks zurück."""
        if not self.source_stats:
            return ("", 0)
        return max(self.source_stats.items(), key=lambda x: x[1])
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary für Export."""
        return {
            "name": self.name,
            "chunk_count": self.chunk_count,
            "document_count": self.document_count,
            "chunks_per_document": self.get_chunks_per_document(),
            "average_chunk_size": self.avg_chunk_size,
            "metadata_keys": self.metadata_keys,
            "source_statistics": self.source_stats
        }

class DatabaseStats:
    """Datenklasse für gesamte Datenbankstatistiken."""
    def __init__(self, collections: List[CollectionStats], total_chunks: int, total_documents: int):
        self.collections = collections
        self.total_chunks = total_chunks         # Gesamtanzahl aller Chunks
        self.total_documents = total_documents   # Gesamtanzahl aller ursprünglichen Dokumente
        self.collection_count = len(collections)
    
    def get_avg_chunks_per_document(self) -> float:
        """Berechnet durchschnittliche Chunks pro Dokument über alle Collections."""
        return self.total_chunks / self.total_documents if self.total_documents > 0 else 0.0
    
    def get_collection_by_name(self, name: str) -> Optional[CollectionStats]:
        """Gibt Collection-Statistiken für bestimmten Namen zurück."""
        for collection in self.collections:
            if collection.name == name:
                return collection
        return None
    
    def get_largest_collection(self) -> Optional[CollectionStats]:
        """Gibt die Collection mit den meisten Chunks zurück."""
        if not self.collections:
            return None
        return max(self.collections, key=lambda x: x.chunk_count)

# --- Kernfunktionen ---
def analyze_collection(collection_name: str, db_path: str) -> Optional[CollectionStats]:
    """
    Analysiert eine einzelne Collection und erstellt Statistiken.
    
    Args:
        collection_name: Name der zu analysierenden Collection
        db_path: Pfad zur ChromaDB
    
    Returns:
        CollectionStats-Objekt mit Analyseergebnissen oder None bei Fehler
    """
    if not os.path.exists(db_path):
        print(f"❌ Fehler: Der ChromaDB-Pfad '{db_path}' existiert nicht.")
        return None
    
    try:
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(collection_name)
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Collection '{collection_name}': {type(e).__name__}: {e}")
        return None
    
    # Grundlegende Anzahl
    chunk_count = collection.count()
    
    if chunk_count == 0:
        return CollectionStats(
            name=collection.name,
            chunk_count=0,
            document_count=0,
            source_stats={},
            metadata_keys=[],
            avg_chunk_size=0.0
        )
    
    # Alle Daten abrufen für detaillierte Analyse
    try:
        results = collection.get(
            ids=None, 
            where=None, 
            include=['metadatas', 'documents']
        )
        
        metadatas = results.get('metadatas', [])
        documents = results.get('documents', [])
        
    except Exception as e:
        print(f"⚠️ Warnung: Konnte Details für Collection '{collection.name}' nicht abrufen: {e}")
        metadatas = []
        documents = []
    
    # Quellen-Statistiken und Dokumentenzählung
    source_chunk_counts = defaultdict(int)
    all_metadata_keys = set()
    unique_sources = set()  # Für die Zählung der ursprünglichen Dokumente
    
    for metadata in metadatas:
        if metadata:
            # Sammle alle verfügbaren Metadaten-Schlüssel
            all_metadata_keys.update(metadata.keys())
            
            # Zähle Chunks pro Quelle
            source = metadata.get('source', 'Unbekannte Quelle')
            source_chunk_counts[source] += 1
            unique_sources.add(source)  # Eindeutige Quellen sammeln
    
    # Durchschnittliche Chunk-Größe berechnen
    avg_chunk_size = 0.0
    if documents:
        total_chars = sum(len(doc) if doc else 0 for doc in documents)
        avg_chunk_size = total_chars / len(documents)
    
    # Dokumentenzählung: Anzahl eindeutiger Quellen
    document_count = len(unique_sources) if unique_sources else 0
    
    return CollectionStats(
        name=collection.name,
        chunk_count=chunk_count,
        document_count=document_count,
        source_stats=dict(source_chunk_counts),
        metadata_keys=sorted(list(all_metadata_keys)),
        avg_chunk_size=avg_chunk_size
    )

def get_database_statistics(db_path: str) -> Optional[DatabaseStats]:
    """
    Erstellt umfassende Statistiken für die gesamte ChromaDB.
    
    Args:
        db_path: Pfad zur ChromaDB
    
    Returns:
        DatabaseStats-Objekt oder None bei Fehler
    """
    if not os.path.exists(db_path):
        print(f"❌ Fehler: Der ChromaDB-Pfad '{db_path}' existiert nicht.")
        return None
    
    try:
        client = chromadb.PersistentClient(path=db_path)
        collections = client.list_collections()
        collection_stats = []
        total_chunks = 0
        total_documents = 0
        
        for collection in collections:
            stats = analyze_collection(collection.name, db_path)
            if stats:
                collection_stats.append(stats)
                total_chunks += stats.chunk_count
                total_documents += stats.document_count
        
        return DatabaseStats(
            collections=collection_stats,
            total_chunks=total_chunks,
            total_documents=total_documents
        )
        
    except Exception as e:
        print(f"❌ Fehler beim Analysieren der Datenbank: {type(e).__name__}: {e}")
        return None

def list_collections(db_path: str) -> List[str]:
    """
    Listet alle verfügbaren Collections in der Datenbank auf.
    
    Args:
        db_path: Pfad zur ChromaDB
    
    Returns:
        Liste der Collection-Namen
    """
    if not os.path.exists(db_path):
        print(f"❌ Fehler: Der ChromaDB-Pfad '{db_path}' existiert nicht.")
        return []
    
    try:
        client = chromadb.PersistentClient(path=db_path)
        collections = client.list_collections()
        return [col.name for col in collections]
    except Exception as e:
        print(f"❌ Fehler beim Auflisten der Collections: {type(e).__name__}: {e}")
        return []

def get_collection_summary(collection_name: str, db_path: str) -> Optional[CollectionStats]:
    """
    Alias für analyze_collection - für bessere Lesbarkeit.
    
    Args:
        collection_name: Name der Collection
        db_path: Pfad zur ChromaDB
    
    Returns:
        CollectionStats-Objekt oder None bei Fehler
    """
    return analyze_collection(collection_name, db_path)

def get_quick_stats(db_path: str) -> Dict[str, Union[int, List[str]]]:
    """
    Schnelle Übersicht ohne detaillierte Analyse.
    
    Args:
        db_path: Pfad zur ChromaDB
    
    Returns:
        Dictionary mit Grundstatistiken
    """
    if not os.path.exists(db_path):
        return {"error": f"Pfad '{db_path}' existiert nicht"}
    
    try:
        client = chromadb.PersistentClient(path=db_path)
        collections = client.list_collections()
        
        total_chunks = 0
        collection_names = []
        
        for collection in collections:
            collection_names.append(collection.name)
            total_chunks += collection.count()
        
        return {
            "collection_count": len(collections),
            "collection_names": collection_names,
            "total_chunks": total_chunks,
            "database_path": db_path
        }
        
    except Exception as e:
        return {"error": f"Fehler: {type(e).__name__}: {e}"}

def compare_collections(db_path: str, collection_names: List[str]) -> Optional[Dict]:
    """
    Vergleicht mehrere Collections miteinander.
    
    Args:
        db_path: Pfad zur ChromaDB
        collection_names: Liste der zu vergleichenden Collection-Namen
    
    Returns:
        Dictionary mit Vergleichsdaten
    """
    comparison = {
        "collections": [],
        "summary": {
            "total_chunks": 0,
            "total_documents": 0,
            "analyzed_collections": 0
        }
    }
    
    for name in collection_names:
        stats = analyze_collection(name, db_path)
        if stats:
            comparison["collections"].append(stats.to_dict())
            comparison["summary"]["total_chunks"] += stats.chunk_count
            comparison["summary"]["total_documents"] += stats.document_count
            comparison["summary"]["analyzed_collections"] += 1
    
    if comparison["summary"]["analyzed_collections"] == 0:
        return None
    
    # Durchschnittswerte berechnen
    count = comparison["summary"]["analyzed_collections"]
    comparison["summary"]["avg_chunks_per_collection"] = comparison["summary"]["total_chunks"] / count
    comparison["summary"]["avg_documents_per_collection"] = comparison["summary"]["total_documents"] / count
    
def export_statistics_to_json(db_path: str, output_file: str = "chromadb_stats.json") -> bool:
    """
    Exportiert die Datenbankstatistiken in eine JSON-Datei.
    
    Args:
        db_path: Pfad zur ChromaDB
        output_file: Name der Ausgabedatei
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    db_stats = get_database_statistics(db_path)
    if not db_stats:
        return False
    
    # Konvertiere zu JSON-serialisierbarem Format
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "database_path": db_path,
        "summary": {
            "total_collections": db_stats.collection_count,
            "total_documents": db_stats.total_documents,
            "total_chunks": db_stats.total_chunks,
            "avg_chunks_per_document": db_stats.get_avg_chunks_per_document()
        },
        "collections": [stats.to_dict() for stats in db_stats.collections]
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Statistiken erfolgreich exportiert nach: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Exportieren: {type(e).__name__}: {e}")
        return False

def get_collection_chunks(collection_name: str, db_path: str, limit: int = 10, 
                         offset: int = 0, include_embeddings: bool = False) -> Optional[Dict]:
    """
    Ruft einzelne Chunks einer Collection ab.
    
    Args:
        collection_name: Name der Collection
        db_path: Pfad zur ChromaDB
        limit: Maximale Anzahl Chunks (0 = alle)
        offset: Start-Position für Paginierung
        include_embeddings: Ob Embeddings eingeschlossen werden sollen
    
    Returns:
        Dictionary mit Chunk-Daten oder None bei Fehler
    """
    if not os.path.exists(db_path):
        print(f"❌ Fehler: Der ChromaDB-Pfad '{db_path}' existiert nicht.")
        return None
    
    try:
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(collection_name)
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Collection '{collection_name}': {type(e).__name__}: {e}")
        return None
    
    total_chunks = collection.count()
    if total_chunks == 0:
        return {
            "collection_name": collection_name,
            "total_chunks": 0,
            "chunks": [],
            "pagination": {"offset": 0, "limit": limit, "has_more": False}
        }
    
    try:
        # Include-Parameter basierend auf Anforderung
        include_params = ['metadatas', 'documents']
        if include_embeddings:
            include_params.append('embeddings')
        
        # Alle Daten abrufen und dann paginieren (ChromaDB hat keine native Pagination)
        results = collection.get(
            ids=None,
            where=None,
            include=include_params
        )
        
        ids = results.get('ids', [])
        metadatas = results.get('metadatas', [])
        documents = results.get('documents', [])
        embeddings = results.get('embeddings', []) if include_embeddings else []
        
        # Paginierung anwenden
        end_index = offset + limit if limit > 0 else len(ids)
        chunk_slice = slice(offset, end_index)
        
        chunks = []
        for i in range(offset, min(end_index, len(ids))):
            chunk_data = {
                'id': ids[i] if i < len(ids) else None,
                'metadata': metadatas[i] if i < len(metadatas) else {},
                'document': documents[i] if i < len(documents) else '',
                'chunk_size': len(documents[i]) if i < len(documents) and documents[i] else 0,
                'index': i
            }
            
            if include_embeddings and i < len(embeddings):
                chunk_data['embedding'] = embeddings[i]
                chunk_data['embedding_size'] = len(embeddings[i]) if embeddings[i] else 0
            
            chunks.append(chunk_data)
        
        has_more = end_index < len(ids) if limit > 0 else False
        
        return {
            "collection_name": collection_name,
            "total_chunks": total_chunks,
            "chunks": chunks,
            "pagination": {
                "offset": offset,
                "limit": limit,
                "returned_count": len(chunks),
                "has_more": has_more
            }
        }
        
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Chunks: {type(e).__name__}: {e}")
        return None

def display_collection_chunks(collection_name: str, db_path: str, limit: int = 5, 
                            show_full_text: bool = False, show_metadata: bool = True) -> None:
    """
    Zeigt einzelne Chunks einer Collection formatiert an.
    
    Args:
        collection_name: Name der Collection
        db_path: Pfad zur ChromaDB
        limit: Anzahl anzuzeigender Chunks
        show_full_text: Ob vollständiger Text angezeigt werden soll
        show_metadata: Ob Metadaten angezeigt werden sollen
    """
    chunk_data = get_collection_chunks(collection_name, db_path, limit=limit)
    if not chunk_data:
        return
    
    print(f"\n🧩 CHUNKS DER COLLECTION '{collection_name}'")
    print(f"{'='*60}")
    print(f"📊 Gesamtanzahl Chunks: {chunk_data['total_chunks']}")
    print(f"📋 Angezeigte Chunks: {chunk_data['pagination']['returned_count']}")
    if chunk_data['pagination']['has_more']:
        print(f"➡️ Weitere Chunks verfügbar")
    
    if not chunk_data['chunks']:
        print("⚠️ Keine Chunks gefunden.")
        return
    
    for i, chunk in enumerate(chunk_data['chunks'], 1):
        print(f"\n🗂️ Chunk {i} (Index: {chunk['index']})")
        print("-" * 40)
        
        # ID anzeigen
        if chunk['id']:
            print(f"🆔 ID: {chunk['id']}")
        
        # Dokument/Text anzeigen
        document = chunk.get('document', '')
        if document:
            if show_full_text:
                print(f"📄 Volltext ({chunk['chunk_size']} Zeichen):")
                print(f"   {document}")
            else:
                # Kurze Vorschau (erste 200 Zeichen)
                preview = document[:200] + "..." if len(document) > 200 else document
                print(f"📄 Vorschau ({chunk['chunk_size']} Zeichen):")
                print(f"   {preview}")
        else:
            print("📄 Kein Dokumententext vorhanden")
        
        # Metadaten anzeigen
        if show_metadata and chunk.get('metadata'):
            print(f"🏷️ Metadaten:")
            for key, value in chunk['metadata'].items():
                # Lange Werte kürzen
                if isinstance(value, str) and len(str(value)) > 100:
                    display_value = str(value)[:100] + "..."
                else:
                    display_value = value
                print(f"   • {key}: {display_value}")
        
        # Embedding-Info (falls vorhanden)
        if 'embedding_size' in chunk:
            print(f"🧠 Embedding-Dimensionen: {chunk['embedding_size']}")

def search_chunks_by_source(collection_name: str, db_path: str, source_filter: str) -> Optional[List[Dict]]:
    """
    Filtert Chunks nach einer bestimmten Quelle.
    
    Args:
        collection_name: Name der Collection
        db_path: Pfad zur ChromaDB
        source_filter: Quelldatei zum Filtern
    
    Returns:
        Liste der gefilterten Chunks oder None bei Fehler
    """
    chunk_data = get_collection_chunks(collection_name, db_path, limit=0)  # Alle Chunks
    if not chunk_data:
        return None
    
    filtered_chunks = []
    for chunk in chunk_data['chunks']:
        metadata = chunk.get('metadata', {})
        source = metadata.get('source', '')
        
        if source_filter.lower() in source.lower():
            filtered_chunks.append(chunk)
    
    return filtered_chunks

def get_chunk_by_id(collection_name: str, db_path: str, chunk_id: str) -> Optional[Dict]:
    """
    Ruft einen spezifischen Chunk anhand seiner ID ab.
    
    Args:
        collection_name: Name der Collection
        db_path: Pfad zur ChromaDB
        chunk_id: ID des gewünschten Chunks
    
    Returns:
        Chunk-Daten oder None bei Fehler/nicht gefunden
    """
    if not os.path.exists(db_path):
        print(f"❌ Fehler: Der ChromaDB-Pfad '{db_path}' existiert nicht.")
        return None
    
    try:
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(collection_name)
        
        results = collection.get(
            ids=[chunk_id],
            include=['metadatas', 'documents']
        )
        
        if not results['ids']:
            return None
        
        return {
            'id': results['ids'][0],
            'metadata': results['metadatas'][0] if results['metadatas'] else {},
            'document': results['documents'][0] if results['documents'] else '',
            'chunk_size': len(results['documents'][0]) if results['documents'] and results['documents'][0] else 0
        }
        
    except Exception as e:
        print(f"❌ Fehler beim Abrufen des Chunks: {type(e).__name__}: {e}")
        return None

def analyze_chunk_sizes(collection_name: str, db_path: str) -> Optional[Dict]:
    """
    Analysiert die Größenverteilung der Chunks in einer Collection.
    
    Args:
        collection_name: Name der Collection
        db_path: Pfad zur ChromaDB
    
    Returns:
        Dictionary mit Größenstatistiken
    """
    chunk_data = get_collection_chunks(collection_name, db_path, limit=0)
    if not chunk_data or not chunk_data['chunks']:
        return None
    
    sizes = [chunk['chunk_size'] for chunk in chunk_data['chunks']]
    
    if not sizes:
        return None
    
    sizes.sort()
    n = len(sizes)
    
    # Statistiken berechnen
    stats = {
        'total_chunks': n,
        'min_size': min(sizes),
        'max_size': max(sizes),
        'avg_size': sum(sizes) / n,
        'median_size': sizes[n // 2] if n % 2 == 1 else (sizes[n // 2 - 1] + sizes[n // 2]) / 2,
        'size_distribution': {
            'very_small': len([s for s in sizes if s < 100]),      # < 100 Zeichen
            'small': len([s for s in sizes if 100 <= s < 500]),     # 100-499 Zeichen
            'medium': len([s for s in sizes if 500 <= s < 1500]),   # 500-1499 Zeichen
            'large': len([s for s in sizes if 1500 <= s < 3000]),   # 1500-2999 Zeichen
            'very_large': len([s for s in sizes if s >= 3000])      # >= 3000 Zeichen
        }
    }
    
    return stats

def display_chunk_size_analysis(collection_name: str, db_path: str) -> None:
    """
    Zeigt eine Analyse der Chunk-Größen formatiert an.
    
    Args:
        collection_name: Name der Collection
        db_path: Pfad zur ChromaDB
    """
    stats = analyze_chunk_sizes(collection_name, db_path)
    if not stats:
        print(f"❌ Konnte Chunk-Größen für Collection '{collection_name}' nicht analysieren.")
        return
    
    print(f"\n📏 CHUNK-GRÖSSEN ANALYSE '{collection_name}'")
    print(f"{'='*50}")
    print(f"📊 Gesamtanzahl Chunks: {stats['total_chunks']}")
    print(f"📐 Minimale Größe: {stats['min_size']:,} Zeichen")
    print(f"📐 Maximale Größe: {stats['max_size']:,} Zeichen")
    print(f"📐 Durchschnittliche Größe: {stats['avg_size']:.1f} Zeichen")
    print(f"📐 Median-Größe: {stats['median_size']:.1f} Zeichen")
    
    print(f"\n📊 Größenverteilung:")
    dist = stats['size_distribution']
    total = stats['total_chunks']
    
    categories = [
        ('Sehr klein (< 100)', dist['very_small']),
        ('Klein (100-499)', dist['small']),
        ('Mittel (500-1499)', dist['medium']),
        ('Groß (1500-2999)', dist['large']),
        ('Sehr groß (≥ 3000)', dist['very_large'])
    ]
    
    for category, count in categories:
        percentage = (count / total) * 100 if total > 0 else 0
        bar = "█" * int(percentage / 5)  # Einfache Balkenanzeige
        print(f"   {category:<20}: {count:>4} ({percentage:>5.1f}%) {bar}")

def export_chunks_to_json(collection_name: str, db_path: str, output_file: str, 
                         limit: int = 0, include_embeddings: bool = False) -> bool:
    """
    Exportiert Chunks einer Collection in eine JSON-Datei.
    
    Args:
        collection_name: Name der Collection
        db_path: Pfad zur ChromaDB
        output_file: Name der Ausgabedatei
        limit: Maximale Anzahl Chunks (0 = alle)
        include_embeddings: Ob Embeddings exportiert werden sollen
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    chunk_data = get_collection_chunks(collection_name, db_path, limit=limit, 
                                     include_embeddings=include_embeddings)
    if not chunk_data:
        return False
    
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "collection_name": collection_name,
        "database_path": db_path,
        "export_settings": {
            "limit": limit,
            "include_embeddings": include_embeddings
        },
        "summary": {
            "total_chunks_in_collection": chunk_data['total_chunks'],
            "exported_chunks": len(chunk_data['chunks'])
        },
        "chunks": chunk_data['chunks']
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        print(f"✅ {len(chunk_data['chunks'])} Chunks erfolgreich exportiert nach: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Exportieren: {type(e).__name__}: {e}")
        return False
    """
    Exportiert die Datenbankstatistiken in eine JSON-Datei.
    
    Args:
        db_path: Pfad zur ChromaDB
        output_file: Name der Ausgabedatei
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    db_stats = get_database_statistics(db_path)
    if not db_stats:
        return False
    
    # Konvertiere zu JSON-serialisierbarem Format
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "database_path": db_path,
        "summary": {
            "total_collections": db_stats.collection_count,
            "total_documents": db_stats.total_documents,
            "total_chunks": db_stats.total_chunks,
            "avg_chunks_per_document": db_stats.get_avg_chunks_per_document()
        },
        "collections": [stats.to_dict() for stats in db_stats.collections]
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Statistiken erfolgreich exportiert nach: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Exportieren: {type(e).__name__}: {e}")
        return False

def print_collection_summary(collection_name: str, db_path: str) -> None:
    """
    Gibt eine formatierte Zusammenfassung einer Collection aus.
    
    Args:
        collection_name: Name der Collection
        db_path: Pfad zur ChromaDB
    """
    stats = analyze_collection(collection_name, db_path)
    if not stats:
        print(f"❌ Konnte Collection '{collection_name}' nicht analysieren.")
        return
    
    print(f"\n📊 Collection: '{stats.name}'")
    print(f"{'='*50}")
    print(f"📄 Dokumente (Dateien): {stats.document_count}")
    print(f"🧩 Chunks: {stats.chunk_count}")
    
    if stats.chunk_count > 0:
        print(f"📊 Chunks pro Dokument: {stats.get_chunks_per_document():.1f}")
        print(f"📏 Ø Chunk-Größe: {stats.avg_chunk_size:.0f} Zeichen")
        
        if stats.source_stats:
            print(f"\n📁 Quelldateien ({len(stats.source_stats)}):")
            sorted_sources = sorted(stats.source_stats.items(), key=lambda x: x[1], reverse=True)
            for source, count in sorted_sources[:5]:  # Top 5 anzeigen
                percentage = (count / stats.chunk_count) * 100
                print(f"   • {source}: {count} Chunks ({percentage:.1f}%)")
            
            if len(sorted_sources) > 5:
                print(f"   ... und {len(sorted_sources) - 5} weitere")
        
        if stats.metadata_keys:
            print(f"\n🏷️ Metadaten-Felder: {', '.join(stats.metadata_keys)}")
    else:
        print("⚠️ Collection ist leer")

def display_chromadb_statistics(db_path: str, detailed: bool = True) -> None:
    """
    Zeigt umfassende Statistiken der ChromaDB-Collections an.
    
    Args:
        db_path: Pfad zur ChromaDB
        detailed: Ob detaillierte Statistiken angezeigt werden sollen
    """
    print(f"🔍 Verbinde zu ChromaDB unter: {db_path}...")
    
    db_stats = get_database_statistics(db_path)
    if not db_stats:
        return
    
    print("✅ Verbindung zur ChromaDB erfolgreich.")
    
    if not db_stats.collections:
        print("\nℹ️ Keine Collections in dieser ChromaDB gefunden.")
        return
    
    # Übersicht
    print(f"\n{'='*60}")
    print(f"📊 CHROMADB STATISTIKEN")
    print(f"{'='*60}")
    print(f"📁 Anzahl Collections: {db_stats.collection_count}")
    print(f"📄 Gesamtanzahl Dokumente (Dateien): {db_stats.total_documents}")
    print(f"🧩 Gesamtanzahl Chunks: {db_stats.total_chunks}")
    if db_stats.total_documents > 0:
        print(f"📊 Durchschnittliche Chunks pro Dokument: {db_stats.get_avg_chunks_per_document():.1f}")
    print(f"📅 Analysiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Details pro Collection
    print(f"\n{'='*60}")
    print(f"📋 COLLECTION DETAILS")
    print(f"{'='*60}")
    
    for i, stats in enumerate(db_stats.collections, 1):
        print(f"\n🗂️ Collection {i}: '{stats.name}'")
        print(f"   📄 Anzahl Dokumente (Dateien): {stats.document_count}")
        print(f"   🧩 Anzahl Chunks: {stats.chunk_count}")
        
        if stats.chunk_count == 0:
            print("   ⚠️ Collection ist leer")
            continue
        
        if stats.document_count > 0:
            print(f"   📊 Durchschnittliche Chunks pro Dokument: {stats.get_chunks_per_document():.1f}")
        
        if detailed:
            print(f"   📏 Durchschnittliche Chunk-Größe: {stats.avg_chunk_size:.1f} Zeichen")
            
            if stats.metadata_keys:
                print(f"   🏷️ Verfügbare Metadaten-Felder: {', '.join(stats.metadata_keys)}")
            
            if stats.source_stats:
                print("   📁 Chunks pro Quelldatei:")
                for source, count in sorted(stats.source_stats.items()):
                    percentage = (count / stats.chunk_count) * 100
                    print(f"      • '{source}': {count} Chunks ({percentage:.1f}%)")
            else:
                print("   ⚠️ Keine Quellinformationen gefunden")
        
        print("-" * 50)

# --- Ausführung ---
if __name__ == "__main__":
    # Standard DB-Pfad - hier anpassen!
    DEFAULT_DB_PATH = "./multimodal_chromadb"
    
    # Benutzer nach DB-Pfad fragen oder Standard verwenden
    db_path = input(f"ChromaDB-Pfad [{DEFAULT_DB_PATH}]: ").strip()
    if not db_path:
        db_path = DEFAULT_DB_PATH
    
    # Verfügbare Optionen anzeigen
    print("\n" + "="*60)
    print("📊 CHROMADB STATISTICS - HAUPTMENÜ")
    print("="*60)
    print("1. Schnelle Übersicht")
    print("2. Detaillierte Datenbankanalyse")
    print("3. Spezifische Collection analysieren")
    print("4. Collection-Chunks anzeigen")
    print("5. Chunk-Größenanalyse")
    print("6. Chunks nach Quelle filtern")
    print("7. Spezifischen Chunk anzeigen (nach ID)")
    print("8. Collections vergleichen")
    print("9. Export: Statistiken als JSON")
    print("10. Export: Chunks als JSON")
    
    choice = input("Wählen Sie eine Option (1-10) [2]: ").strip()
    
    if choice == "1":
        # Schnelle Übersicht
        quick = get_quick_stats(db_path)
        if "error" in quick:
            print(f"❌ {quick['error']}")
        else:
            print(f"\n📊 Schnelle Übersicht:")
            print(f"Collections: {quick['collection_count']}")
            print(f"Gesamtchunks: {quick['total_chunks']}")
            print(f"Collection-Namen: {', '.join(quick['collection_names'])}")
    
    elif choice == "3":
        # Spezifische Collection
        collections = list_collections(db_path)
        if collections:
            print(f"\n📋 Verfügbare Collections: {', '.join(collections)}")
            col_name = input("Collection-Name eingeben: ").strip()
            if col_name in collections:
                print_collection_summary(col_name, db_path)
            else:
                print(f"❌ Collection '{col_name}' nicht gefunden.")
        else:
            print("❌ Keine Collections gefunden.")
    
    elif choice == "4":
        # Collection-Chunks anzeigen
        collections = list_collections(db_path)
        if collections:
            print(f"\n📋 Verfügbare Collections: {', '.join(collections)}")
            col_name = input("Collection-Name eingeben: ").strip()
            if col_name in collections:
                limit = input("Anzahl Chunks anzeigen [5]: ").strip()
                limit = int(limit) if limit.isdigit() else 5
                
                show_full = input("Vollständigen Text anzeigen? (j/n) [n]: ").strip().lower()
                show_full_text = show_full in ['j', 'ja', 'y', 'yes']
                
                display_collection_chunks(col_name, db_path, limit=limit, 
                                        show_full_text=show_full_text)
            else:
                print(f"❌ Collection '{col_name}' nicht gefunden.")
        else:
            print("❌ Keine Collections gefunden.")
    
    elif choice == "5":
        # Chunk-Größenanalyse
        collections = list_collections(db_path)
        if collections:
            print(f"\n📋 Verfügbare Collections: {', '.join(collections)}")
            col_name = input("Collection-Name eingeben: ").strip()
            if col_name in collections:
                display_chunk_size_analysis(col_name, db_path)
            else:
                print(f"❌ Collection '{col_name}' nicht gefunden.")
        else:
            print("❌ Keine Collections gefunden.")
    
    elif choice == "6":
        # Chunks nach Quelle filtern
        collections = list_collections(db_path)
        if collections:
            print(f"\n📋 Verfügbare Collections: {', '.join(collections)}")
            col_name = input("Collection-Name eingeben: ").strip()
            if col_name in collections:
                source_filter = input("Quelldatei-Filter eingeben: ").strip()
                filtered_chunks = search_chunks_by_source(col_name, db_path, source_filter)
                
                if filtered_chunks:
                    print(f"\n🔍 Gefilterte Chunks ({len(filtered_chunks)} gefunden):")
                    print("="*50)
                    
                    for i, chunk in enumerate(filtered_chunks[:10], 1):  # Max 10 anzeigen
                        source = chunk.get('metadata', {}).get('source', 'Unbekannt')
                        preview = chunk.get('document', '')[:100] + "..." if len(chunk.get('document', '')) > 100 else chunk.get('document', '')
                        print(f"\n{i}. ID: {chunk.get('id', 'N/A')}")
                        print(f"   📁 Quelle: {source}")
                        print(f"   📄 Vorschau: {preview}")
                    
                    if len(filtered_chunks) > 10:
                        print(f"\n... und {len(filtered_chunks) - 10} weitere Chunks")
                else:
                    print(f"❌ Keine Chunks mit Quelle '{source_filter}' gefunden.")
            else:
                print(f"❌ Collection '{col_name}' nicht gefunden.")
        else:
            print("❌ Keine Collections gefunden.")
    
    elif choice == "7":
        # Spezifischen Chunk anzeigen
        collections = list_collections(db_path)
        if collections:
            print(f"\n📋 Verfügbare Collections: {', '.join(collections)}")
            col_name = input("Collection-Name eingeben: ").strip()
            if col_name in collections:
                chunk_id = input("Chunk-ID eingeben: ").strip()
                chunk = get_chunk_by_id(col_name, db_path, chunk_id)
                
                if chunk:
                    print(f"\n🗂️ CHUNK DETAILS")
                    print("="*40)
                    print(f"🆔 ID: {chunk['id']}")
                    print(f"📏 Größe: {chunk['chunk_size']} Zeichen")
                    print(f"📄 Dokument:")
                    print(f"   {chunk['document']}")
                    
                    if chunk['metadata']:
                        print(f"🏷️ Metadaten:")
                        for key, value in chunk['metadata'].items():
                            print(f"   • {key}: {value}")
                else:
                    print(f"❌ Chunk mit ID '{chunk_id}' nicht gefunden.")
            else:
                print(f"❌ Collection '{col_name}' nicht gefunden.")
        else:
            print("❌ Keine Collections gefunden.")
    
    elif choice == "8":
        # Collections vergleichen
        collections = list_collections(db_path)
        if len(collections) >= 2:
            print(f"\n📋 Verfügbare Collections: {', '.join(collections)}")
            col_names = input("Collection-Namen eingeben (durch Komma getrennt): ").strip()
            col_list = [name.strip() for name in col_names.split(',') if name.strip()]
            
            if len(col_list) >= 2:
                comparison = compare_collections(db_path, col_list)
                if comparison:
                    print(f"\n🔍 COLLECTION-VERGLEICH")
                    print("="*50)
                    print(f"📊 Analysierte Collections: {comparison['summary']['analyzed_collections']}")
                    print(f"📄 Gesamtdokumente: {comparison['summary']['total_documents']}")
                    print(f"🧩 Gesamtchunks: {comparison['summary']['total_chunks']}")
                    print(f"📊 Ø Chunks pro Collection: {comparison['summary']['avg_chunks_per_collection']:.1f}")
                    
                    print(f"\n📋 Details:")
                    for col_data in comparison['collections']:
                        print(f"  • {col_data['name']}: {col_data['document_count']} Docs, {col_data['chunk_count']} Chunks")
                else:
                    print("❌ Vergleich fehlgeschlagen.")
            else:
                print("❌ Mindestens 2 Collection-Namen erforderlich.")
        else:
            print("❌ Mindestens 2 Collections für Vergleich erforderlich.")
    
    elif choice == "9":
        # Export Statistiken
        output_file = input("JSON-Dateiname [chromadb_stats.json]: ").strip()
        if not output_file:
            output_file = "chromadb_stats.json"
        
        success = export_statistics_to_json(db_path, output_file)
        if success:
            print("✅ Statistiken erfolgreich exportiert.")
    
    elif choice == "10":
        # Export Chunks
        collections = list_collections(db_path)
        if collections:
            print(f"\n📋 Verfügbare Collections: {', '.join(collections)}")
            col_name = input("Collection-Name eingeben: ").strip()
            if col_name in collections:
                output_file = input(f"JSON-Dateiname [{col_name}_chunks.json]: ").strip()
                if not output_file:
                    output_file = f"{col_name}_chunks.json"
                
                limit = input("Anzahl Chunks exportieren (0 = alle) [0]: ").strip()
                limit = int(limit) if limit.isdigit() else 0
                
                include_emb = input("Embeddings einschließen? (j/n) [n]: ").strip().lower()
                include_embeddings = include_emb in ['j', 'ja', 'y', 'yes']
                
                success = export_chunks_to_json(col_name, db_path, output_file, 
                                               limit=limit, include_embeddings=include_embeddings)
                if success:
                    print("✅ Chunks erfolgreich exportiert.")
            else:
                print(f"❌ Collection '{col_name}' nicht gefunden.")
        else:
            print("❌ Keine Collections gefunden.")
    
    else:
        # Standardausführung mit detaillierten Statistiken
        display_chromadb_statistics(db_path)
        
        # Optional: Export in JSON-Datei
        print(f"\n{'='*60}")
        export_choice = input("Möchten Sie die Statistiken als JSON exportieren? (j/n): ").lower()
        if export_choice in ['j', 'ja', 'y', 'yes']:
            export_statistics_to_json(db_path)