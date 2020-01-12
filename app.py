import stripe, datetime
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
        bank_usage = False
        first_name = request.form['first_name']
        last_name=request.form['last_name']
        email = request.form['email']
        country=request.form['country']
        full_phone=request.form['full_phone']
        phone=request.form['phone']
        describe=request.form['describe']
        cc_number=request.form['cc_number']
        cc_cvv=request.form['cc_cvv']
        cc_expire=request.form['cc_expire']
        routing_number=request.form['routing_number']
        acc_number=request.form['acc_number']
        acc_number_confirm=request.form['acc_number_confirm']
        cc_number = cc_number.replace(" ","")
        cc_expire = cc_expire.replace(" ","")
        cc_expire_split = cc_expire.split("/")
        cc_expire_join = cc_expire.replace("/","")
        if not phone.isdigit():
            return render_template('main.html', phone_number_digit=True)
        if len(cc_number) > 0 or len(cc_expire_split[0]) > 0 or len(cc_cvv) == 4: 
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
            if not cc_cvv.isdigit():
                return render_template('main.html', cc_cvv_digit=True)
            if not (len(cc_cvv) == 3 or len(cc_cvv) == 4):
                return render_template('main.html', cc_cvv_length=True)
            today = datetime.datetime.now().timetuple()
            time = datetime.datetime(today[0],today[1],today[2],today[3],today[4]).timestamp()
            account = stripe.Account.create(type="custom",country=country,tos_acceptance={"date":int(time), "ip":"127.0.0.1"},product_description=describe,email=email,legal_entity={"first_name":first_name,"last_name":last_name, "personal_email":email, "personal_phone_number":full_phone, "phone_number":full_phone},requested_capabilities=["card_payments", "transfers",],)
            try:
                token = stripe.Token.create(card={"number": cc_number,"exp_month": cc_expire_split[0],"exp_year": cc_expire_split[1],"currency":"usd", "cvc":cc_cvv},)            
                credit_card = stripe.Account.create_external_account(account["id"],external_account=token["id"])
            except:
                return render_template('main.html', not_debit_card=True)
            account_links = stripe.AccountLink.create(account=account["id"],failure_url='https://afriex-stripe.herokuapp.com/failure',success_url='https://afriex-stripe.herokuapp.com/success',type='custom_account_verification',collect='currently_due',)
            # print([first_name, last_name, email, country, phone, full_phone, describe, cc_number, cc_expire, cc_cvv, routing_number, acc_number, acc_number_confirm]) 
            return redirect(account_links["url"])

        bank_usage = True
        if not routing_number.isdigit():
            return render_template('main.html', routing_number_digit=True, bank_usage=bank_usage)
        if len(routing_number) != 9:
            return render_template('main.html', routing_number_length=True, bank_usage=bank_usage)
        if acc_number != acc_number_confirm:
            return render_template('main.html', acc_number_unmatch=True, bank_usage=bank_usage)
        if not acc_number.isdigit():
            return render_template('main.html', acc_number_digit=True, bank_usage=bank_usage)
        if len(acc_number) != 12:
            return render_template('main.html', acc_number_length=True, bank_usage=bank_usage)
        today = datetime.datetime.now().timetuple()
        time = datetime.datetime(today[0],today[1],today[2],today[3],today[4]).timestamp()
        account = stripe.Account.create(type="custom",country=country,tos_acceptance={"date":int(time), "ip":"127.0.0.1"},product_description=describe,email=email,legal_entity={"first_name":first_name,"last_name":last_name, "personal_email":email, "personal_phone_number":full_phone, "phone_number":full_phone},requested_capabilities=["card_payments", "transfers",],)
        try:
            token = stripe.Token.create(bank_account={"country": country,"currency": "usd","routing_number": routing_number,"account_number": acc_number,},)        
            bank = stripe.Account.create_external_account(account["id"],external_account=token["id"])
        except:
            return render_template('main.html', not_bank_account=True, bank_usage=bank_usage)
        account_links = stripe.AccountLink.create(account=account["id"],failure_url='https://afriex-stripe.herokuapp.com/failure',success_url='https://afriex-stripe.herokuapp.com/success',type='custom_account_verification',collect='currently_due',)
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