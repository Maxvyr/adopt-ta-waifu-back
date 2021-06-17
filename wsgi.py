from app import app

if __name__ == '__main__':
    app.debug = False
    app.run("127.0.0.1", 8080, debug=False)
