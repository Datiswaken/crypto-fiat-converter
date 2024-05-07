def is_output_filename_valid(filename: str) -> bool:
    return filename.endswith(".csv") and len(filename.split(".")) == 2
