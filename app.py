from src import create_app
from src.config import Config

app = create_app(Config)

if __name__ == '__main__':
    app.debug = True
    app.run()
