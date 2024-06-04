import logging

def setup_logger(name: str):
    logging.basicConfig(
        format="[%(asctime)s] %(name)s: %(levelname)s: %(message)s",
        level=logging.INFO
    )
    
    return logging.getLogger(name)