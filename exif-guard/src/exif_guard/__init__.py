"""exif-guard: auditoria local de metadados EXIF para fotos próprias."""

from exif_guard.exif import PhotoMetadata, dms_to_decimal, map_link, read_exif

__version__ = "0.1.0"
__all__ = ["PhotoMetadata", "dms_to_decimal", "map_link", "read_exif", "__version__"]
