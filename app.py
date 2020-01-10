import stripe
from flask import Flask, jsonify, render_template, request, redirect


app = Flask(__name__)

stripe_keys = {
  'secret_key': 'sk_test_pxUuaANGXrRy7EIBgW2AzPFH',
  'publishable_key': 'pk_test_hWMwML4SxDuvVDqsg94BzyZc'
}

stripe.api_key = stripe_keys['secret_key']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name=request.form['last_name']
        email = request.form['email']
        country=request.form['country']
        full_phone=request.form['full_phone']
        phone=request.form['phone']
        describe=request.form['describe']
        cc_number=request.form['cc_number']
        cc_expire=request.form['cc_expire']
        cc_number = cc_number.replace(" ","")
        cc_expire = cc_expire.replace(" ","")
        cc_expire_split = cc_expire.split("/")
        cc_expire_join = cc_expire.replace("/","") 
        if not phone.isdigit():
            return render_template('main.html', phone_number_digit=True)
        if "/" not in cc_expire:
            return render_template('main.html', demarcate_not_present=True)
        if len(cc_expire_split[0]) != 2 or len(cc_expire_split[1]) != 2:
            return render_template('main.html', expire_wrong_format=True)
        if not cc_number.isdigit():
            return render_template('main.html', cc_number_digit=True)
        if len(cc_number) != 16:
            return render_template('main.html', cc_number_length=True)
        if not cc_expire_join.isdigit():
            return render_template('main.html', cc_expire_digit=True)
        account = stripe.Account.create(type="custom",country=country,email=email,requested_capabilities=["card_payments", "transfers",],)
        account_links = stripe.AccountLink.create(account=account["id"],failure_url='http://127.0.0.1:5000/failure',success_url='http://127.0.0.1:5000/success',type='custom_account_verification',collect='currently_due',)                             
        print([first_name, last_name, email, country, phone, full_phone, describe, cc_number, cc_expire]) 
        return redirect(account_links["url"])        
    return render_template('main.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/failure')
def failure():
    return render_template('failure.html')

if __name__ == '__main__':
    app.run(debug=True)