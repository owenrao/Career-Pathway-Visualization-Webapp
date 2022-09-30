from flask import Flask, render_template, request, redirect
from plot import plot_validation,get_occ_title,plot_annual_income_map,plot_employment_per_1000_map,get_occ_info,plot_annual_income_change_line,plot_tot_emp_change_bar,plot_income_distribution_bar

#App Config
app = Flask(__name__)
app.secret_key = b'551'
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"

#db.init_app(app)

'''
#Admin Config
admin = Admin(app, name='Dashboard')
admin.add_view(MyModelView(Skill, db.session))
admin.add_view(MyModelView(SkillType, db.session))
admin.add_view(MyModelView(Course, db.session))
with app.app_context(): db.create_all()
'''

@app.route('/', methods = ['GET'])
def index():
    return render_template("index.html")

@app.route('/details/<string:title>', methods = ['GET','POST'])
def details(title):
    occ_data = get_occ_title(title)
    dscrpt = "Administer nursing care to ill or injured persons. Licensing or registration required. Include administrative, public health, industrial, private duty, and surgical nurses."*3
    payload = {
        "name": title,
        "dscrpt": dscrpt,
        "graphs": {
            "employment_per_1000_map": plot_validation(plot_employment_per_1000_map,occ_data),
            "tot_emp_change_bar": plot_validation(plot_tot_emp_change_bar,occ_data),
            "annual_income_map": plot_validation(plot_annual_income_map,occ_data),
            "income_distribution_bar": plot_validation(plot_income_distribution_bar,occ_data),
            "annual_income_change_line": plot_validation(plot_annual_income_change_line,occ_data)
        },
        "data": get_occ_info(occ_data)
    }
    return render_template("details.html", payload = payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port="5050",debug=True)