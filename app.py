from fastapi import FastAPI, Response

app = FastAPI()


# testing
app.get("/")
def health_check():
    return {"message": "success"}


