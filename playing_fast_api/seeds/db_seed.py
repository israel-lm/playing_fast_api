from pymongo import MongoClient
import json

from playing_fast_api.logger_setup import setup_logger
from playing_fast_api.defs import DB_URL, DB_NAME, COLLECTION_NAME, DATA_FILE_NAME

logger = setup_logger(__name__)

class DBSeed:
    """ Seed MongoDB with courses data."""
    
    def __init__(self):
        self.mongo_client = MongoClient(DB_URL)
        if self.mongo_client is not None:
            self.db_id = self.mongo_client[DB_NAME]
            self.collection = self.db_id[COLLECTION_NAME]
        else:
            self.db_id = None
            self.collection = None
            logger.error("Connection to MongoDB failed.")

    def populate_db(self) -> bool:
        """
        Populate the DB with initial data.

        Returns:
            bool: True if operation succeeds, False otherwise
        """
        
        with open(DATA_FILE_NAME, "r") as file:
            courses = json.load(file)

        if self.collection is not None:
            self.collection.create_index("name")

            for course in courses:
                course["rating"] = {"total": 0, "count": 0}
                for chapter in course.get("chapters"):
                    chapter["rating"] = {"total": 0, "count": 0}
                
                self.collection.insert_one(course)

            self.mongo_client.close()
            return True
        else:
            logger.error("Collection not defined.")
            return False
        

if __name__ == "__main__":
    logger.info("Start seeding DB.")
    seed = DBSeed()
    if seed.populate_db():
        logger.info("Seeding successful.")
    else:
        logger.error("Seeding failed.")