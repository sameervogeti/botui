import os

# from app import app
from app import app

port = int(os.getenv('PORT', 4000))

print("Starting app on port %d" % port)

app.run(debug=False, port=port, host='0.0.0.0')