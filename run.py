from app import app
try:
    app.run(host = '0.0.0.0', debug = True)
finally:  
    open('flag.txt', 'w').writeline(True).close()