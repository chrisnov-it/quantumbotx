import os
from core import create_app

# Set environment to skip MT5 initialization on Vercel
os.environ['SKIP_MT5_INIT'] = '1'

app = create_app()

if __name__ == '__main__':
    app.run()
