from website import create_app

app = create_app() #Create app instance

if __name__ == "__main__":
    app.run(debug=True)