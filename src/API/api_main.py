from src.API.app import app
from src.API.handlers import *

def main():
    app.run(host="0.0.0.0", port=8000, debug=True)

if __name__ == "__main__":
    main()