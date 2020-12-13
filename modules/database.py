import pymongo
from pymongo import MongoClient
import tabulate
import datetime

cluster = MongoClient(
    "mongodb+srv://NYPCLASSBOT:fatpeepee123@nyp-class-bot.boaao.mongodb.net/class-links?retryWrites=true&w=majority"
)
db = cluster["class_links"]


class Db:
    cluster = db

    def __init__(self, guildId):
        self.guildId = guildId
        # self.collection = db[str(guildId)]
        self.collection = db[guildId]
        # Remove this^^ after creation of cluster from timetable is created

    def delSelf(self):
        db.self.collection.remove(self.guildId)

    def insertEntry(self, subj, day, time):
        post = {"day": day, "time": time, "subject": subj}
        self.collection.insert_one(post)
        print("Entry is inserted.")
        return "Entry is inserted."

    def insertManyEntry(self, arrayOfPosts):
        self.collection.insert_many(arrayOfPosts)
        print("Entries have been inserted.")

    # inserting multiple entry
    # post2 = {"_id": "subject", "time": 1200, "day:": "link"}
    # collection.insert_many([post, post2])

    def updateEntry(self, subj, day, time, newField, newValue):
        self.collection.update_one(
            {"day": day, "time": time, "subject": subj},
            {"$set": {newField: newValue}},
        )
        print("Entry has been updated.")
        return "Entry has been updated "

    def findEntry(self, day, subj, time):
        x = self.collection.find({"day": day, "subject": subj, "time": time})
        for i in x:
            print(i)

    def deleteSingleEntry(self, subj, day, time):
        # show all entries for discord server
        # from the entry data, enter criterias for it to be deleted.
        self.collection.delete_one(
            {
                "day": day,
                "time": time,
                "subject": subj,
            }
        )
        print("Entry has been deleted.")
        return "Entry has been deleted."

    def getAllEntry(self):
        entries = []
        x = self.collection.find()
        for i in x:
            entries.append(i)
        return entries


if __name__ == "__main__":
    # 769097949514563594
    guildDb = Db("769097949514563594_cip")
    # print(list(db.list_collection_names()))
    print(guildDb.getAllEntry())
    secondsFromNow = (datetime.timedelta(0, 20) + datetime.datetime.now()).strftime("%H%M")
    print(secondsFromNow)
    # guildDb.insertEntry("LECO6\nBSTAT\nELEARNING\n\nFT\nOHMOIY", 6, secondsFromNow)
    # 2001
    # guildDb.deleteSingleEntry("LECO6\nBSTAT\nELEARNING\n\nFT\nOHMOIY", 6, "2001")
