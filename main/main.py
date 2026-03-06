from models.dorm import Dorm
from fastmcp import FastMCP

dorm = Dorm("Ducka")

app = FastMCP()

@app.post("/request-maintenance")
async def request_maintenance(resident_id, room_id, issue_category):
    res = dorm.request_maintenance(resident_id, room_id, issue_category)
    return res


if __name__ == "__main__":
    print("test")
    print("Hello World")
    print("Tonson")

    ducka = Dorm("ducka")
    print(ducka)