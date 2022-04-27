from flask import Flask, render_template, request
from prep import predict_score

app = Flask(__name__, template_folder='./templates', static_folder='./templates/static')


@app.route("/", methods=['GET', 'POST'])
def index():
    data = False
    if request.method == "POST":
        form_data = [i for i in request.form.values()]
        score1 = predict_score([form_data])
        score2 = predict_score([[form_data[1], form_data[0], form_data[2]]])
        data = [form_data, round(score1[0][0]), round(score2[0][0])]
    return render_template("layouts/index.html", data=data)


if __name__ == '__main__':
    app.run(port=8080, debug=False)
