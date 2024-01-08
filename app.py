from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

player_path = 'data/player_stats_23.csv'
player_df = pd.read_csv(player_path, encoding='ISO-8859-1', delimiter=';')
fifa_path = 'data/fifa23_stats.csv'
fifa_df = pd.read_csv(fifa_path)

@app.route('/')
def index():
    # Display basic statistics on the homepage
    player_stats = player_df.describe().to_html()
    fifa_stats = fifa_df.describe().to_html()
    return render_template('index.html', df1=player_stats, df2=fifa_stats)  

if __name__ == '__main__':
    app.run(debug=True)
